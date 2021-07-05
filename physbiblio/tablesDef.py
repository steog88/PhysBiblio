"""Static definitions of the structure (column names and content)
for the tables of the database.

This file is part of the physbiblio package.
"""
import traceback

try:
    from physbiblio.strings.main import TablesDefStrings as tdstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())

profilesSettingsTable = [
    ["name", "text", "primary key not null"],
    ["databasefile", "text", "not null"],
    ["description", "text", ""],
    ["oldCfg", "text", ""],
    ["isDefault", "integer", "default 0"],
    ["ord", "integer", "default 100"],
    ["CONSTRAINT", "unique_databasefile", "UNIQUE (databasefile)"],
]
searchesTable = [
    ["idS", "integer", "primary key"],
    ["name", "text", ""],
    ["count", "integer", "default 0 not null"],
    ["searchDict", "text", "not null"],
    ["limitNum", "integer", "default 50"],
    ["offsetNum", "integer", "default 0"],
    ["replaceFields", "text", ""],
    ["manual", "integer", "default 0"],
    ["isReplace", "integer", "default 0"],
]
searchesTableDescriptions = tdstr.searchesDescs

tableFields = {}
tableFields["entries"] = [
    ["bibkey", "text", "primary key not null collate nocase"],
    ["inspire", "text", ""],
    ["arxiv", "text", ""],
    ["ads", "text", ""],
    ["scholar", "text", ""],
    ["doi", "text", ""],
    ["isbn", "text", ""],
    ["year", "integer", ""],
    ["link", "text", ""],
    ["comments", "text", ""],
    ["old_keys", "text", ""],
    ["crossref", "text", ""],
    ["bibtex", "text", "not null"],
    ["firstdate", "text", "not null"],
    ["pubdate", "text", ""],
    ["exp_paper", "integer", "default 0"],
    ["lecture", "integer", "default 0"],
    ["phd_thesis", "integer", "default 0"],
    ["review", "integer", "default 0"],
    ["proceeding", "integer", "default 0"],
    ["book", "integer", "default 0"],
    ["noUpdate", "integer", "default 0"],
    ["marks", "text", ""],
    ["abstract", "text", ""],
    ["bibdict", "text", ""],
    ["citations", "integer", "default 0"],
    ["citations_no_self", "integer", "default 0"],
]
tableFields["categories"] = [
    ["idCat", "integer", "primary key"],
    ["name", "text", "not null"],
    ["description", "text", "not null"],
    ["parentCat", "integer", "default 0"],
    ["comments", "text", "default ''"],
    ["ord", "integer", "default 0"],
]
tableFields["experiments"] = [
    ["idExp", "integer", "primary key"],
    ["name", "text", "not null"],
    ["comments", "text", "not null"],
    ["homepage", "text", ""],
    ["inspire", "text", ""],
]
tableFields["expCats"] = [
    ["idExC", "integer", "primary key"],
    ["idExp", "integer", "not null"],
    ["idCat", "integer", "not null"],
]
tableFields["entryCats"] = [
    ["idEnC", "integer", "primary key"],
    ["bibkey", "text", "not null"],
    ["idCat", "integer", "not null"],
]
tableFields["entryExps"] = [
    ["idEnEx", "integer", "primary key"],
    ["bibkey", "text", "not null"],
    ["idExp", "integer", "not null"],
]
tableFields["settings"] = [
    ["name", "text", "primary key not null"],
    ["value", "text", "default ''"],
]
fieldsDescriptions = {}
fieldsDescriptions["entries"] = tdstr.entriesDescs
fieldsDescriptions["categories"] = tdstr.catsDescs
fieldsDescriptions["experiments"] = tdstr.expsDescs
fieldsDescriptions["expCats"] = tdstr.expsCatsDescs
fieldsDescriptions["entryCats"] = tdstr.entriesCatsDescs
fieldsDescriptions["entryExps"] = tdstr.entriesExpsDescs
fieldsDescriptions["settings"] = tdstr.settingsDescs
