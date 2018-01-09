# PhysBiblio
Bibliography manager in Python
by S. Gariazzo (stefano.gariazzo@gmail.com)

PhysBiblio is a program that helps to manage bibliography, with a particular focus on High Energy Physics tools.
It is written in Python, it uses PySide for the graphical interface and Sqlite for the database management.

## 1. Getting started

### Dependencies
PhysBiblio depends on several python packages:
* sqlite3 (for the database)
* pyside (for the graphical interface)
* pyoai	(for massively harvesting the INSPIRE-HEP database)
* bibtexparser (to manage bibtex entries)
* feedparser (to deal with arXiv data)
* pymarc (to deal with arXiv data)

Within Ubuntu, you should be able to install all the required packages using:
```
sudo apt install python-pyside pip
sudo pip install git+http://github.com/infrae/pyoai
sudo pip install bibtexparser
sudo pip install feedparser
sudo pip install pymarc
```

### Installation and usage
To install PhysBiblio into your computer, go to [PhysBiblio](https://github.com/steog88/physBiblio), clone the git repository or download the .zip archive and uncompress it into the folder you prefer.
To run the program, execute the main.py file that you will find in the newly created folder.
You may launch it by double-clicking or via command line, using `./main.py` or `python main.py`.

In Ubuntu, you may want to create a shortcut to PhysBiblio.
To do so, you can simply create a new file /your/home/.local/share/applications/PhysBiblio.desktop with the editor of your choice, which must contain the following lines:
```
[Desktop Entry]
Exec=/path/to/PhysBiblio/main.py
Icon=/path/to/PhysBiblio/physbiblio/gui/images/icon.png
Name=PhysBiblio
Path[$e]=/path/to/PhysBiblio/
```

### Default settings
When you first open PhysBiblio, you will need to set up some configuration parameters.
In particular, if you do not correctly set the web browser and the PDF reader some features may not work.

**WARNING:**
PhysBiblio has been intensively tested only on Ubuntu (14.04LTS to 17.10 versions), using python up to version 2.7.14.
It may work equally well in other operating systems or with different python versions, but it has not been tested.
In any case, several bugs are still present and the program may freeze or crash unexpectedly.

## 2. Features
PhysBiblio has some nice features which may help to manage the bibliography. Some of them are listed here.

### Import
The default import interface can fetch and download information from INSPIRE-HEP.
The advanced import can also work with [arXiv](www.arxiv.org), [dx.doi.org](dx.doi.org), [ISBN2bibtex](http://www.ebook.de/de/tools/isbn2bibtex).

### Export
It is very easy to export some entries into a `.bib` file. You can export the entire bibtex database, a selection or let the program export only the entries that you need to compile a given `.tex` file.

### Update
PhysBiblio can use INSPIRE-HEP information in order to update the information of recently published entries.
You will find very easy to keep your database up-to-date with journal info, you just have to occasionally run the Update function on single papers or on the whole table.
You can use this feature also to update the content of an existing `.bib` file.

### Categories
The default database contains two categories: `Main` and `Tags`. You can add subcategories in a tree structure and filter your bibtex entries according to the classification.

### Experiments
Separately from categories, you can organize papers published by experiments or collaborations and insert links to the experiment web page.
When you assign a paper to an experiment, it will be classified also in the same categories of the experiment itself.

### Profiles
You may manage different profiles, each with different settings and independent databases.
It may be useful if you want to maintain separate activities or collections independently one of the other.

### PDF
A "Download from arXiv" feature is present for all the papers with an arXiv identifier.
For the other papers, you can manually assign a PDF that you have separately downloaded and it will be stored in a subfolder.
You will not need to know where it is saved, because you will access it from the program.

## 3. Data paths
PhysBiblio saves data, by default, in a `data/` subfolder of its main path.

The stored data include:
* a `profiles.dat` file, containing the information on the existing profiles;
* a `pdf/` subfolder, with the PDF for all the papers. This is shared for all the profiles unless you set different paths in the configuration files of each profile;
* sets of `.cfg`, `.db` and `.log` files, which contain the configuration, the database and an error log for each profile.

You can change some of the paths in the configuration.
Please note that changing the configuration will not move the existing files into the new locations.

