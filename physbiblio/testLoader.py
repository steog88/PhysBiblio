"""Adapting the code from setuptools.command.test:ScanningLoader,
which is not finding tests in python3.

This file is part of the physbiblio package.
"""
import sys
if sys.version_info[0] < 3:
	from unittest2 import TestLoader
else:
	from unittest import TestLoader

from pkg_resources import resource_listdir, resource_exists


class PBScanningLoader(TestLoader):
	"""Custom ScanningLoader implementation to be used
	when calling `setup.py test`
	"""

	def __init__(self):
		TestLoader.__init__(self)
		self._visited = set()

	def loadTestsFromModule(self, module, pattern=None):
		"""Return a suite of all tests cases contained in the given module
		If the module is a package, load tests from all the modules in it.
		If the module has an ``additional_tests`` function, call it and add
		the return value to the tests.
		"""
		if module in self._visited:
			return None
		self._visited.add(module)

		tests = []
		tests.append(TestLoader.loadTestsFromModule(self, module))

		if hasattr(module, "additional_tests"):
			tests.append(module.additional_tests())

		if hasattr(module, '__path__'):
			if "tests" in resource_listdir(module.__name__, ''):
				tests.append(self.loadTestsFromName(
					module.__name__ + '.' + "tests"))
			for file in resource_listdir(module.__name__, ''):
				if file != "tests" or file != "tmp":
					continue
				elif file.endswith('.py') and file != '__init__.py':
					submodule = module.__name__ + '.' + file[:-3]
				else:
					if resource_exists(module.__name__, file + '/__init__.py'):
						submodule = module.__name__ + '.' + file
					else:
						continue
				tests.append(self.loadTestsFromName(submodule))

		if len(tests) != 1:
			return self.suiteClass(tests)
		else:
			return tests[0] # don't create a nested suite for only one return
