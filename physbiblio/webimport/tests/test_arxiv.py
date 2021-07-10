#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import datetime
import sys
import traceback

import bibtexparser
import six

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, patch
else:
    import unittest
    from unittest.mock import MagicMock, patch

try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import pbConfig
    from physbiblio.setuptests import *
    from physbiblio.strings.webimport import ArxivStrings
    from physbiblio.webimport.arxiv import WebSearch
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())

sampleFeed1 = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <link href="http://arxiv.org/api/query?search_query%3Dau%3Agariazzo%26id_list%3D%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=au:gariazzo&amp;id_list=&amp;start=0&amp;max_results=10</title>
  <id>http://arxiv.org/api/VQoV0zBpKZN/v+xgzuDvxEU0zJg</id>
  <updated>2021-07-10T00:00:00-04:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">53</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:it"""
sampleFeed2 = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <link href="http://arxiv.org/api/query?search_query%3Dau%3Agariazzo%26id_list%3D%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=au:gariazzo&amp;id_list=&amp;start=0&amp;max_results=10</title>
  <id>http://arxiv.org/api/VQoV0zBpKZN/v+xgzuDvxEU0zJg</id>
  <updated>2021-07-10T00:00:00-04:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">53</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/1510.05980v1</id>
  </entry>
  <entry>
    <updated>2016-02-18T18:24:53Z</updated>
    <published>2016-02-18T18:24:53Z</published>
    <title>Dark Radiation and Inflationary Freedom</title>
    <summary>  test1
</summary>
    <author>
      <name>Stefano Gariazzo</name>
    </author>
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1088/1742-6596/718/3/032006</arxiv:doi>
    <link title="doi" href="http://dx.doi.org/10.1088/1742-6596/718/3/032006" rel="related"/>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">Poster presented at NuPhys2015 (London, 16-18 December 2015). 5
  pages, 3 figures</arxiv:comment>
    <link href="http://arxiv.org/abs/1602.05902v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1602.05902v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>"""
sampleFeed3 = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <link href="http://arxiv.org/api/query?search_query%3Dau%3Agariazzo%26id_list%3D%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=au:gariazzo&amp;id_list=&amp;start=0&amp;max_results=10</title>
  <id>http://arxiv.org/api/VQoV0zBpKZN/v+xgzuDvxEU0zJg</id>
  <updated>2021-07-10T00:00:00-04:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">53</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/1510.05980v1</id>
    <updated>2015-10-20T17:42:31Z</updated>
    <published>2015-10-20T17:42:31Z</published>
    <title>Dark Radiation and Inflationary Freedom</title>
    <summary>  test1
</summary>
    <author>
      <name>Stefano Gariazzo</name>
    </author>
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1088/1742-6596/718/3/032006</arxiv:doi>
    <link title="doi" href="http://dx.doi.org/10.1088/1742-6596/718/3/032006" rel="related"/>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">8 pages, 4 figures; to appear in the Proceedings of the TAUP 2015
  conference</arxiv:comment>
    <link href="http://arxiv.org/abs/1510.05980v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1510.05980v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="hep-ph" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1602.05902v1</id>
    <updated>2016-02-18T18:24:53Z</updated>
    <published>2016-02-18T18:24:53Z</published>
    <title>Dark Radiation and Inflationary Freedom</title>
    <summary>  test2
</summary>
    <author>
      <name>Stefano Gariazzo</name>
    </author>
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1088/1742-6596/718/3/032006</arxiv:doi>
    <link title="doi" href="http://dx.doi.org/10.1088/1742-6596/718/3/032006" rel="related"/>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">Poster presented at NuPhys2015 (London, 16-18 December 2015). 5
  pages, 3 figures</arxiv:comment>
    <link href="http://arxiv.org/abs/1602.05902v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1602.05902v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>"""
sampleFeed4 = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <link href="http://arxiv.org/api/query?search_query%3Dau%3Agariazzo%26id_list%3D%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=au:gariazzo&amp;id_list=&amp;start=0&amp;max_results=10</title>
  <id>http://arxiv.org/api/VQoV0zBpKZN/v+xgzuDvxEU0zJg</id>
  <updated>2021-07-10T00:00:00-04:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">53</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/1510.05980v1</id>
    <updated>2015-10-20T17:42:31Z</updated>
    <published>2015-10-20T17:42:31Z</published>
    <title>Dark Radiation and Inflationary Freedom</title>
    <summary>  test1
</summary>
    <author>
      <name>Stefano Gariazzo</name>
    </author>
    <author>
      <name>Nicolao Fornengo</name>
    </author>
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1088/1742-6596/718/3/032006</arxiv:doi>
    <link title="doi" href="http://dx.doi.org/10.1088/1742-6596/718/3/032006" rel="related"/>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">8 pages, 4 figures; to appear in the Proceedings of the TAUP 2015
  conference</arxiv:comment>
    <link href="http://arxiv.org/abs/1510.05980v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1510.05980v1" rel="related" type="application/pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1602.05902v1</id>
    <updated>2016-02-18T18:24:53Z</updated>
    <published>2016-02-18T18:24:53Z</published>
    <link href="http://arxiv.org/abs/1602.05902v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1602.05902v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.CO" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>"""


class TestArxivMethods(unittest.TestCase):
    """Test the functions that import entries from arxiv.
    Should not fail if everything works fine.
    """

    def test_init(self):
        """Test init and basic class properties"""
        ws = WebSearch()
        self.assertIsInstance(ws, WebInterf)
        self.assertIsInstance(ws, ArxivStrings)
        self.assertTrue(hasattr(ws, "name"))
        self.assertTrue(hasattr(ws, "description"))
        self.assertTrue(hasattr(ws, "url"))
        self.assertTrue(hasattr(ws, "urlRss"))
        self.assertTrue(hasattr(ws, "categories"))
        self.assertIsInstance(ws.categories, dict)
        for k, v in ws.categories.items():
            self.assertIsInstance(v, list)
        self.assertTrue(hasattr(ws, "urlArgs"))
        self.assertIsInstance(physBiblioWeb.webSearch["arxiv"], WebSearch)

    def test_getYear(self):
        """test getYear"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("physbiblio.webimport.arxiv.getYear", return_value="abc") as _g:
            self.assertEqual(aws.getYear("AAA"), "abc")
            _g.assert_called_once_with("AAA")
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(aws.getYear("123456"), None)
            self.assertEqual(aws.getYear("abcde"), None)
            self.assertEqual(aws.getYear(None), None)
            _w.assert_called_once()
            self.assertEqual(aws.getYear("hep-ex/1234567"), "2012")
            self.assertEqual(aws.getYear("hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("hep-ex/1234567 hep-ex/9876543"), "2012")
            self.assertEqual(aws.getYear("astro-ph/9876543 hep-ex/1234567"), "1998")
            self.assertEqual(aws.getYear("9876543 hep-ex/1234567"), "2012")
            self.assertEqual(aws.getYear("hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("151234567 hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("1512.34567 1234567"), "2015")
            self.assertEqual(aws.getYear("astro-ph/1234.34567 1234567"), "2012")
            self.assertEqual(aws.getYear("1512.34567 1234567"), "2015")
            self.assertEqual(aws.getYear("1301.0001 2005.12345"), "2013")
            self.assertEqual(aws.getYear("0001.0001"), "2000")

    def test_retrieveUrlFirst(self):
        """test retrieveUrlFirst"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch(
            "physbiblio.webimport.arxiv.WebSearch.arxivRetriever", return_value="abc"
        ) as _g:
            self.assertEqual(aws.retrieveUrlAll("AAA"), "abc")
            _g.assert_called_once_with(
                "AAA",
                "all",
                additionalArgs={
                    "max_results": pbConfig.params["maxExternalAPIResults"]
                },
            )
            self.assertEqual(aws.retrieveUrlAll("AAA", searchType="boh"), "abc")
            _g.assert_called_with(
                "AAA",
                "boh",
                additionalArgs={
                    "max_results": pbConfig.params["maxExternalAPIResults"]
                },
            )

    def test_retrieveUrlAll(self):
        """test retrieveUrlAll"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch(
            "physbiblio.webimport.arxiv.WebSearch.arxivRetriever", return_value="abc"
        ) as _g:
            self.assertEqual(aws.retrieveUrlFirst("AAA"), "abc")
            _g.assert_called_once_with(
                "AAA", "all", additionalArgs={"max_results": "1"}
            )
            self.assertEqual(aws.retrieveUrlFirst("AAA", searchType="boh"), "abc")
            _g.assert_called_with("AAA", "boh", additionalArgs={"max_results": "1"})

    def test_arxivRetriever(self):
        """test arxivRetriever"""
        self.maxDiff = None
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.exception"
        ) as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl", return_value="myurl"
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl", return_value=""
        ) as _tu:
            self.assertEqual(aws.arxivRetriever("abc"), "")
            _cu.assert_called_once_with({"start": "0", "search_query": "all:abc"})
            self.assertEqual(aws.arxivRetriever("abc", fullDict=True), ("", {}))
            _cu.reset_mock()
            self.assertEqual(
                aws.arxivRetriever(
                    "abc", fullDict=True, searchType="au", additionalArgs={"a": "AAA"}
                ),
                ("", {}),
            )
            _cu.assert_called_once_with(
                {"start": "0", "a": "AAA", "search_query": "au:abc"}
            )
            _cu.reset_mock()
            self.assertEqual(
                aws.arxivRetriever(
                    "abc", fullDict=True, searchType="au", additionalArgs="123"
                ),
                ("", {}),
            )
            _cu.assert_called_once_with({"start": "0", "search_query": "au:abc"})
            _tu.assert_called_with("myurl")
            _tu.return_value = None
            self.assertEqual(aws.arxivRetriever("abc"), "")
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.debug"
        ) as _d, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl", return_value="myurl"
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value=sampleFeed1,
        ) as _tu:
            self.assertEqual(aws.arxivRetriever("abc"), "")
            _tu.return_value = sampleFeed2
            self.assertEqual(
                aws.arxivRetriever("abc"),
                '@Article{1510.05980,\n          year = "2015",\n'
                + ' archiveprefix = "arXiv",\n         arxiv = "1510.05980",\n}\n\n',
            )
            _tu.return_value = sampleFeed3
            self.assertEqual(
                aws.arxivRetriever("abc"),
                """@Article{1510.05980,
         title = "{Dark Radiation and Inflationary Freedom}",
          year = "2015",
 archiveprefix = "arXiv",
  primaryclass = "astro-ph.CO",
           doi = "10.1088/1742-6596/718/3/032006",
      abstract = "{test1}",
         arxiv = "1510.05980",
       authors = "Stefano Gariazzo",
}

@Article{1602.05902,
         title = "{Dark Radiation and Inflationary Freedom}",
          year = "2016",
 archiveprefix = "arXiv",
  primaryclass = "astro-ph.CO",
           doi = "10.1088/1742-6596/718/3/032006",
      abstract = "{test2}",
         arxiv = "1602.05902",
       authors = "Stefano Gariazzo",
}

""",
            )
            _tu.return_value = sampleFeed4
            self.assertEqual(
                aws.arxivRetriever("abc"),
                """@Article{1510.05980,
         title = "{Dark Radiation and Inflationary Freedom}",
          year = "2015",
 archiveprefix = "arXiv",
           doi = "10.1088/1742-6596/718/3/032006",
      abstract = "{test1}",
         arxiv = "1510.05980",
       authors = "Stefano Gariazzo and Nicolao Fornengo",
}

@Article{1602.05902,
          year = "2016",
 archiveprefix = "arXiv",
  primaryclass = "astro-ph.CO",
         arxiv = "1602.05902",
}

""",
            )
            self.assertEqual(
                aws.arxivRetriever("abc", fullDict=True),
                (
                    """@Article{1510.05980,
         title = "{Dark Radiation and Inflationary Freedom}",
          year = "2015",
 archiveprefix = "arXiv",
           doi = "10.1088/1742-6596/718/3/032006",
      abstract = "{test1}",
         arxiv = "1510.05980",
       authors = "Stefano Gariazzo and Nicolao Fornengo",
}

@Article{1602.05902,
          year = "2016",
 archiveprefix = "arXiv",
  primaryclass = "astro-ph.CO",
         arxiv = "1602.05902",
}

""",
                    {
                        "ENTRYTYPE": "article",
                        "ID": "1510.05980",
                        "abstract": "test1",
                        "archiveprefix": "arXiv",
                        "arxiv": "1510.05980",
                        "authors": "Stefano Gariazzo and Nicolao Fornengo",
                        "doi": "10.1088/1742-6596/718/3/032006",
                        "title": "Dark Radiation and Inflationary Freedom",
                        "year": "2015",
                    },
                ),
            )

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_arxivRetriever_online(self):
        """Online test arxivRetriever"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("logging.Logger.debug") as _d:
            res = aws.arxivRetriever("Zavanin", searchType="au")
        self.assertIsInstance(res, six.string_types)

    def test_arxivDaily(self):
        """test arxivDaily"""
        aws = physBiblioWeb.webSearch["arxiv"]
        raise NotImplementedError

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_arxivDaily_online(self):
        """Online test arxivDaily"""
        aws = physBiblioWeb.webSearch["arxiv"]
        res = aws.arxivDaily("astro-ph.CO")
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
