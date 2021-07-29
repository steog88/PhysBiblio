__version__ = "1.8.1"
__version_date__ = "29/07/2021"

__recent_changes__ = """<br><br><b>New features / improvements:</b><br>
* New 'citations' command to update citation counts without the GUI<br>
* search records by "No type"<br>
* add/remove marks or set/unset types for selections of entries<br>
* frequent searches open automatically in a new tab<br>
* possibility to open lists from categories/experiments in new tab<br>
* possibility to open search/replace results in new tab from search form<br>
* navigate tabs with Ctrl+Tab and Ctrl+Shift+Tab (may have some problems)<br>
* small change in how database.Entries.completeFetched manages an almost empty 'published' field<br>
* improvements to argParser tests<br>
* improvements to database module<br>
* improvements to inspireStats module<br>
* improvements to gui.mainWindow module<br>
* function to match valid arxiv number<br>
<br><b>Bug fixes:</b><br>
* fix crash when the log file is missing and cannot be created at the beginning of the execution<br>
* fixing bug with 'Modify' bibtex entry and citation counts<br>
* fixing bug with renaming pdf folders when target folder already exists<br>
* fixing bug with "Reload bibtex" updates from INSPIRE<br>
* attempt to fix sync problem in WriteStream thanks to simple buffering system<br>
* (1.8.1) fixed list of new features at startup in case of subcategories in CHANGELOG<br>
"""
