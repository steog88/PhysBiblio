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
                tmpDict["id"] = id
                foundObjects.append(tmpDict)
            except Exception as e:
                pBLogger.exception(self.exceptionFormat % (count, id, e))
        pBLogger.info(self.processed % len(hits))
        pBLogger.info(self.endString % time.strftime("%c"))
        return foundObjects

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
        if verbose > 0:
            pBLogger.info(self.doneD)
        return res

    def readRecord(self, record, readConferenceTitle=False):
        """Read the content of a marcxml record
        to return a bibtex string

        Parameters:
            record: the marcxml record to read
            readConferenceTitle (default False): if True, look for
                the proceedings info to get the title of the conference

        Output:
            a dictionary with the obtained fields
        """

        def getProceedingsTitle(conferenceCode):
            """Use INSPIRE-HEP API to retrieve the title
            of the Proceedings associated to a conference
            identified by `conferenceCode`

            Parameters:
                conferenceCode: the identifier of the conference
                    in the INSPIRE-HEP database

            Output:
                a string, if found, or None
            """
            url = (
                pbConfig.inspireConferencesAPI
                + "?q=%s" % conferenceCode
                + "&fields="
                + (",".join(self.metadataConferenceFields))
            )
            text = self.textFromUrl(url)
            try:
                info = json.loads(text)
            except json.decoder.JSONDecodeError:
                pBLogger.exception(self.jsonError)
                return None
            try:
                confs = [
                    a
                    for a in info["hits"]["hits"]
                    if a["metadata"]["cnum"] == conferenceCode
                ]
            except KeyError:
                return None
            try:
                procid = confs[0]["metadata"]["proceedings"][0]["control_number"]
            except (IndexError, KeyError):
                return None
            time.sleep(1)
            url = "%s%s" % (pbConfig.inspireLiteratureAPI, procid)
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
            except (IndexError, KeyError):
                return None
            return title

        tmpDict = {}
        # doi
        tmpDict["doi"] = None
        try:
            for q in record["metadata"]["dois"]:
                tmpDict["doi"] = q["value"]
        except KeyError:
            pass
        # arxiv
        tmpDict["eprint"] = None
        tmpDict["archiveprefix"] = None
        try:
            for q in record["metadata"]["arxiv_eprints"]:
                tmpDict["eprint"] = q["value"]
            tmpDict["archiveprefix"] = "arXiv"
        except KeyError:
            pass
        tmpDict["primaryclass"] = None
        try:
            tmpDict["primaryclass"] = record["metadata"]["primary_arxiv_category"][0]
        except (IndexError, KeyError):
            try:
                tmpDict["primaryclass"] = record["metadata"]["arxiv_eprints"][0][
                    "categories"
                ][0]
            except (IndexError, KeyError):
                pass
        # key
        tmpDict["bibkey"] = None
        tmpOld = []
        try:
            tmpDict["bibkey"] = record["metadata"]["texkeys"][0]
            tmpOld = record["metadata"]["texkeys"]
            tmpOld.pop(0)
        except (IndexError, KeyError) as e:
            pBLogger.warning(self.errorReadRecord, exc_info=True)
        if tmpDict["bibkey"] is None and len(tmpOld) > 0:
            tmpDict["bibkey"] = tmpOld[0]
            tmpOld = []
        # ads
        tmpDict["ads"] = None
        try:
            tmpDict["ads"] = [
                a["value"]
                for a in record["metadata"]["external_system_identifiers"]
                if a["schema"] == "ADS"
            ][0]
        except (IndexError, KeyError):
            pass
        # citations
        tmpDict["cit_no_self"] = record["metadata"][
            "citation_count_without_self_citations"
        ]
        tmpDict["cit"] = record["metadata"]["citation_count"]
        # publication info
        tmpDict["year"] = None
        if tmpDict["eprint"] is not None and tmpDict["year"] is None:
            tmpDict["year"] = getYear(tmpDict["eprint"])
        try:
            pi = record["metadata"]["publication_info"][0]
            tmpDict["journal"] = pi["journal_title"]
            tmpDict["volume"] = pi["journal_volume"]
            tmpDict["year"] = pi["year"]
            tmpDict["pages"] = (
                pi["artid"]
                if "artid" in pi.keys()
                else pi["page_start"]
                if "page_start" in pi.keys()
                else ""
            )
            conferenceCode = pi["cnum"] if "cnum" in pi.keys() else None
        except (IndexError, KeyError):
            tmpDict["journal"] = None
            tmpDict["volume"] = None
            tmpDict["pages"] = None
            conferenceCode = None
        # dates
        try:
            tmpDict["firstdate"] = (
                record["metadata"]["preprint_date"]
                if "preprint_date" in record["metadata"].keys()
                else record["metadata"]["legacy_creation_date"]
                if "legacy_creation_date" in record["metadata"].keys()
                else record["metadata"]["earliest_date"]
            )
        except KeyError:
            tmpDict["firstdate"] = None
        try:
            tmpDict["pubdate"] = record["metadata"]["imprints"][0]["date"]
        except (IndexError, KeyError):
            tmpDict["pubdate"] = None
        # authors
        try:
            tmpDict["author"] = record["metadata"]["first_author"]["full_name"]
        except KeyError:
            try:
                tmpDict["author"] = record["metadata"]["authors"][0]["full_name"]
            except (IndexError, KeyError):
                tmpDict["author"] = ""
        try:
            addAuthors = 0
            if (
                record["metadata"]["author_count"]
                if "author_count" in record["metadata"].keys()
                else len(record["metadata"]["authors"])
            ) > pbConfig.params["maxAuthorSave"] - 1:
                tmpDict["author"] += " and others"
            else:
                for r in record["metadata"]["authors"][1:]:
                    addAuthors += 1
                    if addAuthors > pbConfig.params["maxAuthorSave"]:
                        tmpDict["author"] += " and others"
                        break
                    tmpDict["author"] += " and %s" % r["full_name"]
        except (KeyError, IndexError):
            pass
        # collaboration
        try:
            tmpDict["collaboration"] = ", ".join(
                [c["value"] for c in record["metadata"]["collaborations"]]
            )
        except KeyError:
            tmpDict["collaboration"] = None
        # report numbers
        tmpDict["reportnumber"] = None
        try:
            tmpDict["reportnumber"] = ", ".join(
                [c["value"] for c in record["metadata"]["report_numbers"]]
            )
        except KeyError:
            tmpDict["reportnumber"] = None
        # title
        try:
            tmpDict["title"] = record["metadata"]["titles"][0]["title"]
        except TypeError:
            tmpDict["title"] = None
        if conferenceCode is not None and readConferenceTitle:
            tmpDict["booktitle"] = getProceedingsTitle(conferenceCode)
        # isbn
        try:
            tmpDict["isbn"] = record["metadata"]["isbns"][0]["value"]
        except (IndexError, KeyError):
            tmpDict["isbn"] = None
        # entry type
        if tmpDict["isbn"] is not None:
            tmpDict["ENTRYTYPE"] = "book"
        else:
            try:
                collections = record["metadata"]["document_type"]
            except KeyError:
                collections = []
            if "conferencepaper" in collections or conferenceCode is not None:
                tmpDict["ENTRYTYPE"] = "inproceedings"
            elif "thesis" in collections:
                tmpDict["ENTRYTYPE"] = "phdthesis"
                try:
                    tmpDict["school"] = record["metadata"]["thesis_info"][
                        "institutions"
                    ]
                    tmpDict["year"] = record["metadata"]["thesis_info"]["date"]
                except KeyError:
                    pass
            else:
                tmpDict["ENTRYTYPE"] = "article"
        # old keys
        tmpDict["oldkeys"] = ",".join(tmpOld)
        for k in tmpDict.keys():
            try:
                tmpDict[k] = parse_accents_str(tmpDict[k])
            except Exception:
                pass
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

    def updateBibtex(self, res, bibtex):
        """use OAI data to update the (existing) bibtex information
        of an entry

        Parameters:
            res: the recent search results
            bibtex: the old bibtex to be updated

        Output:
            True/False and a string containing the bibtex of the entry
        """
        try:
            element = bibtexparser.loads(bibtex).entries[0]
        except:
            pBLogger.warning(self.errorInvalidBibtex % bibtex)
            return False, bibtex
        if res["journal"] is None:
            pBLogger.warning(self.warningJournal % (res["id"]))
            return False, bibtex
        try:
            for k in ["doi", "volume", "pages", "year", "journal"]:
                if res[k] != "" and res[k] is not None:
                    element[k] = res[k]
        except KeyError:
            pBLogger.warning(self.warningMissing % (res["id"]))
            return False, bibtex
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [element]
        return True, pbWriter.write(db)
