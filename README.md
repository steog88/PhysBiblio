# PhysBiblio
Bibliography manager in Python
by S. Gariazzo (stefano.gariazzo@gmail.com)

PhysBiblio is a program that helps to manage bibliography, with a particular focus on High Energy Physics tools.
It is written in Python, it uses PySide for the graphical interface and Sqlite for the database management.


## 1. Dependencies, Installation and Usage

PhysBiblio depends on several python packages:
* python-pyside (for the database)
* pyoai	(for massively harvesting the INSPIRES database)
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

** WARNING **
PhysBiblio has been intensively tested only on Ubuntu (14.04LTS to 17.10 versions), using python up to version 2.7.14.
Nevertheless, several bugs are still present and the program may freeze or crash unexpectedly.

## 2. Features
PhysBiblio has some nice features which may help to manage the bibliography.

### Import


### Export


### Update


### Categories


### Experiments
