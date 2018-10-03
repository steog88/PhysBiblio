"""Static definitions of the structure (column names and content)
for the tables of the database.

This file is part of the physbiblio package.
"""
profilesSettingsTable = [
	["name", 		"text", "primary key not null"],
	["databasefile","text", "not null"],
	["description", "text", ""],
	["oldCfg",      "text", ""],
	["isDefault", 	"integer", "default 0"],
	["ord", 		"integer", "default 100"]
]
searchesTable = [
	["idS",				"integer", "primary key"],
	["name",			"text", ""],
	["count",			"integer", "default 0 not null"],
	["searchDict",		"text", "not null"],
	["limitNum",		"integer", "default 50"],
	["offsetNum",		"integer", "default 0"],
	["replaceFields",	"text", ""],
	["manual",			"integer", "default 0"],
	["isReplace",		"integer", "default 0"]]
searchesTableDescriptions = {
	"idS":				"Unique identifier",
	"name":				"Custom name of the search/replace",
	"count":			"Order of the entry in the cronology",
	"searchDict":		"Dictionary of fields to be passed to fetchByDict",
	"limit":			"The max number of results in the search",
	"offset":			"The offset in the search",
	"replaceFields":	"List of fields used in replacement",
	"manual":			"Manually saved",
	"isReplace":		"(T/F) A replacement or a simple search"}

tableFields = {}
tableFields["entries"] = [
	["bibkey", 	"text", "primary key not null"],
	["inspire", "text", ""],
	["arxiv", 	"text", ""],
	["ads", 	"text", ""],
	["scholar", "text", ""],
	["doi", 	"text", ""],
	["isbn", 	"text", ""],
	["year", 	"integer", ""],
	["link", 	"text", ""],
	["comments", 	"text", ""],
	["old_keys", 	"text", ""],
	["crossref", 	"text", ""],
	["bibtex", 		"text", "not null"],
	["firstdate", 	"text", "not null"],
	["pubdate", 	"text", ""],
	["exp_paper",	"integer", "default 0"],
	["lecture",		"integer", "default 0"],
	["phd_thesis",	"integer", "default 0"],
	["review",		"integer", "default 0"],
	["proceeding",	"integer", "default 0"],
	["book",		"integer", "default 0"],
	["noUpdate",	"integer", "default 0"],
	["marks", 		"text", ""],
	["abstract", 	"text", ""],
	["bibdict", 	"text", ""]];
tableFields["categories"] = [
	["idCat", 		"integer", "primary key"],
	["name", 		"text", "not null"],
	["description", "text", "not null"],
	["parentCat", 	"integer", "default 0"],
	["comments", 	"text", "default ''"],
	["ord", 		"integer", "default 0"]];
tableFields["experiments"] = [
	["idExp", 	 "integer", "primary key"],
	["name", 	 "text", "not null"],
	["comments", "text", "not null"],
	["homepage", "text", ""],
	["inspire",  "text", ""]];
tableFields["expCats"] = [
	["idExC", "integer", "primary key"],
	["idExp", "integer", "not null"],
	["idCat", "integer", "not null"]];
tableFields["entryCats"] = [
	["idEnC",  "integer", "primary key"],
	["bibkey", "text", "not null"],
	["idCat",  "integer", "not null"]];
tableFields["entryExps"] = [
	["idEnEx", "integer", "primary key"],
	["bibkey", "text", "not null"],
	["idExp",  "integer", "not null"]];
tableFields["settings"] = [
	["name", 	"text", "primary key not null"],
	["value", 	"text", "default ''"]]
fieldsDescriptions = {}
fieldsDescriptions["entries"] = {
	"bibkey":	"Unique bibtex key that identifies the bibliographic element",
	"inspire":	"INSPIRE-HEP ID of the record",
	"arxiv":	"arXiv ID of the record",
	"ads":		"NASA ADS ID of the record",
	"scholar":	"Google Scholar ID of the record",
	"doi":		"DOI of the record",
	"isbn":		"ISBN code of the record",
	"year":		"Year of publication",
	"link":		"Web link to article or additional material",
	"comments":	"Comments",
	"old_keys":	"Previous bibtex keys of the record",
	"crossref":	"Bibtex crossref reference",
	"bibtex":	"Bibtex entry",
	"firstdate":"Date of first appearance",
	"pubdate":	"Date of publication",
	"exp_paper": "(T/F) The entry is a collaboration paper of some experiment",
	"lecture":	 "(T/F) The entry is a lecture",
	"phd_thesis":"(T/F) The entry is a PhD thesis",
	"review":	 "(T/F) The entry is a review",
	"proceeding":"(T/F) The entry is a proceeding",
	"book":		 "(T/F) The entry is a book",
	"noUpdate":  "(T/F) The entry has been created/modified by the user "
		+ "and/or should not be updated",
	"marks":	 "Mark the record",
	"abstract":	 "Abstract of the record",
	"bibdict":   "Dictionary with fields of the bibtex entry from bibtexparser"}
fieldsDescriptions["categories"] = {
	"idCat": 		"Unique ID that identifies the category",
	"name": 		"Name of the category",
	"description": 	"Description of the category",
	"parentCat": 	"Parent category",
	"comments": 	"Comments",
	"ord": 			"Ordering when plotting (not yet implemented)"}
fieldsDescriptions["experiments"] = {
	"idExp": 	"Unique ID that identifies the experiment",
	"name": 	"Name of the experiment",
	"comments": "Description or comments",
	"homepage": "Web link to the experiment homepage",
	"inspire": 	"INSPIRE-HEP ID of the experiment record"}
fieldsDescriptions["expCats"] = {
	"idExC": "Unique identifier",
	"idExp": "Corresponding experiment ID",
	"idCat": "Corresponding category ID"}
fieldsDescriptions["entryCats"] = {
	"idEnC":  "Unique identifier",
	"bibkey": "Corresponding bibtex key",
	"idCat":  "Corresponding category ID"}
fieldsDescriptions["entryExps"] = {
	"idEnEx": "Unique identifier",
	"bibkey": "Corresponding bibtex key",
	"idExp":  "Corresponding experiment ID"}
fieldsDescriptions["settings"] = {
	"id": 		"Unique identifier",
	"name": 	"name of the setting",
	"value":	"value of the setting"}
