# [PhysBiblio](https://github.com/steog88/physBiblio)
Bibliography manager in Python  
by S. Gariazzo (stefano.gariazzo@gmail.com)

PhysBiblio is a program that helps to manage bibliography, with a particular focus on High Energy Physics tools.  
It is written in Python, it uses PySide for the graphical interface and Sqlite for the database management.

## 1. Getting started

### **WARNING:**
PhysBiblio has been intensively tested only on Ubuntu (14.04LTS to 17.10 versions) and Sabayon Linux, using `python` version `2.7+` and `3.5+`.  
It should work equally well in other operating systems or with different python versions, but it has not been tested.  
In any case, several bugs are surely still present and the program may freeze or crash unexpectedly.
Please report any bug that you find [here](https://github.com/steog88/physBiblio/issues).

### Installation
To install PhysBiblio into your computer, the easiest way is to use `pip` and the official python repositories.
If you do not have `pip` installed in your system, see [this page](https://pip.pypa.io/en/stable/installing/).

#### Python2
If you use `python 2+`, simply use (system-wide install)
```
sudo pip install pyside physbiblio
```
or (user only install)
```
pip install --user pyside physbiblio
```
However, I find that installing `pyside` via `pip` can bring some amount of trouble.
If you are not lucky with the previous command, you may want to install `PySide` via package manager and then use `pip` only for `PhysBiblio`.
The easiest way is then (Ubuntu):
```
sudo apt install python-pyside
sudo pip install physbiblio
```

#### Python3
For `python 3+`, the situation is complicated by the fact that
the series `1.x` of `PySide` available through `pip` does not support Python versions newer than 3.5+, so you cannot install `PySide` with `pip3` if you have a newer version than the 3.5.
This can be solved again if you install `PySide` with the package manager of your system, for example in Ubuntu using
```
sudo apt install python3-pyside
sudo pip3 install physbiblio
```

#### Conda
Here you find a list of instructions to install and run `PhysBiblio` using `conda` and related commands.
It is convenient to use a dedicated environment and python 2+, as `PySide` has problems with newer python versions.
```
conda create --name physbiblio python=2
conda activate physbiblio
conda install PySide
pip install physbiblio
```
At this point, the installation is complete.
To launch the main program correctly, once you have activated the appropriate `conda` environment (`conda activate physbiblio`), use:
```
python PhysBiblio
```
(if you omit `python`, it will try to use the default Python installation instead of the Conda one, and fail due to missing libraries)

#### Additional info
At this point, `PhysBiblio` will be installed in your computer, in Linux it will be in some folder like `/usr/bin/`, `/usr/local/bin/` or `/your/user/folder/.local/bin/`.
You can find out the location where the package is installed with
```
pip show -f physbiblio
```
The primary director is under `Location`, you can combine with the information provided by the list of `Files`.

To upgrade from a previously installed version, add the option `-U` or `--upgrade` when running `pip`, for example:
```
sudo pip install -U physbiblio
```
or
```
pip install -U physbiblio
```

### Test that everything works
Once you have installed the software, you may want to spend few minutes to run the test suite
and check that everything works.  
The test suite is available through the same `PhysBiblio` executable with the command `test`:
`PhysBiblio test`
If this does not work, check that the global variable PATH is correctly configured.
The other possibility is to point to the PhysBiblio script directly, using one of the following commands:
```
/path/to/PhysBiblio test
python /path/to/PhysBiblio test
python3 /path/to/PhysBiblio test
```

The entire suite of tests will check that all the functions work properly and should complete without errors and failures in a few minutes, depending on the internet connection speed.  
A failure may be due to missing packages or missing internet connection (or bugs).
If you are not sure which is your case, please ask help  [here](https://github.com/steog88/physBiblio/issues).

### Usage
To run the program, execute `PhysBiblio` that have been installed.
By default it will run with `python2.x`.
You can choose a specific `python` version running it explicitely via command line, for example you may select `python3` with
```
python3 /path/to/PhysBiblio
```

You may want to create a menu shortcut to PhysBiblio.
In Ubuntu, you can simply create a new file `/your/home/.local/share/applications/PhysBiblio.desktop` with the editor of your choice, and insert the following lines:
```
[Desktop Entry]
Type=Application
Exec=/path/to/PhysBiblio
Icon=/path/to/physbiblio/icon.png
Name=PhysBiblio
Path[$e]=/path/to/PhysBiblio/
```
The icon may be located in `/usr/local/physbiblio/icon.png` or `/usr/physbiblio/icon.png`.

### Default settings
When you first open PhysBiblio, you will need to set up some configuration parameters.  
In particular, if you do not correctly set the web browser and the PDF reader, some features may not work when using the command line.

### Dependencies
PhysBiblio depends on several python packages:
* sqlite3 (for the database)
* pyside (for the graphical interface)
* appdirs (default paths)
* argparse (arguments from command line)
* bibtexparser (to manage bibtex entries)
* dictdiffer (show differences between dictionaries)
* feedparser (to deal with arXiv data)
* matplotlib (to do some plots)
* outdated (check if new versions are available)
* pylatexenc (conversion of accented and other utf-8 characters to latex commands)
* pymarc (to deal with arXiv data)
* pyoai	(for massively harvesting the INSPIRE-HEP database)
* requests (download json pages)
* six (compatibility between python2 and python3)
* unittest2+mock (python2.x) / unittest (python3.x) (for testing the methods and functions)

## 2. Features
PhysBiblio has some nice features which may help to manage the bibliography. Some of them are listed here.

### Profiles
You may manage different profiles, each with different settings and independent databases.
It may be useful if you want to maintain separate activities or collections independently one of the other.

### Import
The default import interface can fetch and download information from [INSPIRE-HEP](http://inspirehep.net/).
The advanced import can also work with [arXiv](www.arxiv.org), [dx.doi.org](dx.doi.org), [ISBN2bibtex](http://www.ebook.de/de/tools/isbn2bibtex).  
If an arXiv identifier is present, you can download the paper abstract from arXiv (there is an option to do this by default).

### Export
It is very easy to export some entries into a `.bib` file.
You can export the entire bibtex database, a selection or let the program export only the entries that you need to compile a given `.tex` file.
All the functions are available in the `File` menu.

### Update
PhysBiblio can use [INSPIRE-HEP](http://inspirehep.net/) information in order to update the information of recently published entries.  
You will find very easy to keep your database up-to-date with journal info, you just have to occasionally run the `update` function on single papers or on the whole table.  
You can use this feature also to update the content of an existing `.bib` file.

**Please note** that the use of the `update` functions on long lists of entries is discouraged by the maintainers of INSPIRE-HEP, as it creates a lot of load on the server.
See [here](#inspire-oai) for an alternative and much less demanding method.

### Categories
The default database contains two categories: `Main` and `Tags`.
You can add subcategories in a tree structure and filter your bibtex entries according to the classification.

### Experiments
Separately from categories, you can organize papers published by experiments or collaborations and insert links to the experiment web page.
When you assign a paper to an experiment, it will be classified also in the same categories of the experiment itself.

### PDF
A "Download from arXiv" feature is present for all the papers with an arXiv identifier.  
For the other papers, you can manually assign a PDF that you have separately downloaded and it will be stored in a subfolder.  
You will not need to know where it is saved, because you will access it from the program, but in case you can use the function to copy th PDF wherever you want.

### Marks
You can mark the entries to be able to easily see if they are good/bad, to notice which ones you need to read or the most interesting ones.

### Search and replace
Entries in the database can be searched using different field combinations, their associated categories or experiments, marks, entry types (reviews, proceedings, lectures, ...).

The search form should be easy to understand (if not, help me to improve it and submit an [issue](https://github.com/steog88/physBiblio/issues).
You can play with the logical operators and add more fields if necessary.

A pretty powerful "search and replace" function, which can use regular expressions (regex), is also implemented.  
The search function is the same as in the search only case, but now you cannot select the limit and offset.  
The replace fields let you select from which field you want to take the input and in which one you want to store the new string.  
An additional filtering is performed when trying to match the regular expression. No match, no action.

Two (regex) search and replace examples:

* To move the letter from "volume" to "journal" for the journals of the "Phys. Rev." series, use:
  - from: "published", `(Phys. Rev. [A-Z]{1})([0-9]{2}).*`;
  - To 1: "journal", `\1`;
  - To 2: "volume", `\2`.
  
  To match "Phys. Rev. X" you will have to change `[0-9]{2}` to `[0-9]{1}` in the pattern string.  
  If you want to match "J. Phys. G", change the first part of the pattern string accordingly (`J. Phys. [A-Z]{1}`).

* To remove the first two numbers from "volume" field of JHEP/JCAP entries, use:
  - filter using ["jhep" or "jcap"] ("add another line" and use "OR") in "bibtex";
  - replace `([0-9]{2})([0-9]{2})` in "volume" with `\2`.

### INSPIRE-OAI
INSPIRE-HEP has a dedicated interface for massive harvesting, see [this page](http://inspirehep.net/info/hep/api).  
In order to avoid heavy traffic on the server when using the `update` functions on a long list of entries, you should rely on the OAI functions.
Basically instead of looking for each single entry, the code will download the information of all the entries modified in a given time interval and use what is needed in the local database.  
In this way, the amount of data traffic is higher, but the server-side load for INSPIRE-HEP is much more sustainable.

The easiest way to do this (in Linux) is to use a cron job that will run daily or weekly and the command `PhysBiblio daily` or `PhysBiblio weekly` (see also [3. Command line usage](#3-command-line-usage)).  
The `daily` (`weekly`) routines will download the updates of the last day (week) from the INSPIRE-HEP database and update the local database.

To set your cron job, use `crontab -e` and add one of the following lines:
```
0 7 * * * /path/to/PhysBiblio daily > /path/to/log_daily_`date "+\%y\%m\%d"`.log 2>&1
0 7 * * sat /path/to/PhysBiblio weekly > /path/to/log_weekly_`date "+\%y\%m\%d"`.log 2>&1
```
The syntax is simple: the `daily` (`weekly`) script will run every day (every saturday) at 7:00 and save a logfile in the desired folder.

You may then check the bottom of the logfile to see the modified entries and scroll the entire the content if you want to see the complete list of modifications.

You can also use the more generic `PhysBiblio dates [date1[, date2]]` command, which enables you to fetch the content between the two given dates (which must be in the format `yyyy-mm-dd`).
If not given, the default dates are the same as for the `daily` command.

## 3. Command line usage
Some functions are available also as simple command line instructions,
so they can be included in any non-graphical script.

The usage is simple:
```
/path/to/PhysBiblio <command> [options]
```

The list of available commands includes:
* `gui`: run the graphical interface (default if no options are used).
* `test`: execute the test suite.
* `clean`: process all the bibtex entries in the database to remove bad characters and reformat them.
* `cli`: internal command line interface to work with internal commands. Mainly intended for developing.
* `daily`: see [here](#inspire-oai).
* `dates`: see [here](#inspire-oai).
* `export`:
	export all the bibtex entries in the database, creating a file with the given `filename`.
	If already existing, the file will be overwritten.
* `tex`:
	read one or more `.tex` files,
	scanning for `\cite` or similar commands, and generate a single `.bib` file
	with the required bibtex entries to compile the set of `.tex` files.
	If they are in the local database, the bibtexs are just copied into the output file,
	otherwise the script will connect to INSPIRE-HEP to download the entries,
	which will be stored in the database and in the output file.
	If `outputfile` exists, a backup copy will be created.
* `update`:
	for each of the entries in the database, if required, get updated information from INSPIRE-HEP (publication info or title updates, for example).
	You are encouraged not to use this function if you have a large database, see [here](#inspire-oai) instead.
* `weekly`: see [here](#inspire-oai).

The best ways to know how to use the various sub-commands and options are
```
/path/to/PhysBiblio -h
/path/to/PhysBiblio <command> -h
```

## 4. Data paths
PhysBiblio now saves data, by default, in the directories specified by the `appdirs` package using `user_config_dir` and `user_data_dir`.
Both the directories are indicated at the beginning when launching `PhysBiblio` via command line.

The stored configuration includes a `profiles.db` file, containing the information on the existing profiles.

The stored data include:
* a `pdf/` subfolder, with the PDF for all the papers. This is usually shared among all the profiles, unless you set different paths in the configuration of each profile;
* sets of `.db` and `.log` files, which contain the database and an error log for each profile.

You can change some of the paths and file names in the configuration.
Please note that changing the configuration **will not move** the existing files into the new locations.

## 5. Acknowledgments
Icons adopted in the GUI are mainly from the [Breeze-icons](https://github.com/KDE/breeze-icons) theme, from [KDE](https://www.kde.org/).
