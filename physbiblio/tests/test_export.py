#!/usr/bin/env python
"""Test file for the physbiblio.export module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback
from stat import S_IREAD, S_IRGRP, S_IROTH

import bibtexparser

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import patch
else:
    import unittest
    from unittest.mock import patch

try:
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.export import pBExport
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.long, "Long tests")
class TestExportMethods(unittest.TestCase):
    """Tests for methods in physbiblio.export"""

    def setUp(self):
        """Generate filenames"""
        self.testBibName = os.path.join(pbConfig.dataPath, "tests_%s.bib" % today_ymd)
        self.testTexName = os.path.join(pbConfig.dataPath, "tests_%s.tex" % today_ymd)

    def tearDown(self):
        """remove files"""
        if os.path.exists(self.testBibName):
            os.remove(self.testBibName)
        if os.path.exists(self.testTexName):
            os.remove(self.testTexName)

    def test_backup(self):
        """Test backup file creation and related"""
        emptyFileName = self.testBibName
        if os.path.exists(emptyFileName):
            os.remove(emptyFileName)
        if os.path.exists(emptyFileName + pBExport.backupExtension):
            os.remove(emptyFileName + pBExport.backupExtension)
        self.assertFalse(pBExport.backupCopy(emptyFileName))
        self.assertFalse(os.path.exists(emptyFileName))
        self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))
        open(emptyFileName, "a").close()
        self.assertTrue(pBExport.backupCopy(emptyFileName))
        self.assertTrue(os.path.exists(emptyFileName + pBExport.backupExtension))
        os.remove(emptyFileName)
        self.assertFalse(os.path.exists(emptyFileName))
        self.assertTrue(pBExport.restoreBackupCopy(emptyFileName))
        self.assertTrue(os.path.exists(emptyFileName))
        with patch("os.path.isfile", side_effect=[False, True, True]) as _isf, patch(
            "shutil.copy2", side_effect=[True, IOError]
        ) as _cp2, patch("logging.Logger.exception") as _ex:
            self.assertFalse(pBExport.restoreBackupCopy(emptyFileName))
            self.assertTrue(pBExport.restoreBackupCopy(emptyFileName))
            self.assertFalse(pBExport.restoreBackupCopy(emptyFileName))
            _ex.assert_called_once()
        self.assertTrue(pBExport.rmBackupCopy(emptyFileName))
        self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))

    def test_offlineExports(self):
        """Test of offline export functions exportSelected,
        updateExportedBib
        """
        testBibName = self.testBibName
        sampleList = [
            {"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'},
            {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'},
        ]
        sampleTxt = (
            '@Article{empty,\nauthor="me",\ntitle="no"\n}\n'
            + '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
        )
        pBDB.bibs.lastFetched = sampleList
        pBExport.exportLast(testBibName)
        with open(testBibName) as f:
            self.assertEqual(f.read(), sampleTxt)
        os.remove(testBibName)

        sampleList = [{"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}'}]
        sampleTxt = '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}\n'
        pBExport.exportSelected(testBibName, sampleList)
        with open(testBibName) as f:
            self.assertEqual(f.read(), sampleTxt)

        with patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[
                {
                    "bibtexDict": {
                        "ID": "empty2",
                        "ENTRYTYPE": "Article",
                        "author": "me et al",
                        "title": "yes",
                    }
                }
            ],
            autospec=True,
        ) as _mock:
            pBExport.updateExportedBib(testBibName, overwrite=True)
        with open(testBibName) as f:
            self.assertEqual(
                f.read().replace(" ", "").replace("\n", ""),
                sampleTxt.replace("me2", "me et al").replace(" ", "").replace("\n", ""),
            )
        pBExport.rmBackupCopy(testBibName)

    def test_exportAll(self):
        """Test of exportAll"""
        testBibName = self.testBibName
        sampleList = [
            {"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'},
            {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'},
        ]
        sampleTxt = (
            '@Article{empty,\nauthor="me",\ntitle="no"\n}\n'
            + '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
        )
        with patch(
            "physbiblio.database.Entries.fetchCursor",
            return_value=sampleList,
            autospec=True,
        ) as _curs:
            pBExport.exportAll(testBibName)
        with open(testBibName) as f:
            self.assertEqual(f.read(), sampleTxt)

    def test_exportForTexFile(self):
        """test exportForTexFile function with a fake tex and database"""
        testBibName = self.testBibName
        testTexName = self.testTexName
        texString = (
            "\cite{empty,prova., empty2+}\citep{empty2+}"
            + "\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
        )
        with open(testTexName, "w") as f:
            f.write(texString)
        with open(testTexName) as f:
            self.assertEqual(f.read(), texString)
        sampleList = [
            {
                "bibkey": "empty",
                "bibtex": '@Article{empty,\n        author = "me",\n         '
                + 'title = "{no}",\n}',
            },
            {
                "bibkey": "empty2+",
                "bibtex": '@Article{empty2+,\nauthor="me2",\ntitle="yes"\n}',
            },
        ]

        self.assertFalse(os.path.exists(testBibName))
        with patch(
            "physbiblio.database.CatsEntries.insert", return_value=True, autospec=True
        ) as _ceins, patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [
                    {
                        "bibkey": "empty",
                        "bibtexDict": {},
                        "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}',
                    }
                ],
                [],
                [
                    {
                        "bibkey": "Gariazzo:2015rra",
                        "bibtexDict": {},
                        "bibtex": "@article{Gariazzo:2015rra,\nauthor= "
                        + '"Gariazzo, S. and others",\ntitle='
                        + '"{Light sterile neutrinos}",\n}',
                    }
                ],
                [
                    {
                        "bibkey": "empty2+",
                        "bibtexDict": {},
                        "bibtex": '@Article{empty2+,\nauthor="me2",\ntitle="yes"\n}',
                    }
                ],
                [],
                [
                    {
                        "bibkey": "Gariazzo:2015rra",
                        "bibtexDict": {},
                        "bibtex": "@article{Gariazzo:2015rra,\nauthor= "
                        + '"Gariazzo, S. and others",\ntitle='
                        + '"{Light sterile neutrinos}",\n}',
                    }
                ],
                [],
                [],
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert",
            side_effect=[
                "@article{Gariazzo:2015rra,\nauthor= "
                + '"Gariazzo, S. and others",\ntitle='
                + '"{Light sterile neutrinos}",\n}',
                "@article{Gariazzo:2015rra,\nauthor= "
                + '"Gariazzo, S. and others",\ntitle='
                + '"{Light sterile neutrinos}",\n}',
                "",
            ],
            autospec=True,
        ) as _mock:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, overwrite=True, autosave=False
            )
        self.assertEqual(
            output[0],
            ["empty", "prova.", "empty2+", "Gariazzo:2015rra", "Gariazzo:2017rra"],
        )  # requiredBibkeys
        self.assertEqual(
            output[1], ["prova.", "Gariazzo:2015rra", "Gariazzo:2017rra"]
        )  # missing
        self.assertEqual(output[2], ["Gariazzo:2015rra"])  # retrieved
        self.assertEqual(output[3], ["Gariazzo:2017rra"])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {"prova.": "Gariazzo:2015rra"})  # newKeys
        self.assertEqual(output[6], 2)  # warnings
        self.assertEqual(output[7], 5)  # total
        self.assertTrue(os.path.exists(testBibName))
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{empty,\n        author = "me",\n         title = '
            + '"{no}",\n}\n\n',
            '@Article{prova.,\n        author = "Gariazzo, S. and others",'
            + '\n         title = "{Light sterile neutrinos}",'
            + "\n}\n\n",
            '@Article{empty2+,\n        author = "me2",\n         title = '
            + '"{yes}",\n}\n\n',
            "@Article{Gariazzo:2015rra,\n        author = "
            + '"Gariazzo, S. and others",\n         title = '
            + '"{Light sterile neutrinos}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testTexName, "a") as f:
            f.write("\cite{newcite}")
        with patch(
            "physbiblio.database.CatsEntries.insert", return_value=True, autospec=True
        ) as _ceins, patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [],
                [],
                [],
                [
                    {
                        "bibkey": "newcite",
                        "bibtexDict": {},
                        "bibtex": '@article{newcite,\nauthor= "myself",\ntitle='
                        + '"{some paper}",\n}',
                    }
                ],
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert",
            side_effect=[
                "",
                '@article{newcite,\nauthor= "myself",\ntitle=' + '"{some paper}",\n}',
            ],
            autospec=True,
        ) as _mock:
            output = pBExport.exportForTexFile(testTexName, testBibName, autosave=False)
        self.assertEqual(output[0], ["Gariazzo:2017rra", "newcite"])  # requiredBibkeys
        self.assertEqual(output[1], ["Gariazzo:2017rra", "newcite"])  # missing
        self.assertEqual(output[2], ["newcite"])  # retrieved
        self.assertEqual(output[3], ["Gariazzo:2017rra"])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 1)  # warnings
        self.assertEqual(output[7], 6)  # total
        self.assertTrue(os.path.exists(testBibName))
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{empty,\n        author = "me",\n         title = '
            + '"{no}",\n}\n\n',
            '@Article{prova.,\n        author = "Gariazzo, S. and others"'
            + ',\n         title = "{Light sterile neutrinos}",\n}\n\n',
            '@Article{empty2+,\n        author = "me2",\n         title = '
            + '"{yes}",\n}\n\n',
            "@Article{Gariazzo:2015rra,\n        author = "
            + '"Gariazzo, S. and others",\n         title = '
            + '"{Light sterile neutrinos}",\n}\n\n',
            '@Article{newcite,\n        author = "myself",'
            + '\n         title = "{some paper}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testTexName, "w") as f:
            f.write("\cite{newcite:NOW18}")
        with patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [
                    {
                        "bibkey": "newcite:now18",
                        "bibtexDict": {},
                        "bibtex": '@article{newcite:now18,\nauthor= "myself",\ntitle='
                        + '"{some paper}",\n}',
                    }
                ]
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, overwrite=True, autosave=False
            )
        self.assertEqual(output[0], ["newcite:NOW18"])  # requiredBibkeys
        self.assertEqual(output[1], [])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], [])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 0)  # warnings
        self.assertEqual(output[7], 1)  # total
        self.assertTrue(os.path.exists(testBibName))
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{newcite:NOW18,\n        author = "myself",\n         '
            + 'title = "{some paper}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testTexName, "w") as f:
            f.write("\cite{newcite:NOW18}\cite{bib1}\cite{bib2}")
        bibtex1 = '@Article{newcite,\nauthor="S. Gariazzo",\ntitle=' + '"{newtitle}"\n}'
        bibtex2 = (
            '@article{bib1,\nauthor="SG",\ntitle=' + '"{Light sterile neutrinos}",\n}'
        )
        bibtex3 = '@Article{bib2,\nauthor="me",\ntitle="title"\n}'
        with patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [
                    {
                        "bibkey": "newcite:now18",
                        "bibtexDict": bibtexparser.loads(bibtex1).entries[0],
                        "bibtex": bibtex1,
                    }
                ],
                [
                    {
                        "bibkey": "bib1",
                        "bibtexDict": bibtexparser.loads(bibtex2).entries[0],
                        "bibtex": bibtex2,
                    }
                ],
                [
                    {
                        "bibkey": "bib2",
                        "bibtexDict": bibtexparser.loads(bibtex3).entries[0],
                        "bibtex": bibtex3,
                    }
                ],
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, autosave=False, updateExisting=True
            )
        self.assertEqual(output[0], ["bib1", "bib2"])  # requiredBibkeys
        self.assertEqual(output[1], [])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], [])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 0)  # warnings
        self.assertEqual(output[7], 3)  # total
        self.assertTrue(os.path.exists(testBibName))
        self.maxDiff = None
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{newcite:NOW18,\n        author = "S. Gariazzo",'
            + '\n         title = "{newtitle}",\n}\n\n',
            '@Article{bib1,\n        author = "SG",\n         title = '
            + '"{Light sterile neutrinos}",\n}\n\n',
            '@Article{bib2,\n        author = "me",\n         title = '
            + '"{title}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testTexName, "w") as f:
            f.write("\cite{newcite:NOW18}\cite{bib1}")
        bibtex1 = (
            '@Article{newcite:now18,\nauthor="S. Gariazzo",\ntitle=' + '"{newtitle}"\n}'
        )
        bibtex2 = (
            '@article{bib1,\nauthor="SG",\ntitle=' + '"{Light sterile neutrinos}",\n}'
        )
        with patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [
                    {
                        "bibkey": "newcite:now18",
                        "bibtexDict": bibtexparser.loads(bibtex1).entries[0],
                        "bibtex": bibtex1,
                    }
                ],
                [
                    {
                        "bibkey": "bib1",
                        "bibtexDict": bibtexparser.loads(bibtex2).entries[0],
                        "bibtex": bibtex2,
                    }
                ],
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, autosave=False, removeUnused=True
            )
        self.assertEqual(output[0], [])  # requiredBibkeys
        self.assertEqual(output[1], [])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], [])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 0)  # warnings
        self.assertEqual(output[7], 2)  # total
        self.assertTrue(os.path.exists(testBibName))
        self.maxDiff = None
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{newcite:NOW18,\n        author = "S. Gariazzo",'
            + '\n         title = "{newtitle}",\n}\n\n',
            '@Article{bib1,\n        author = "SG",\n         '
            + 'title = "{Light sterile neutrinos}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testTexName, "w") as f:
            f.write("\cite{newcite}")
        bibtex1 = '@Article{newcite,\nauthor="S. Gariazzo",' + '\ntitle="{title}"\n}'
        with patch(
            "physbiblio.database.Entries.getByBibtex",
            side_effect=[
                [
                    {
                        "bibkey": "newcite",
                        "bibtexDict": bibtexparser.loads(bibtex1).entries[0],
                        "bibtex": bibtex1,
                    }
                ]
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, autosave=False, overwrite=True
            )
        self.assertEqual(output[0], ["newcite"])  # requiredBibkeys
        self.assertEqual(output[1], [])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], [])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 0)  # warnings
        self.assertEqual(output[7], 1)  # total
        self.assertTrue(os.path.exists(testBibName))
        self.maxDiff = None
        with open(testBibName) as f:
            newTextBib = f.read()
        for t in [
            "%file written by PhysBiblio\n",
            '@Article{newcite,\n        author = "S. Gariazzo",'
            + '\n         title = "{title}",\n}\n\n',
        ]:
            self.assertIn(t, newTextBib)

        with open(testBibName, "w") as f:
            f.write(
                "%file written by PhysBiblio\n"
                + '@Article{empty,\n    author = "me",\n         title = '
                + '"{no}",\n}\n\n'
                + '@Article{prova,\n  author = "Gariazzo, S. and others",'
                + '\n         title = "{Light sterile neutrinos}",'
                + "\n\n"
                + '@Article{empty2,\n   author = "",\n         title = '
                + '"{yes}",\n}\n\n'
                + "@Article{Gariazzo:2015rra,\n        author = "
                + '"Gariazzo, S. and others",\n         %title = '
                + '"{Light sterile neutrinos}",\n}\n\n'
            )
        with patch(
            "physbiblio.database.Entries.getByBibtex", autospec=True
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName,
                testBibName,
                autosave=False,
                removeUnused=True,
                updateExisting=True,
            )
        self.assertEqual(output[0], ["newcite"])  # requiredBibkeys
        self.assertEqual(output[1], ["newcite"])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], ["newcite"])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 1)  # warnings
        self.assertEqual(output[7], 1)  # total
        self.assertTrue(os.path.exists(testBibName))
        with open(testBibName) as f:
            newTextBib = f.read()
        self.assertEqual(newTextBib, "%file written by PhysBiblio\n")

        os.remove(testBibName)
        with patch("logging.Logger.error") as _er, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(testTexName, testBibName, autosave=False)
            _er.assert_any_call("Cannot read file %s.\nCreating one." % testBibName)
        self.assertEqual(len(output), 8)
        self.assertTrue(os.path.exists(testBibName))
        with patch("logging.Logger.exception") as _ex, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            self.assertFalse(
                pBExport.exportForTexFile(
                    testTexName, "/surely/not/existing/path.bib", autosave=False
                )
            )
            _ex.assert_called_once_with(
                "Cannot create file /surely/not/existing/path.bib!"
            )

        texString = (
            "\cite{someA&A...123,prova., empty2+}\citep{empty2+}"
            + "\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
        )
        with open(testTexName, "w") as f:
            f.write(texString)
        with patch(
            "physbiblio.database.Entries.getByBibtex",
            return_value=[
                {
                    "bibkey": "newcite:now18",
                    "bibtexDict": bibtexparser.loads(bibtex1).entries[0],
                    "bibtex": bibtex1,
                }
            ],
            autospec=True,
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(testTexName, testBibName, autosave=False)
        self.assertEqual(
            output[0],
            [
                "someA&A...123",
                "prova.",
                "empty2+",
                "Gariazzo:2015rra",
                "Gariazzo:2017rra",
            ],
        )  # requiredBibkeys
        self.assertEqual(output[1], [])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], [])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 0)  # warnings
        self.assertEqual(output[7], 5)  # total

        with open(testBibName, "w") as f:
            f.write(
                "%file written by PhysBiblio\n"
                + '@Article{empty,\n    author = "me",\n         title = '
                + '"{no}",\n}\n\n'
                + '@Article{prova,\n  author = "Gariazzo, S. and others",'
                + '\n         title = "{Light sterile neutrinos}",'
                + "}\n\n"
                + '@Article{empty2,\n   author = "boh",\n         title = '
                + '"{yes}",\n}\n\n'
                + "@Article{Gariazzo:2015rra,\n        author = "
                + '"Gariazzo, S. and others",\n         title = '
                + '"{Light sterile neutrinos}",\n}\n\n'
            )
        with open(testTexName, "w") as f:
            f.write(
                "\cite{prova,empty2}\citep{empty}"
                + "\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
            )
        with patch(
            "physbiblio.database.Entries.getByBibtex", return_value=[], autospec=True
        ) as _getbbibt, patch(
            "physbiblio.database.Entries.loadAndInsert", return_value=[], autospec=True
        ) as _lai:
            output = pBExport.exportForTexFile(
                testTexName, testBibName, autosave=False, reorder=True
            )
        self.assertEqual(output[0], ["Gariazzo:2017rra"])  # requiredBibkeys
        self.assertEqual(output[1], ["Gariazzo:2017rra"])  # missing
        self.assertEqual(output[2], [])  # retrieved
        self.assertEqual(output[3], ["Gariazzo:2017rra"])  # notFound
        self.assertEqual(output[4], [])  # unexpected
        self.assertEqual(output[5], {})  # newKeys
        self.assertEqual(output[6], 1)  # warnings
        self.assertEqual(output[7], 5)  # total
        with open(testBibName) as f:
            newTextBib = f.readlines()
        useful = [l for l in newTextBib if "@" in l]
        for i, e in enumerate(["empty", "empty2", "Gariazzo:2015rra", "prova"]):
            self.assertIn(e, useful[i])


if __name__ == "__main__":
    unittest.main()
