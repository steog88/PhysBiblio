#!/usr/bin/env python
"""Test file for the physbiblio.argParser module.

This file is part of the physbiblio package.
"""
import sys
import traceback

if sys.version_info[0] < 3:
    import unittest2 as unittest
else:
    import unittest

try:
    import physbiblio
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestPackage(unittest.TestCase):
    """Test package properties"""

    def test_package(self):
        """Test that the physbiblio package has some basic properties"""
        self.assertTrue(hasattr(physbiblio, "__author__"))
        self.assertTrue(hasattr(physbiblio, "__email__"))
        self.assertTrue(hasattr(physbiblio, "__version__"))
        self.assertTrue(hasattr(physbiblio, "__version_date__"))
        self.assertTrue(hasattr(physbiblio, "__all__"))
        self.assertTrue(hasattr(physbiblio, "__recent_changes__"))


if __name__ == "__main__":
    unittest.main()
