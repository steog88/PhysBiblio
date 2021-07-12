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
    from physbiblio.webimport.arxiv import WebSearch, isValidArxiv
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

sampleDailyFeed1 = """<?xml version="1.0" encoding="UTF-8"?>

<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
 xmlns:admin="http://webns.net/mvcb/"
>

<channel rdf:about="http://arxiv.org/">
<title>hep-ex updates on arXiv.org</title>
<link>http://arxiv.org/</link>
<description rdf:parseType="Literal">High Energy Physics - Experiment (hep-ex) updates on the arXiv.org e-print archive</description>
<dc:language>en-us</dc:language>
<dc:date>2021-07-08T20:30:00-05:00</dc:date>
<dc:publisher>www-admin@arxiv.org</dc:publisher>
<dc:subject>High Energy Physics - Experiment</dc:subject>
<syn:updateBase>1901-01-01T00:00+00:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>daily</syn:updatePeriod>
<image rdf:resource="http://arxiv.org/icons/sfx.gif" />
</channel>
<image rdf:about="http://arxiv.org/icons/sfx.gif">
<title>arXiv.org</title>
<url>http://arxiv.org/icons/sfx.gif</url>
<link>http://arxiv.org/</link>
</image>
<item rdf:about="http://arxiv.org/abs/2107.03419">
<title>Observation of excited $\Omega_c^0$ baryons in $\Omega_b^- \to \Xi_c^+ K^-\pi^-$ decays. (arXiv:2107.03419v1 [hep-ex])</title>
<link>http://arxiv.org/abs/2107.03419</link>
<description rdf:parseType="Literal">desc1
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/au:+collaboration_LHCb/0/1/0/all/0/1&quot;&gt;LHCb collaboration&lt;/a&gt;: &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/au:+Aaij_R/0/1/0/all/0/1&quot;&gt;R. Aaij&lt;/a&gt;, et al. (909 additional authors not shown)</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/2106.00550">
<title>Potential applications of modular representation theory to quantum mechanics. (arXiv:2106.00550v2 [math.GR] CROSS LISTED)</title>
<link>http://arxiv.org/abs/2106.00550</link>
<description rdf:parseType="Literal">desc2
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/math/1/au:+Wilson_R/0/1/0/all/0/1&quot;&gt;Robert A. Wilson&lt;/a&gt;</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/2007.03939">
<title>Fireball tomography from bottomonia elliptic flow in relativistic heavy-ion collisions. (arXiv:2007.03939v2 [hep-ph] UPDATED)</title>
<link>http://arxiv.org/abs/2007.03939</link>
<description rdf:parseType="Literal">desc3
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/hep-ph/1/au:+Bhaduri_P/0/1/0/all/0/1&quot;&gt;Partha Pratim Bhaduri&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/hep-ph/1/au:+Alqahtani_M/0/1/0/all/0/1&quot;&gt;Mubarak Alqahtani&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/hep-ph/1/au:+Borghini_N/0/1/0/all/0/1&quot;&gt;Nicolas Borghini&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/hep-ph/1/au:+Jaiswal_A/0/1/0/all/0/1&quot;&gt;Amaresh Jaiswal&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/hep-ph/1/au:+Strickland_M/0/1/0/all/0/1&quot;&gt;Michael Strickland&lt;/a&gt;</dc:creator>
</item>
</rdf:RDF>"""
sampleDailyFeed2 = """<?xml version="1.0" encoding="UTF-8"?>

<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
 xmlns:admin="http://webns.net/mvcb/"
>

<channel rdf:about="http://arxiv.org/">
<title>hep-ex updates on arXiv.org</title>
<link>http://arxiv.org/</link>
<description rdf:parseType="Literal">High Energy Physics - Experiment (hep-ex) updates on the arXiv.org e-print archive</description>
<dc:language>en-us</dc:language>
<dc:date>2021-07-08T20:30:00-05:00</dc:date>
<dc:publisher>www-admin@arxiv.org</dc:publisher>
<dc:subject>High Energy Physics - Experiment</dc:subject>
<syn:updateBase>1901-01-01T00:00+00:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>daily</syn:updatePeriod>
<image rdf:resource="http://arxiv.org/icons/sfx.gif" />
</channel>
<image rdf:about="http://arxiv.org/icons/sfx.gif">
<title>arXiv.org</title>
<url>http://arxiv.org/icons/sfx.gif</url>
<link>http://arxiv.org/</link>
</image>
<item rdf:about="http://arxiv.org/abs/2107.03419">
<link>http://arxiv.org/abs/2107.03419</link>
<description rdf:parseType="Literal">desc1
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/au:+collaboration_LHCb/0/1/0/all/0/1&quot;&gt;LHCb collaboration&lt;/a&gt;: &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/au:+Aaij_R/0/1/0/all/0/1&quot;&gt;R. Aaij&lt;/a&gt;, et al. (909 additional authors not shown)</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/2106.00550">
<title>Potential applications of modular representation theory to quantum mechanics. (arXiv:2106.00550v2 [math.GR] CROSS LISTED)</title>
<link>http://arxiv.org/abs/2106.00550</link>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/math/1/au:+Wilson_R/0/1/0/all/0/1&quot;&gt;Robert A. Wilson&lt;/a&gt;</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/2007.03939">
<title>Fireball tomography from bottomonia elliptic flow in relativistic heavy-ion collisions. (arXiv:2007.03939v2 [hep-ph] UPDATED)</title>
<link>http://arxiv.org/abs/2007.03939</link>
<description rdf:parseType="Literal">desc3
</description>
</item>
</rdf:RDF>"""


class TestArxivMethods(unittest.TestCase):
    """Test the functions that import entries from arxiv.
    Should not fail if everything works fine.
    """

    def test_isValidArxiv(self):
        """test isValidArxiv"""
        self.assertTrue(isValidArxiv("arxiv:0703.0000v15"))
        self.assertTrue(isValidArxiv("0703.0000v1"))
        self.assertTrue(isValidArxiv("0703.0000"))
        self.assertTrue(isValidArxiv("arxiv:1712.01000v15"))
        self.assertTrue(isValidArxiv("1712.02000v1"))
        self.assertTrue(isValidArxiv("1712.02000"))
        self.assertTrue(isValidArxiv("hep-ph/9912567v10"))
        self.assertTrue(isValidArxiv("hep-ph/9912567v1"))
        self.assertTrue(isValidArxiv("arxiv:hep-ph/9912567"))
        self.assertTrue(isValidArxiv("arxiv:math/9902567v10"))
        self.assertTrue(isValidArxiv("math/9902567v1"))
        self.assertTrue(isValidArxiv("math/9902567"))
        self.assertTrue(isValidArxiv("arxiv:math.CO/0112567v10"))
        self.assertTrue(isValidArxiv("math.CO/0112567v4"))
        self.assertTrue(isValidArxiv("math.CO/0112567"))
        self.assertTrue(isValidArxiv("cs/0112567v10"))
        self.assertTrue(isValidArxiv("cs/0112567v4"))
        self.assertTrue(isValidArxiv("cs/0112567"))
        self.assertTrue(isValidArxiv("astro-ph.CO/0001567v10"))
        self.assertTrue(isValidArxiv("arxiv:astro-ph.CO/0001567v9"))
        self.assertTrue(isValidArxiv("arxiv:astro-ph.CO/0001567"))
        self.assertTrue(isValidArxiv("physics.acc-ph/0001567v9"))
        self.assertTrue(isValidArxiv("physics.acc-ph/0001567"))
        self.assertTrue(isValidArxiv("physics.acc-ph/0001567v10"))
        self.assertTrue(isValidArxiv("cond-mat.dis-nn/0001567"))
        self.assertTrue(isValidArxiv("cond-mat.dis-nn/0001567v9"))
        self.assertTrue(isValidArxiv("cond-mat.dis-nn/0001567"))
        self.assertFalse(isValidArxiv("1712.000"))
        self.assertFalse(isValidArxiv("1712.000v1"))
        self.assertFalse(isValidArxiv("1712.000123"))
        self.assertFalse(isValidArxiv("172.0000"))
        self.assertFalse(isValidArxiv("172.0000v1"))
        self.assertFalse(isValidArxiv("172.00123"))
        self.assertFalse(isValidArxiv("astroph/1234567"))
        self.assertFalse(isValidArxiv("a/1234567"))
        self.assertFalse(isValidArxiv("mat/1234567"))
        self.assertFalse(isValidArxiv("math/123456"))
        self.assertFalse(isValidArxiv("hep-ex/123456"))
        self.assertFalse(isValidArxiv("cond-mat.dis-nn/123456"))
        self.assertFalse(isValidArxiv("mat.CO/1234567"))
        self.assertFalse(isValidArxiv("math.ZZ/1234567"))

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
        with patch("logging.Logger.info") as _i:
            res = aws.arxivRetriever("Zavanin", searchType="au")
        self.assertIsInstance(res, six.string_types)

    def test_arxivDaily(self):
        """test arxivDaily"""
        self.maxDiff = None
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.exception"
        ) as _e, patch("logging.Logger.warning") as _w, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl", return_value=""
        ) as _tu:
            self.assertEqual(aws.arxivDaily("abc"), False)
            _tu.assert_not_called()
            self.assertEqual(aws.arxivDaily("abc"), False)
            _tu.assert_not_called()
            self.assertEqual(aws.arxivDaily("astro-ph.ab"), False)
            _tu.assert_not_called()
            _tu.return_value = None
            self.assertEqual(aws.arxivDaily("hep-ph"), False)
            _tu.assert_called_once_with("https://export.arxiv.org/rss/hep-ph")
            _tu.return_value = sampleFeed1
            self.assertEqual(aws.arxivDaily("astro-ph.CO"), [])
            _tu.assert_called_with("https://export.arxiv.org/rss/astro-ph.CO")
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.exception"
        ) as _e, patch("logging.Logger.warning") as _w, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value=sampleDailyFeed1,
        ) as _tu:
            self.assertEqual(
                aws.arxivDaily("hep-ex"),
                [
                    {
                        "abstract": "desc1",
                        "author": "LHCb collaboration and R. Aaij",
                        "authors": ["LHCb collaboration", "R. Aaij"],
                        "cross": False,
                        "eprint": "2107.03419",
                        "primaryclass": "hep-ex",
                        "replacement": False,
                        "title": "Observation of excited $\\Omega_c^0$ baryons in $\\Omega_b^- \to "
                        "\\Xi_c^+ K^-\\pi^-$ decays.",
                        "version": "2107.03419v1",
                    },
                    {
                        "abstract": "desc2",
                        "author": "Robert A. Wilson",
                        "authors": ["Robert A. Wilson"],
                        "cross": True,
                        "eprint": "2106.00550",
                        "primaryclass": "math.GR",
                        "replacement": False,
                        "title": "Potential applications of modular representation theory to quantum "
                        "mechanics.",
                        "version": "2106.00550v2",
                    },
                    {
                        "abstract": "desc3",
                        "author": "Partha Pratim Bhaduri and Mubarak Alqahtani and Nicolas Borghini "
                        "and others",
                        "authors": [
                            "Partha Pratim Bhaduri",
                            "Mubarak Alqahtani",
                            "Nicolas Borghini",
                            "Amaresh Jaiswal",
                            "Michael Strickland",
                        ],
                        "cross": True,
                        "eprint": "2007.03939",
                        "primaryclass": "hep-ph",
                        "replacement": True,
                        "title": "Fireball tomography from bottomonia elliptic flow in relativistic "
                        "heavy-ion collisions.",
                        "version": "2007.03939v2",
                    },
                ],
            )
            _tu.return_value = sampleDailyFeed2
            self.assertEqual(aws.arxivDaily("hep-ex"), [])

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_arxivDaily_online(self):
        """Online test arxivDaily"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("logging.Logger.info") as _i:
            res = aws.arxivDaily("astro-ph.CO")
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
