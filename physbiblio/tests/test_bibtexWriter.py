#!/usr/bin/env python
"""Test file for the physbiblio.bibtexWriter module.

This file is part of the physbiblio package.
"""
import sys
import traceback

import bibtexparser

if sys.version_info[0] < 3:
    import unittest2 as unittest
else:
    import unittest

try:
    from physbiblio.bibtexWriter import *
    from physbiblio.config import pbConfig
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.long, "Long tests")
@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.exception")
class TestWebImportMethods(unittest.TestCase):
    """Test the functions that writes bibtexs."""

    def test_properties(self, *args):
        """Test properties of the pbWriter object"""
        self.assertIsInstance(pbWriter, PBBibTexWriter)
        self.assertIsInstance(pbWriter, BibTexWriter)
        self.assertEqual(pbWriter._max_field_width, 13)
        # order of fields in output
        self.assertEqual(
            pbWriter.display_order,
            [
                "author",
                "collaboration",
                "title",
                "booktitle",
                "publisher",
                "journal",
                "volume",
                "year",
                "pages",
                "russian",
                "archiveprefix",
                "primaryclass",
                "eprint",
                "doi",
                "reportNumber",
            ],
        )
        self.assertEqual(
            pbWriter.bracket_fields,
            [
                "title",
                "booktitle",
                "www",
                "note",
                "abstract",
                "comment",
                "article",
                "url",
            ],
        )
        self.assertEqual(
            pbWriter.excluded_fields, ["adsnote", "adsurl", "slaccitation"]
        )
        self.assertEqual(pbWriter.order_entries_by, None)
        self.assertEqual(pbWriter.comma_first, False)

    def test_bibtexWrite(self, *args):
        """Test _entry_to_bibtex"""
        basicEntry = {
            "ID": "test",
            "ENTRYTYPE": "article",
            "author": "me",
            "title": "My title",
        }
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [basicEntry]
        self.assertEqual(
            pbWriter.write(db).strip(),
            '@Article{test,\n        author = "me",\n         '
            + 'title = "{My title}",\n}',
        )
        entry = dict(basicEntry)
        entry["ENTRYTYPE"] = "proceeding"
        entry["eprint"] = "1721"
        entry["slaccitation"] = "1721"
        entry["title"] = "{my title}"
        db.entries = [entry]
        self.assertEqual(
            pbWriter.write(db).strip(),
            '@Proceeding{test,\n        author = "me",\n         '
            + 'title = "{my title}",\n        eprint = "1721",\n}',
        )
        entry = dict(basicEntry)
        entry["ENTRYTYPE"] = "custom"
        entry["myfield"] = "abcd"
        entry["journal"] = "JCAP"
        entry["title"] = "{My} title"
        db.entries = [entry]
        self.assertEqual(
            pbWriter.write(db).strip(),
            '@Custom{test,\n        author = "me",\n         '
            + 'title = "{{My} title}",\n       journal = "JCAP",'
            + '\n       myfield = "abcd",\n}',
        )


if __name__ == "__main__":
    unittest.main()
