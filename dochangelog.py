#!/usr/bin/env python
"""Read json file and compile CHANGELOG and physbiblio/version.py

This file is part of the physbiblio package.
"""

import yaml

# read yaml
with open("CHANGELOG.yaml") as _f:
    text = _f.read()
changelog = yaml.load(text, Loader=yaml.FullLoader)

# prepare physbiblio/version.py
lastchanges = changelog[0]["changes"]

if isinstance(lastchanges, list):
    mdchanges = "<br>\n".join(
        [
            (
                "<br>{}:<br>* {}<br>".format(
                    next(iter(li.keys())), "<br>\n* ".join(next(iter(li.values())))
                )
                if isinstance(li, dict)
                else f"* {li}"
            )
            for li in lastchanges
        ]
    )
elif isinstance(lastchanges, dict):
    mdchanges = "<br>\n".join(
        [
            "<br><b>{}:</b><br>\n* {}".format(li, "<br>\n* ".join(list(v)))
            if isinstance(v, list)
            else f"* {li}"
            for li, v in lastchanges.items()
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
for li in changelog:
    try:
        d = li["date"].strftime("%Y-%m-%d")
    except AttributeError:
        d = li["date"]
    text += "{version:} ({datef:}):\n".format(
        version=li["version"],
        datef=d,
    )
    if isinstance(li["changes"], dict):
        for k, v in li["changes"].items():
            text += f"    {k}:\n"
            for b in v:
                text += f"    * {b}\n"
            text += "\n"
    else:
        for a in li["changes"]:
            text += f"    * {a}\n"
        text += "\n"

with open("CHANGELOG", "w") as _f:
    _f.write(text)
