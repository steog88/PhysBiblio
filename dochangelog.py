#!/usr/bin/env python
"""Read json file and compile CHANGELOG and physbiblio/version.py

This file is part of the physbiblio package.
"""

import sys

import yaml

# read yaml
with open("CHANGELOG.yaml") as _f:
    text = _f.read()
changelog = yaml.load(text, Loader=yaml.FullLoader)

# prepare physbiblio/version.py
mdchanges = "<br>\n".join(
    [
        "<br>%s:<br>* %s<br>"
        % (list(l.keys())[0], "<br>\n* ".join(list(l.values())[0]))
        if isinstance(l, dict)
        else "* %s" % l
        for l in changelog[0]["changes"]
    ]
)
try:
    currdate = changelog[0]["date"].strftime("%d/%m/%Y")
except AttributeError:
    currdate = changelog[0]["date"]
text = """__version__ = "{version:}"
__version_date__ = "{datef:}"

__recent_changes__ = \"\"\"<br>{mdchanges:}<br>
\"\"\"
""".format(
    version=changelog[0]["version"],
    datef=currdate,
    mdchanges=mdchanges,
)

with open("physbiblio/version.py", "w") as _f:
    _f.write(text)


# prepare CHANGELOG
text = ""
for l in changelog:
    try:
        d = l["date"].strftime("%Y-%m-%d")
    except AttributeError:
        d = l["date"]
    text += "{version:} ({datef:}):\n".format(
        version=l["version"],
        datef=d,
    )
    if isinstance(l["changes"], dict):
        for k, v in l["changes"].items():
            text += "    %s:\n" % k
            for b in v:
                text += "    * %s\n" % b
            text += "\n"
    else:
        for a in l["changes"]:
            text += "    * %s\n" % a
        text += "\n"

with open("CHANGELOG", "w") as _f:
    _f.write(text)
