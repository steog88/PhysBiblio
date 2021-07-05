#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import datetime
import os
import sys
import traceback

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

if sys.version_info[0] < 3:
    import unittest2 as unittest
else:
    import unittest

try:
    from physbiblio.config import pbConfig
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.setuptests import *
    from physbiblio.webimport.webInterf import PBSession, WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.online, "Online tests")
class TestWebImportMethods(unittest.TestCase):
    """Test the functions that import entries from the web.
    Should not fail if everything works fine.
    """

    def test_methods_success(self):
        """Test webimport with known results"""
        self.maxDiff = None
        tests = {
            "arxiv": [
                "1507.08204",
                u"@Article{1507.08204,\n         title = "
                + '"{Light sterile neutrinos}",\n          year = "2015",'
                + '\n archiveprefix = "arXiv",\n  primaryclass = '
                + '"hep-ph",\n           doi = '
                + '"10.1088/0954-3899/43/3/033001",\n      abstract = '
                + '"{The theory and phenomenology of light sterile neutrinos'
                + " at the eV mass scale is reviewed. The reactor, Gallium "
                + "and LSND anomalies are briefly described and interpreted "
                + "as indications of the existence of short-baseline "
                + "oscillations which require the existence of light sterile"
                + " neutrinos. The global fits of short-baseline oscillation"
                + " data in 3+1 and 3+2 schemes are discussed, together "
                + "with the implications for beta-decay and neutrinoless "
                + "double-beta decay. The cosmological effects of light "
                + "sterile neutrinos are briefly reviewed and the "
                + "implications of existing cosmological data are discussed."
                + " The review concludes with a summary of future "
                + 'perspectives.}",\n         arxiv = "1507.08204",\n    '
                + '   authors = "S. Gariazzo and C. Giunti and M. Laveder '
                + 'and Y. F. Li and E. M. Zavanin",\n}',
            ],
            "doi": [
                "10.1088/0954-3899/43/3/033001",
                """@article{Gariazzo_2015,
	doi = {10.1088/0954-3899/43/3/033001},
	url = {"""
                + pbConfig.doiUrl
                + """10.1088%2F0954-3899%2F43%2F3%2F033001},
	year = 2015,
	month = {mar},
	publisher = {{IOP} Publishing},
	volume = {43},
	number = {3},
	pages = {033001},
	author = {S Gariazzo and C Giunti and M Laveder and Y F Li and E M Zavanin},
	title = {Light sterile neutrinos},
	journal = {Journal of Physics G: Nuclear and Particle Physics}
}""",
            ],
            "inspire": [
                "Gariazzo:2015rra",
                """@article{Gariazzo:2015rra,
    author = "Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y. F. and Zavanin, E. M.",
    title = "{Light sterile neutrinos}",
    eprint = "1507.08204",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    doi = "10.1088/0954-3899/43/3/033001",
    journal = "J. Phys. G",
    volume = "43",
    pages = "033001",
    year = "2016"
}""",
            ],
            "isbn": [
                "9781107013957",
                """@book{9781107013957,
  Author = {Julien Lesgourgues, Gianpiero Mangano, Gennaro Miele},
  Title = {Neutrino Cosmology},
  Publisher = {Cambridge University Press},
  Year = {2014},
  Date = {2014-02-28},
  PageTotal = {392 Seiten},
  EAN = {9781107013957},
  ISBN = {110701395X},
  URL = {https://www.ebook.de/de/product/19797496/julien_lesgourgues_gianpiero_mangano_gennaro_miele_neutrino_cosmology.html}
}""",
            ],
        }
        for method, strings in tests.items():
            print(method)
            if method == "arxiv":
                self.assertEqual(
                    physBiblioWeb.webSearch[method]
                    .retrieveUrlFirst(strings[0], searchType="id")
                    .strip(),
                    strings[1].strip(),
                )
                self.assertEqual(
                    physBiblioWeb.webSearch[method]
                    .retrieveUrlAll(strings[0], searchType="id")
                    .strip(),
                    strings[1].strip(),
                )
            else:
                self.assertEqual(
                    physBiblioWeb.webSearch[method]
                    .retrieveUrlFirst(strings[0])
                    .strip(),
                    strings[1].strip(),
                )
                self.assertEqual(
                    physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(),
                    strings[1].strip(),
                )

    def test_methods_insuccess(self):
        """Test webimport using missing and/or invalid identifiers"""
        print(physBiblioWeb.webSearch.keys())
        self.maxDiff = None
        tests = {
            "arxiv": ["1801.15000", ""],
            "doi": ["10.1088/9999-3899/43/a/033001", ""],
            "inspire": ["Gariazzo:2014rra", ""],
            "isbn": ["978019850871a", ""],
        }
        self.assertFalse(physBiblioWeb.webSearch["inspire"].retrieveOAIData("9999999"))
        for method, strings in tests.items():
            print(method)
            res = physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0])
            print(res)
            self.assertEqual(res.strip(), strings[1].strip())
            self.assertEqual(
                physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(),
                strings[1].strip(),
            )


class TestWebImportOffline(unittest.TestCase):
    """Offline test for some functions of the webImport package."""

    def test_PBSession(self):
        """test the PBSession class"""
        pbs = PBSession()
        self.assertIsInstance(pbs, requests.Session)
        fr = Retry()
        ha = HTTPAdapter(max_retries=fr)
        with patch(
            "physbiblio.webimport.webInterf.Retry", return_value=fr
        ) as _r, patch(
            "physbiblio.webimport.webInterf.HTTPAdapter", return_value=ha
        ) as _ha, patch(
            "requests.Session.mount"
        ) as _m:
            pbs = PBSession()
            _r.assert_called_once_with(
                total=5,
                backoff_factor=1.0,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )
            _ha.assert_called_once_with(max_retries=fr)
            _m.assert_any_call("https://", ha)
            _m.assert_any_call("http://", ha)

    def test_createUrl(self):
        """Test createUrl"""
        pbw = WebInterf()
        pbw.url = pbConfig.inspireLiteratureAPI
        pbw.urlArgs = {"abc": "1", "def": "2"}
        self.assertEqual(
            pbw.createUrl(), "https://inspirehep.net/api/literature/?abc=1&def=2"
        )
        self.assertEqual(
            pbw.createUrl({"abc": "2", "def": "1"}),
            "https://inspirehep.net/api/literature/?abc=2&def=1",
        )
        self.assertEqual(
            pbw.createUrl({}),
            "https://inspirehep.net/api/literature/",
        )
        self.assertEqual(
            pbw.createUrl({}, ""),
            "https://inspirehep.net/api/literature/",
        )
        self.assertEqual(
            pbw.createUrl({"def": "1"}, "abc"),
            "abc?def=1",
        )

    def test_inspire_retrieve(self):
        """Test retrieveUrlFirst and retrieveUrlAll from inspire module"""
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveBibtex",
            autospec=True,
            side_effect=["abc", "def"],
        ) as _f:
            self.assertEqual(
                physBiblioWeb.webSearch["inspire"].retrieveUrlFirst("abc"), "abc"
            )
            _f.assert_called_once_with(
                physBiblioWeb.webSearch["inspire"], "abc", size=1
            )
            _f.reset_mock()
            self.assertEqual(
                physBiblioWeb.webSearch["inspire"].retrieveUrlAll("abc"), "def"
            )
            _f.assert_called_once_with(
                physBiblioWeb.webSearch["inspire"], "abc", size=250
            )

    def test_arxivYear(self):
        """test the arxivDaily method in the arxiv module"""
        self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("abc"), None)
        self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("0123.345"), None)
        self.assertEqual(
            physBiblioWeb.webSearch["arxiv"].getYear("hep-ph/9900000"), "1999"
        )
        self.assertEqual(
            physBiblioWeb.webSearch["arxiv"].getYear("hep-ph/990000"), None
        )
        self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("1234.5678"), "2012")
        self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("1678.56789"), "2016")

    def test_arxivDaily(self):
        """test the arxivDaily method in the arxiv module"""
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(physBiblioWeb.webSearch["arxiv"].arxivDaily("missing"))
            self.assertFalse(
                physBiblioWeb.webSearch["arxiv"].arxivDaily("physics.missing")
            )
        content_example = (
            """<?xml version="1.0" encoding="UTF-8"?>

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
<description rdf:parseType="Literal">High Energy Physics - """
            + """Experiment (hep-ex) updates on the arXiv.org e-print archive</description>
<dc:language>en-us</dc:language>
<dc:date>2018-05-23T20:30:00-05:00</dc:date>
<dc:publisher>www-admin@arxiv.org</dc:publisher>
<dc:subject>High Energy Physics - Experiment</dc:subject>
<syn:updateBase>1901-01-01T00:00+00:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>daily</syn:updatePeriod>
<items>
 <rdf:Seq>
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.08875" />
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.09166" />
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.06430" />
 </rdf:Seq>
</items>
<image rdf:resource="http://arxiv.org/icons/sfx.gif" />
</channel>
<image rdf:about="http://arxiv.org/icons/sfx.gif">
<title>arXiv.org</title>
<url>http://arxiv.org/icons/sfx.gif</url>
<link>http://arxiv.org/</link>
</image>
<item rdf:about="http://arxiv.org/abs/1805.08875">
<title>Measurement of Transverse Single Spin Asymmetries. """
            + """(arXiv:1805.08875v1 [hep-ex])</title>
<link>http://arxiv.org/abs/1805.08875</link>
<description rdf:parseType="Literal">&lt;p&gt;In 2015 the first """
            + """collisions between polarized protons and nuclei occurred at
the Relativistic Heavy Ion Collider (RHIC), at a center-of-mass energy of
$\sqrt{s_{NN}}=200$ GeV. Comparisons between spin asymmetries and
cross-sections in $p+p$ production to those in $p+A$ production provide insight
into nuclear structure, namely nuclear modification factors, nuclear dependence
of spin asymmetries, and comparison to models with saturation effects. The
transverse single-spin asymmetry, $A_{N}$, has been measured in $\pi^{0}$
production in the STAR Forward Meson Spectrometer (FMS), an electromagnetic
calorimeter covering a forward psuedorapidity range """
            + """of $2.6&amp;lt;\eta&amp;lt;4$. Within
this kinematic range, STAR has previously reported the persistence of large
$\pi^0$ asymmetries with unexpected dependences on $p_T$ and event topology in
$p+p$ collisions. This talk will compare these dependences to those in $p+A$
production.
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/"""
            + """au:+Dilks_C/0/1/0/all/0/1&quot;&gt;Christopher Dilks&lt;/a&gt; """
            + """(STAR Collaboration)</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/1805.09166">
<title>Recent Top quark results from the Tevatron. """
            + """(arXiv:1805.09166v1 [hep-ex] CROSS LISTED)</title>
<link>http://arxiv.org/abs/1805.09166</link>
<description rdf:parseType="Literal">&lt;p&gt;We present recent measurements
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/"""
            + """hep-ex/1/au:+Tuchming_B/0/1/0/all/0/1&quot;&gt;"""
            + """Boris Tuchming&lt;/a&gt;</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/1805.06430">
<title>New Perspective on Hybrid Mesons. (arXiv:1805.06430v2 """
            + """[nucl-th] UPDATED)</title>
<link>http://arxiv.org/abs/1805.06430</link>
<description rdf:parseType="Literal">&lt;p&gt;It is thought that """
            + """strong interactions within the Standard Model can generate
bound-states in which non-Abelian gauge-bosons play a dual role, serving both
as force and matter fields.
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/"""
            + """nucl-th/1/au:+Xu_S/0/1/0/all/0/"""
            + """1&quot;&gt;Shu-Sheng Xu&lt;/a&gt;, &lt;a """
            + """href=&quot;http://arxiv.org/find/"""
            + """nucl-th/1/au:+Cui_Z/0/1/0/all/"""
            + """0/1&quot;&gt;Zhu-Fang Cui&lt;/a&gt;, &lt;a """
            + """href=&quot;http://arxiv.org/find/nucl-th/1/au:+"""
            + """Chang_L/0/1/0/all/0/1&quot;&gt;Lei Chang&lt;/"""
            + """a&gt;, &lt;a href=&quot;http://arxiv.org/find/nucl-th/1/au:+"""
            + """Papavassiliou_J/0/1/0/all/0/1&quot;&gt;Joannis """
            + """Papavassiliou&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/"""
            + """nucl-th/1/au:+Roberts_C/0/1/0/all/0/1&quot;"""
            + """&gt;Craig D. Roberts&lt;/a&gt;, &lt;a """
            + """href=&quot;http://arxiv.org/find/nucl-th/"""
            + """1/au:+Zong_H/0/1/0/all/0/1&quot;&gt;Hong-Shi Zong"""
            + """&lt;/a&gt;</dc:creator>
</item>
</rdf:RDF>"""
        )
        with patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value=content_example,
            autospec=True,
        ) as _fromUrl, patch.dict(pbConfig.params, {"maxAuthorNames": 3}, clear=False):
            result = physBiblioWeb.webSearch["arxiv"].arxivDaily("hep-ex")
            _fromUrl.assert_called_once_with(
                physBiblioWeb.webSearch["arxiv"], "https://export.arxiv.org/rss/hep-ex"
            )
            self.assertEqual(
                result[0],
                {
                    "primaryclass": u"hep-ex",
                    "author": u"Christopher Dilks",
                    "title": u"Measurement of Transverse Single Spin Asymmetries.",
                    "abstract": u"In 2015 the first collisions between "
                    + "polarized protons and nuclei occurred at the "
                    + "Relativistic Heavy Ion Collider (RHIC), at a "
                    + "center-of-mass energy of $\\sqrt{s_{NN}}=200$ GeV. "
                    + "Comparisons between spin asymmetries and cross-sections "
                    + "in $p+p$ production to those in $p+A$ production "
                    + "provide insight into nuclear structure, namely "
                    + "nuclear modification factors, nuclear dependence "
                    + "of spin asymmetries, and comparison to models "
                    + "with saturation effects. The transverse single-spin "
                    + "asymmetry, $A_{N}$, has been measured in $\\pi^{0}$ "
                    + "production in the STAR Forward Meson Spectrometer "
                    + "(FMS), an electromagnetic calorimeter covering a "
                    + "forward psuedorapidity range of $2.6&lt;\\eta&lt;4$. "
                    + "Within this kinematic range, STAR has previously "
                    + "reported the persistence of large $\\pi^0$ asymmetries "
                    + "with unexpected dependences on $p_T$ and event topology "
                    + "in $p+p$ collisions. This talk will compare "
                    + "these dependences to those in $p+A$ production. ",
                    "cross": False,
                    "version": u"1805.08875v1",
                    "eprint": u"1805.08875",
                    "authors": [u"Christopher Dilks"],
                    "replacement": False,
                },
            )
            self.assertEqual(
                result[1],
                {
                    "primaryclass": u"hep-ex",
                    "author": u"Boris Tuchming",
                    "title": u"Recent Top quark results from the Tevatron.",
                    "abstract": u"We present recent measurements ",
                    "cross": True,
                    "version": u"1805.09166v1",
                    "eprint": u"1805.09166",
                    "authors": [u"Boris Tuchming"],
                    "replacement": False,
                },
            )
            self.assertEqual(
                result[2],
                {
                    "primaryclass": u"nucl-th",
                    "author": u"Shu-Sheng Xu and Zhu-Fang Cui and "
                    + "Lei Chang and others",
                    "title": u"New Perspective on Hybrid Mesons.",
                    "abstract": u"It is thought that strong interactions "
                    + "within the Standard Model can generate bound-states "
                    + "in which non-Abelian gauge-bosons play a dual role, "
                    + "serving both as force and matter fields. ",
                    "cross": True,
                    "version": u"1805.06430v2",
                    "eprint": u"1805.06430",
                    "authors": [
                        u"Shu-Sheng Xu",
                        u"Zhu-Fang Cui",
                        u"Lei Chang",
                        u"Joannis Papavassiliou",
                        u"Craig D. Roberts",
                        u"Hong-Shi Zong",
                    ],
                    "replacement": True,
                },
            )


if __name__ == "__main__":
    unittest.main()
