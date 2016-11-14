tableFields = {}
tableFields["entries"] = [
	["bibkey", "text", "primary key not null"],
	["inspire", "text", ""],
	["arxiv", "text", ""],
	["ads", "text", ""],
	["scholar", "text", ""],
	["doi", "text", ""],
	["isbn", "text", ""],
	["year", "int", ""],
	["link", "text", ""],
	["comments", "text", ""],
	["old_keys", "text", ""],
	["crossref", "text", ""],
	["bibtex", "text", "not null"],
	["firstdate", "text", "not null"],
	["pubdate", "text", ""],
	["exp_paper",	"int", "default 0"],
	["lecture",		"int", "default 0"],
	["phd_thesis",	"int", "default 0"],
	["review",		"int", "default 0"],
	["proceeding",	"int", "default 0"],
	["book",		"int", "default 0"],
	["marks", "text", ""]];
tableFields["categories"] = [
	["idCat", "integer", "primary key"],
	["name", "text", "not null"],
	["description", "text", "not null"],
	["parentCat", "int", "default 0"],
	["comments", "text", "default ''"],
	["ord", "int", "default 0"]];
tableFields["experiments"] = [
	["idExp", "integer", "primary key"],
	["name", "text", "not null"],
	["comments", "text", "not null"],
	["homepage", "text", ""],
	["inspire", "text", ""]];
tableFields["expCats"] = [
	["idExC", "integer", "primary key"],
	["idExp", "int", "not null"],
	["idCat", "int", "not null"]];
tableFields["entryCats"] = [
	["idEnC", "integer", "primary key"],
	["bibkey", "text", "not null"],
	["idCat", "int", "not null"]];
tableFields["entryExps"] = [
	["idEnEx", "integer", "primary key"],
	["bibkey", "text", "not null"],
	["idExp", "int", "not null"]];
