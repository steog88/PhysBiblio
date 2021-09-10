"""Module that deals with importing info from the INSPIRE-HEP API.

This file is part of the physbiblio package.
"""
import json
import re
import time
import traceback

import bibtexparser

try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import InspireStrings
    from physbiblio.webimport.arxiv import getYear
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class WebSearch(WebInterf, InspireStrings):
    """Subclass of WebInterf that can connect
    to INSPIRE-HEP to perform searches
    """

    name = "inspire"
    description = "INSPIRE fetcher"
    url = pbConfig.inspireLiteratureAPI
    urlRecord = pbConfig.inspireLiteratureLink
    correspondences = [
        ["id", "inspire"],
        ["year", "year"],
        # ["arxiv", "arxiv"],
        # ["oldkeys", "old_keys"],
        ["firstdate", "firstdate"],
        ["pubdate", "pubdate"],
        ["doi", "doi"],
        ["ads", "ads"],
        ["isbn", "isbn"],
        ["bibtex", "bibtex"],
        ["link", "link"],
        ["cit", "citations"],
        ["cit_no_self", "citations_no_self"],
    ]
    bibtexFields = [
        "author",
        "title",
        "journal",
        "volume",
        "year",
        "pages",
        # "arxiv",
        "primaryclass",
        "archiveprefix",
        "eprint",
        "doi",
        "isbn",
        "school",
        "reportnumber",
        "booktitle",
        "collaboration",
    ]
    updateBibtexFields = [
        "author",
        "title",
        "doi",
        "volume",
        "pages",
        "year",
        "journal",
        "eprint",
        "archiveprefix",
        "primaryclass",
        "collaboration",
        "reportnumber",
        "booktitle",
        "publisher",
        "arxiv",
    ]
    metadataLiteratureFields = [
        "arxiv_eprints",
        "author_count",
        "authors.full_name",
        "citation_count",
        "citation_count_without_self_citations",
        "collaborations",
        "control_number",
        "document_type",
        "dois",
        "earliest_date",
        "external_system_identifiers",
        "first_author.full_name",
        "imprints",
        "isbns",
        "legacy_creation_date",
        "preprint_date",
        "primary_arxiv_category",
        "publication_info",
        "report_numbers",
        "texkeys",
        "thesis_info",
        "titles",
    ]
    metadataCitationFields = [
        "citation_count",
        "citation_count_without_self_citations",
        "control_number",
    ]
    metadataConferenceFields = [
        "cnum",
        "proceedings",
        "titles",
    ]
    defaultSize = 250

    def __init__(self):
        """Initializes the class variables
        using the WebInterf constructor.

        Define additional specific parameters for the INSPIRE-HEP API.
        """
        WebInterf.__init__(self)
        self.urlArgs = {
            "sort": "mostrecent",
            "size": "%s" % self.defaultSize,
            "page": "1",
        }

    def _fixAccents(self, text):
        """Enclose particular accent strings such as '\"a' in curly braces
        to avoid parsing errors in bibtexparser

        Parameter:
            text: the input bibtex

        Output:
            the fixed bibtex
        """
        match = re.compile('((\\\\")[a-zA-Z]{1})', re.MULTILINE)
        for t in match.finditer(text):
            text = text.replace(t.group(), "{%s}" % t.group())
        return text

    def retrieveBibtex(self, string, size=250):
        """Retrieves a list of bibtexs

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        args = self.urlArgs.copy()
        args["q"] = string.replace(" ", "%20")
        args["size"] = str(size)
        args["format"] = "bibtex"
        url = self.createUrl(args)
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url)
        text = self._fixAccents(text)
        try:
            return parse_accents_str(text)
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveUrlFirst(self, string):
        """Retrieves the first result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        return self.retrieveBibtex(string, size=1)

    def retrieveUrlAll(self, string):
        """Retrieves all the result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        return self.retrieveBibtex(string, size=self.defaultSize)

    def retrieveAPIResults(self, url, max_iterations=20):
        """Obtain results from the INSPIRE API, merging several calls
        if more than one page is available

        Parameter:
            url: the initial url to fetch.
                Subsequent ones, if present, will be fetched by the json
            max_iterations (default 20): maximum number of times
                that links.next is employed before stopping

        Output:
            a list of hits and the total number of hits
                as returned by the first GET
        """
        hits = []
        tot = 0
        iteration = 0
        while url != "" and url is not None and iteration < max_iterations:
            pBLogger.info(self.searchResultsFrom % (url))
            text = self.textFromUrl(url)
            if text is None or text == "":
                pBLogger.warning(self.errorEmptyText)
                return hits, tot
            try:
                results = json.loads(text)
            except json.decoder.JSONDecodeError:
                pBLogger.exception(self.jsonError)
                return hits, tot
            if "message" in results.keys():
                pBLogger.exception(
                    self.apiResponseError % (results["status"], results["message"])
                )
                return hits, tot
            elif "id" in results.keys():
                return [results], 1
            elif "hits" in results.keys():
                try:
                    hits += results["hits"]["hits"]
                    if tot == 0:
                        tot = results["hits"]["total"]
                except (IndexError, KeyError):
                    pBLogger.exception(self.genericError)
                    return hits, tot
                try:
                    url = results["links"]["next"]
                    iteration += 1
                except KeyError:
                    url = ""
        return hits, tot

    def retrieveSearchResults(
        self, searchstring, size=500, fields=None, addfields=[], max_iterations=20
    ):
        """Extract a list of hits from an Inspire search
        (through the q parameter)

        Parameters:
            searchstring: the string used to query the Inspire API
            size (default 500): how many hits per page (max 1000)
            fields (default None): if not None, replace the default selection
                of metadata fields required in the output
            addfields (default []): list of requested metadata fields
                apart from the default ones
                (useful especially when fields=None)
            max_iterations (default 20): maximum number of times
                that links.next is employed before stopping

        Output:
            from self.retrieveAPIResults
        """
        if fields is None:
            fields = self.metadataLiteratureFields
        if len(addfields) > 0:
            fields += addfields
        args = self.urlArgs.copy()
        args["q"] = searchstring.replace(" ", "%20")
        args["size"] = "%d" % (size if size <= 1000 else 1000)
        args["fields"] = ",".join(fields)
        try:
            del args["page"]
        except KeyError:
            pass
        return self.retrieveAPIResults(
            self.createUrl(args), max_iterations=max_iterations
        )

    def retrieveBatchQuery(self, entries, searchFormat="%s", **kwargs):
        """Read a list of entries and create a general search string
        for a "manual" batch query to the INSPIRE database
        through the new API.

        Parameters:
            entries: a list search strings for the entries of interest
            searchFormat (default "%s"): formatter for the search string
                of each entry. Example: use "recid:%s" to match IDs
            kwargs: passed to self.retrieveSearchResults

        Output:
            the output of self.retrieveSearchResults
        """
        entries = [e for e in entries if e != "" and e is not None]
        try:
            if searchFormat == "%s":
                entries = [
                    "texkeys:%s" % e if e.lower().startswith("de:") else e
                    for e in entries
                ]
        except (AttributeError, TypeError):
            pass
        searchString = " or ".join([searchFormat % e for e in entries])
        return self.retrieveSearchResults(searchString, **kwargs)

    def retrieveInspireID(self, string, number=None, isDoi=False, isArxiv=False):
        """Read the fetched content for a given entry
        to obtain its INSPIRE-HEP ID

        Parameters:
            string: the search string
            number (optional): the integer corresponding
                to the desired entry in the list,
                if more than one is present
            isDoi (default False): if the search string is a DOI,
                add the "doi" prefix in the url
            isArxiv (default False): if the search string is an arxiv id,
                add the "eprint" (and "arxiv:" if needed) prefix in the url
        """
        i = 0
        if isDoi:
            string = "doi+" + string
        elif isArxiv:
            if re.match("[0-9]{4}\.[0-9]{4,5}", string) and "arxiv:" not in string:
                string = "arxiv:" + string
            string = "eprint " + string
        args = self.urlArgs.copy()
        args["q"] = string.replace(" ", "%20")
        args["size"] = "1"
        args["fields"] = "control_number"
        try:
            args["page"] = int(number)
            if args["page"] == 0:
                del args["page"]
        except (TypeError, ValueError):
            pass
        url = self.createUrl(args)
        pBLogger.info(self.searchIDInfo % (string, url))
        text = self.textFromUrl(url)
        if text is None or text.strip() == "":
            pBLogger.warning(self.errorEmptyText)
            return ""
        try:
            results = json.loads(text)
        except json.decoder.JSONDecodeError:
            pBLogger.exception(self.jsonError)
            return ""
        try:
            inspireID = "%s" % results["hits"]["hits"][0]["metadata"]["control_number"]
        except (IndexError, KeyError):
            pBLogger.exception(self.genericError)
            return ""
        pBLogger.info(self.foundID % inspireID)
        return inspireID

    def retrieveCumulativeUpdates(self, date1, date2, max_iterations=20):
        """Harvest the INSPRIE API to get all the updates
        and new occurrences between two dates

        Parameters:
            date1, date2: dates that define
                the time interval to be searched
            max_iterations (default 20): maximum number of times
                that links.next is employed before stopping

        Output:
            a list of dictionaries containing the bibtex information
        """
        pBLogger.info(self.startString % time.strftime("%c"))
        hits, total = self.retrieveSearchResults(
            "du%3E%3D" + date1 + " and du%3C%3D" + date2, max_iterations=max_iterations
        )
        foundObjects = []
        if len(hits) != total:
            pBLogger.info(self.numberOfEntriesChanged % (len(hits), total))
        for count, rec in enumerate(hits):
            id = rec["metadata"]["control_number"]
            if count % 500 == 0:
                pBLogger.info(self.processed % count)
            if not rec:
                continue
            try:
                tmpDict = self.readRecord(rec)
                tmpDict["id"] = "%s" % id
                foundObjects.append(tmpDict)
            except Exception as e:
                pBLogger.exception(self.exceptionFormat % (count, id, e))
        pBLogger.info(self.processed % len(hits))
        pBLogger.info(self.endString % time.strftime("%c"))
        return foundObjects

    def processRecord(self, record, bibtex=None, readConferenceTitle=False):
        """Process the JSON entry for a given record

        Parameters:
            record: the INSPIRE-HEP JSON record
            bibtex (default None): whether the bibtex should be
                included in the output dictionary
            readConferenceTitle (boolean, default False):
                try to read the conference title if dealing
                with a proceeding

        Output:
            the dictionary containing the bibtex information
        """
        try:
            res = self.readRecord(record, readConferenceTitle=readConferenceTitle)
        except Exception:
            pBLogger.exception(self.errorReadRecord)
            return False
        if bibtex is not None:
            try:
                outcome, bibtex = self.updateBibtex(res, bibtex)
            except Exception:
                pBLogger.exception(self.errorUpdateBibtex)
                return False
            if outcome:
                res["bibtex"] = bibtex
        return res

    def retrieveOAIData(
        self, inspireID, bibtex=None, verbose=0, readConferenceTitle=False
    ):
        """Get the JSON entry for a given record

        Parameters:
            inspireID: the INSPIRE-HEP identifier (a number)
                of the desired entry
            bibtex (default None): whether the bibtex should be
                included in the output dictionary
            verbose (default 0): increase the output level
            readConferenceTitle (boolean, default False):
                try to read the conference title if dealing
                with a proceeding

        Output:
            the dictionary containing the bibtex information
        """
        hits, tot = self.retrieveAPIResults("%s%s" % (self.url, inspireID))
        if verbose > 0:
            pBLogger.info(self.readData + time.strftime("%c"))
        try:
            record = hits[0]
        except IndexError:
            pBLogger.exception(self.errorEmptySearch)
            return False
        try:
            res = self.processRecord(
                record, bibtex=bibtex, readConferenceTitle=readConferenceTitle
            )
        except Exception:
            pBLogger.exception(self.errorReadRecord)
            return False
        if verbose > 0:
            pBLogger.info(self.doneD)
        return res

    def getProceedingsTitle(self, conferenceCode, useUrl=None):
        """Use INSPIRE-HEP API to retrieve the title
        of the Proceedings associated to a conference
        identified by `conferenceCode`

        Parameters:
            conferenceCode: the identifier of the conference
                in the INSPIRE-HEP database
            useUrl (default None): if not None, the link to use
                for retrieving the title of conference proceedings

        Output:
            a string, if found, or None
        """
        if useUrl is None:
            url = (
                pbConfig.inspireConferencesAPI
                + "?q=%s" % conferenceCode
                + "&fields="
                + (",".join(self.metadataConferenceFields))
            )
            text = self.textFromUrl(url)
            try:
                info = json.loads(text)
            except (TypeError, json.decoder.JSONDecodeError):
                pBLogger.exception(self.jsonError)
                return None
            try:
                confs = [
                    a
                    for a in info["hits"]["hits"]
                    if a["metadata"]["cnum"] == conferenceCode
                ]
            except (KeyError, TypeError):
                return None
            try:
                procid = confs[0]["metadata"]["proceedings"][0]["control_number"]
            except (IndexError, KeyError, TypeError):
                return None
            url = "%s%s" % (pbConfig.inspireLiteratureAPI, procid)
        else:
            url = useUrl
        text = self.textFromUrl(url)
        try:
            info = json.loads(text)
        except json.decoder.JSONDecodeError:
            pBLogger.exception(self.jsonError)
            return None
        try:
            title = "%s: %s" % (
                info["metadata"]["titles"][0]["title"],
                info["metadata"]["titles"][0]["subtitle"],
            )
        except (IndexError, KeyError, TypeError):
            return None
        return title

    def readRecord(self, record, readConferenceTitle=False, noWarning=False):
        """Read the content of a marcxml record
        to return a bibtex string

        Parameters:
            record: the marcxml record to read
            readConferenceTitle (default False): if True, look for
                the proceedings info to get the title of the conference
            noWarning (default False): if True, suppress some warnings

        Output:
            a dictionary with the obtained fields
        """

        tmpDict = {}
        try:
            tmpDict["id"] = record["metadata"]["control_number"]
        except (KeyError, TypeError):
            tmpDict["id"] = None
        # key
        tmpDict["bibkey"] = None
        try:
            tmpDict["bibkey"] = record["metadata"]["texkeys"][0]
        except (IndexError, KeyError, TypeError):
            if not noWarning:
                pBLogger.warning(self.errorReadRecord % tmpDict["id"])
        # old keys
        tmpOld = []
        try:
            tmpOld = list(record["metadata"]["texkeys"])
            tmpOld.pop(0)
        except (IndexError, KeyError, TypeError):
            if not noWarning:
                pBLogger.warning(self.errorReadRecord % tmpDict["id"])
        tmpDict["oldkeys"] = ",".join(tmpOld)
        # doi
        tmpDict["doi"] = None
        try:
            tmpDict["doi"] = record["metadata"]["dois"][0]["value"]
        except (IndexError, KeyError, TypeError):
            pass
        # arxiv
        tmpDict["eprint"] = None
        tmpDict["archiveprefix"] = None
        try:
            tmpDict["eprint"] = record["metadata"]["arxiv_eprints"][0]["value"]
            tmpDict["archiveprefix"] = "arXiv"
        except (IndexError, KeyError, TypeError):
            pass
        tmpDict["primaryclass"] = None
        try:
            tmpDict["primaryclass"] = record["metadata"]["primary_arxiv_category"][0]
        except (IndexError, KeyError):
            try:
                tmpDict["primaryclass"] = record["metadata"]["arxiv_eprints"][0][
                    "categories"
                ][0]
            except (IndexError, KeyError, TypeError):
                pass
        # ads
        tmpDict["ads"] = None
        try:
            tmpDict["ads"] = [
                a["value"]
                for a in record["metadata"]["external_system_identifiers"]
                if a["schema"] == "ADS"
            ][0]
        except (IndexError, KeyError, TypeError):
            pass
        # authors
        try:
            tmpDict["author"] = record["metadata"]["first_author"]["full_name"]
        except KeyError:
            try:
                tmpDict["author"] = record["metadata"]["authors"][0]["full_name"]
            except (IndexError, KeyError, TypeError):
                tmpDict["author"] = ""
        try:
            if (
                record["metadata"]["author_count"]
                if "author_count" in record["metadata"].keys()
                else len(record["metadata"]["authors"])
            ) > pbConfig.params["maxAuthorSave"] - 1:
                tmpDict["author"] += " and others"
            else:
                for r in record["metadata"]["authors"][1:]:
                    tmpDict["author"] += " and %s" % r["full_name"]
        except (IndexError, KeyError, TypeError):
            pass
        # collaboration
        try:
            tmpDict["collaboration"] = ", ".join(
                [c["value"] for c in record["metadata"]["collaborations"]]
            )
        except (KeyError, TypeError):
            tmpDict["collaboration"] = None
        # title
        try:
            tmpDict["title"] = record["metadata"]["titles"][0]["title"]
        except (IndexError, KeyError, TypeError):
            tmpDict["title"] = None
        # conference title
        try:
            pi = record["metadata"]["publication_info"][0]
            conferenceCode = pi["cnum"] if "cnum" in pi.keys() else None
        except (IndexError, KeyError, TypeError):
            conferenceCode = None
        try:
            pi = record["metadata"]["publication_info"][0]
            parentUrl = pi["parent_record"]["$ref"]
        except (IndexError, KeyError, TypeError):
            parentUrl = None
        if conferenceCode is not None and readConferenceTitle:
            tmpDict["booktitle"] = self.getProceedingsTitle(
                conferenceCode, useUrl=parentUrl
            )
        # publication info
        tmpDict["year"] = None
        if tmpDict["eprint"] is not None and tmpDict["year"] is None:
            tmpDict["year"] = getYear(tmpDict["eprint"])
        try:
            pi = record["metadata"]["publication_info"][0]
            try:
                tmpDict["journal"] = pi["journal_title"]
            except KeyError:
                tmpDict["journal"] = None
            try:
                tmpDict["volume"] = pi["journal_volume"]
            except KeyError:
                tmpDict["volume"] = None
            try:
                tmpDict["year"] = pi["year"]
            except KeyError:
                pass
            try:
                tmpDict["pages"] = (
                    pi["artid"]
                    if "artid" in pi.keys()
                    else "%s-%s" % (pi["page_start"], pi["page_end"])
                    if ("page_start" in pi.keys() and "page_end" in pi.keys())
                    else pi["page_start"]
                    if "page_start" in pi.keys()
                    else None
                )
            except KeyError:
                tmpDict["pages"] = None
        except (IndexError, KeyError, TypeError):
            tmpDict["journal"] = None
            tmpDict["volume"] = None
            tmpDict["pages"] = None
        # dates
        try:
            tmpDict["firstdate"] = (
                record["metadata"]["preprint_date"]
                if "preprint_date" in record["metadata"].keys()
                else record["metadata"]["legacy_creation_date"]
                if "legacy_creation_date" in record["metadata"].keys()
                else record["metadata"]["earliest_date"]
            )
        except (KeyError, TypeError):
            tmpDict["firstdate"] = None
        try:
            tmpDict["pubdate"] = record["metadata"]["imprints"][0]["date"]
        except (IndexError, KeyError, TypeError):
            tmpDict["pubdate"] = None
        # report numbers
        tmpDict["reportnumber"] = None
        try:
            tmpDict["reportnumber"] = ", ".join(
                [c["value"] for c in record["metadata"]["report_numbers"]]
            )
        except (KeyError, TypeError):
            tmpDict["reportnumber"] = None
        # isbn
        try:
            tmpDict["isbn"] = record["metadata"]["isbns"][0]["value"]
        except (IndexError, KeyError, TypeError):
            tmpDict["isbn"] = None
        # entry type
        if tmpDict["isbn"] is not None:
            tmpDict["ENTRYTYPE"] = "book"
        else:
            try:
                collections = record["metadata"]["document_type"]
            except KeyError:
                collections = []
            if "conference paper" in collections or conferenceCode is not None:
                tmpDict["ENTRYTYPE"] = "inproceedings"
            elif "thesis" in collections:
                tmpDict["ENTRYTYPE"] = "phdthesis"
                try:
                    tmpDict["school"] = ", ".join(
                        record["metadata"]["thesis_info"]["institutions"]
                    )
                    tmpDict["year"] = record["metadata"]["thesis_info"]["date"]
                except (KeyError, TypeError):
                    pass
            else:
                tmpDict["ENTRYTYPE"] = "article"
        # clean accents
        for k in tmpDict.keys():
            try:
                tmpDict[k] = parse_accents_str(tmpDict[k])
            except Exception:
                pass
        # citations
        try:
            tmpDict["cit_no_self"] = int(
                record["metadata"]["citation_count_without_self_citations"]
            )
        except (KeyError, ValueError):
            tmpDict["cit_no_self"] = None
        try:
            tmpDict["cit"] = int(record["metadata"]["citation_count"])
        except (KeyError, ValueError):
            tmpDict["cit"] = None
        # link
        tmpDict["link"] = None
        try:
            if tmpDict["eprint"] is not None and tmpDict["eprint"] != "":
                tmpDict["link"] = pbConfig.arxivUrl + "/abs/" + tmpDict["eprint"]
        except KeyError:
            pass
        try:
            if tmpDict["doi"] is not None and tmpDict["doi"] != "":
                tmpDict["link"] = pbConfig.doiUrl + tmpDict["doi"]
        except KeyError:
            pass
        # build bibtex
        bibtexDict = {"ENTRYTYPE": tmpDict["ENTRYTYPE"], "ID": tmpDict["bibkey"]}
        for k in self.bibtexFields:
            if k in tmpDict.keys() and tmpDict[k] is not None and tmpDict[k] != "":
                bibtexDict[k] = tmpDict[k]
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [bibtexDict]
        tmpDict["bibtex"] = pbWriter.write(db)
        return tmpDict

    def updateBibtex(self, res, bibtex, force=False):
        """use OAI data to update the (existing) bibtex information.
        Unless force is True,
        update record only if publication info is present
        (assume data won't change unless the paper is published)

        Parameters:
            res: the recent search results
            bibtex: the old bibtex to be updated

        Output:
            True/False and a string containing the bibtex of the entry
        """

        def arxivEprint(element):
            """eprint has priority over arxiv field:
            if the latter is present, delete it,
            eventually copying its content into the former
            """
            if "arxiv" in element.keys():
                if "eprint" not in element.keys():
                    element["eprint"] = element["arxiv"]
                del element["arxiv"]
            return element

        try:
            element = bibtexparser.loads(bibtex).entries[0]
        except Exception:
            pBLogger.warning(self.errorInvalidBibtex % bibtex)
            return False, bibtex
        if not force:
            try:
                assert res["journal"] is not None
            except (AssertionError, KeyError):
                pBLogger.warning(self.warningJournal % (res["id"]))
                return False, bibtex
        try:
            newelement = bibtexparser.loads(res["bibtex"]).entries[0]
        except KeyError:
            newelement = {}
        except Exception:
            pBLogger.warning(self.errorInvalidBibtex % res["bibtex"])
            newelement = {}
        element = {**element, **newelement}
        element = arxivEprint(element)
        if not all([k in res for k in self.updateBibtexFields]):
            pBLogger.warning(
                self.warningMissingField
                % (
                    [k for k in self.updateBibtexFields if k not in res.keys()],
                    res["id"],
                )
            )
        for k in self.updateBibtexFields:
            if k in res and res[k] != "" and res[k] is not None:
                element[k] = res[k]
        element = arxivEprint(element)
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [element]
        return True, pbWriter.write(db)
