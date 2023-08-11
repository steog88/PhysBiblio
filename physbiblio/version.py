__version__ = "2.1.0"
__version_date__ = "11/08/2023"

__recent_changes__ = """<br>* search by inspire ID<br>
* search NULL fields<br>
* search noUpdate bibs<br>
* toggle noUpdate from context menu<br>
* shortcut Ctrl+Enter to quickly accept edit dialogs<br>
* fixes with triggered signal<br>
* store query for each tab separately<br>
* fix in merge function<br>
* fix when storing last query from tab<br>
* DB functions checkDuplicates (no quick access to it yet from command line nor GUI) and fetchByField in Entries<br>
* fix None in various fields when running cleanFields<br>
* fix messing up when one of the previous searches had more lines than the desider one<br>
* improved search by key in database (exact match of bibkey or one of the old_keys is required to match)<br>
"""
