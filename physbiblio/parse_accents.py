# -*- coding: iso-8859-15 -*-
"""
This module tries to convert the unicode accented chars into latex strings.
Will be probably rewritten to use pylatexenc.

This file is part of the physbiblio package.
"""
import re
import sys

try:
	from physbiblio.errors import pBLogger
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

accents_changed = []
################################################################
# LaTeX accents replacement
unicode_to_latex = {
    u"\u00C0": "{\\`A}",
    u"\u00C1": "{\\'A}",
    u"\u00C2": "{\\^A}",
    u"\u00C3": "{\\~A}",
    u"\u00C4": "{\\\"A}",
    u"\u00C5": "\\AA ",
    u"\u00C6": "\\AE ",
    u"\u00C7": "\\c{C}",
    u"\u00C8": "{\\`E}",
    u"\u00C9": "{\\'E}",
    u"\u00CA": "{\\^E}",
    u"\u00CB": "{\\\"E}",
    u"\u00CC": "{\\`I}",
    u"\u00CD": "{\\'I}",
    u"\u00CE": "{\\^I}",
    u"\u00CF": "{\\\"I}",
    u"\u00D0": "\\DH ",
    u"\u00D1": "{\\~N}",
    u"\u00D2": "{\\`O}",
    u"\u00D3": "{\\'O}",
    u"\u00D4": "{\\^O}",
    u"\u00D5": "{\\~O}",
    u"\u00D6": "{\\\"O}",
    u"\u00D7": "\\texttimes ",
    u"\u00D8": "\\O ",
    u"\u00D9": "{\\`U}",
    u"\u00DA": "{\\'U}",
    u"\u00DB": "{\\^U}",
    u"\u00DC": "{\\\"U}",
    u"\u00DD": "{\\'Y}",
    u"\u00DE": "\\TH ",
    u"\u00DF": "\\ss ",
    u"\u00E0": "{\\`a}",
    u"\u00E1": "{\\'a}",
    u"\u00E2": "{\\^a}",
    u"\u00E3": "{\\~a}",
    u"\u00E4": "{\\\"a}",
    u"\u00E5": "\\aa ",
    u"\u00E6": "\\ae ",
    u"\u00E7": "{\\cc}",
    u"\u00E8": "{\\`e}",
    u"\u00E9": "{\\'e}",
    u"\u00EA": "{\\^e}",
    u"\u00EB": "{\\\"e}",
    u"\u00EC": "{\\`\\i}",
    u"\u00ED": "{\\'\\i}",
    u"\u00EE": "{\\^\\i}",
    u"\u00EF": "{\\\"\\i}",
    u"\u00F0": "\\dh ",
    u"\u00F1": "{\\~n}",
    u"\u00F2": "{\\`o}",
    u"\u00F3": "{\\'o}",
    u"\u00F4": "{\\^o}",
    u"\u00F5": "{\\~o}",
    u"\u00F6": "{\\\"o}",
    u"\u00F7": "\\div ",
    u"\u00F8": "\\o ",
    u"\u00F9": "{\\`u}",
    u"\u00FA": "{\\'u}",
    u"\u00FB": "{\\^u}",
    u"\u00FC": "{\\\"u}",
    u"\u00FD": "{\\'y}",
    u"\u00FE": "\\th ",
    u"\u00FF": "\\\"{y}",
    u"\u0100": "{\\=A}",
    u"\u0101": "{\\=a}",
    u"\u0102": "{\\u A}",
    u"\u0103": "{\\u a}",
    u"\u0104": "{\\k A}",
    u"\u0105": "{\\k a}",
    u"\u0106": "{\\'C}",
    u"\u0107": "{\\'c}",
    u"\u0108": "{\\^C}",
    u"\u0109": "{\\^c}",
    u"\u010A": "{\\.C}",
    u"\u010B": "{\\.c}",
    u"\u010C": "{\\v C}",
    u"\u010D": "{\\v c}",
    u"\u010E": "{\\v D}",
    u"\u010F": "{\\v d}",
    u"\u0110": "\\DJ ",
    u"\u0111": "\\dj ",
    u"\u0112": "{\\=E}",
    u"\u0113": "{\\=e}",
    u"\u0114": "{\\u E}",
    u"\u0115": "{\\u e}",
    u"\u0116": "{\\.E}",
    u"\u0117": "{\\.e}",
    u"\u0118": "{\\k E}",
    u"\u0119": "{\\k e}",
    u"\u011A": "{\\v E}",
    u"\u011B": "{\\v e}",
    u"\u011C": "{\\^G}",
    u"\u011D": "{\\^g}",
    u"\u011E": "{\\u G}",
    u"\u011F": "{\\u g}",
    u"\u0120": "{\\.G}",
    u"\u0121": "{\\.g}",
    u"\u0122": "{\\c G}",
    u"\u0123": "{\\c g}",
    u"\u0124": "{\\^H}",
    u"\u0125": "{\\^h}",
    u"\u0127": "\\Elzxh ",
    u"\u0128": "{\\~I}",
    u"\u0129": "{\\~\\i}",
    u"\u012A": "{\\=I}",
    u"\u012B": "{\\=\\i}",
    u"\u012C": "{\\uI}",
    u"\u012D": "{\\u\\i}",
    u"\u012E": "{\\k I}",
    u"\u012F": "{\\k i}",
    u"\u0130": "{\\.I}",
    u"\u0131": "\\i ",
    u"\u0132": "IJ",
    u"\u0133": "ij",
    u"\u0134": "{\\^J}",
    u"\u0135": "{\\^\\j}",
    u"\u0136": "{\\c {K}",
    u"\u0137": "{\\c{k}",
    u"\u0139": "{\\'L}",
    u"\u013A": "{\\'l}",
    u"\u013B": "{\\c L}",
    u"\u013C": "{\\c l}",
    u"\u013D": "{\\v L}",
    u"\u013E": "{\\v l}",
    u"\u0141": "\\L ",
    u"\u0142": "\\l ",
    u"\u0143": "{\\'N}",
    u"\u0144": "{\\'n}",
    u"\u0145": "{\\c N}",
    u"\u0146": "{\\c n}",
    u"\u0147": "{\\v N}",
    u"\u0148": "{\\v n}",
    u"\u0149": "'n",
    u"\u014A": "\\NG ",
    u"\u014B": "\\ng ",
    u"\u014C": "{\\=O}",
    u"\u014D": "{\\=o}",
    u"\u014E": "{\\u O}",
    u"\u014F": "{\\u o}",
    u"\u0150": "{\\H O}",
    u"\u0151": "{\\H o}",
    u"\u0152": "\\OE ",
    u"\u0153": "\\oe ",
    u"\u0154": "{\\'R}",
    u"\u0155": "{\\'r}",
    u"\u0156": "{\\c R}",
    u"\u0157": "{\\c r}",
    u"\u0158": "{\\v R}",
    u"\u0159": "{\\v r}",
    u"\u015A": "{\\'S}",
    u"\u015B": "{\\'s}",
    u"\u015C": "{\\^S}",
    u"\u015D": "{\\^s}",
    u"\u015E": "{\\c S}",
    u"\u015F": "{\\c s}",
    u"\u0160": "{\\v S}",
    u"\u0161": "{\\v s}",
    u"\u0162": "{\\c T}",
    u"\u0163": "{\\c t}",
    u"\u0164": "{\\v T}",
    u"\u0165": "{\\v t}",
    u"\u0168": "{\\~U}",
    u"\u0169": "{\\~u}",
    u"\u016A": "{\\=U}",
    u"\u016B": "{\\=u}",
    u"\u016C": "{\\u U}",
    u"\u016D": "{\\u u}",
    u"\u016E": "{\\r U}",
    u"\u016F": "{\\r u}",
    u"\u0170": "{\\H U}",
    u"\u0171": "{\\H u}",
    u"\u0172": "{\\k U}",
    u"\u0173": "{\\k u}",
    u"\u0174": "{\\^W}",
    u"\u0175": "{\\^w}",
    u"\u0176": "{\\^Y}",
    u"\u0177": "{\\^y}",
    u"\u0178": "{\\\"Y}",
    u"\u0179": "{\\'Z}",
    u"\u017A": "{\\'z}",
    u"\u017B": "{\\.Z}",
    u"\u017C": "{\\.z}",
    u"\u017D": "{\\v Z}",
    u"\u017E": "{\\v z}",
    u"\u01F5": "{\\'g}",
    u"\u03CC": "{\\'o}",
    u"\u2009": " ",
    u"\u2013": "-",
    u"\u207b": "-",
    u"\u2014": "--",
    u"\u2015": "---",
}

if sys.version_info[0] < 3:
	translation_table = dict([(ord(k), unicode(v)) for k, v in unicode_to_latex.items()])
else:
	translation_table = dict([(ord(k), str(v)) for k, v in unicode_to_latex.items()])

def parse_accents_str(string):
	"""
	Function that reads a string and translates all the known unicode characters into latex commands.

	Parameters:
		string: the string to be translated

	Output:
		the processed string
	"""
	if string is not None and string is not "":
		string = string.translate(translation_table)
	return string

def parse_accents_record(record):
	"""
	Function that reads the fields inside a bibtex dictionary and translates all the known unicode characters into latex commands.

	Parameters:
		record: the bibtex dictionary generated by bibtexparser

	Output:
		the dictionary after having processed all the fields
	"""
	for val in record:
		if val is not "ID" and len(record[val].strip()) > 0:
			tmp = parse_accents_str(record[val])
			if tmp != record[val]:
				pBLogger.info("    -> Converting bad characters in entry %s: "%record["ID"])
				pBLogger.info("         -- "+tmp.encode("utf-8"))
				accents_changed.append(record["ID"])
			record[val] = tmp
	return record

latex2Html_commands = [
	["textit","i"],
	["textbf","b"],
]
latex2Html_strings = [
	["\%","%"],
	["~"," "],
	["\ "," "],
]
latex_replace = [
	["text", "rm"],
]

def texToHtml(text):
	"""
	Function that converts some Latex commands into HTML commands.

	Parameters:
		text: the string to be processed

	Output:
		the processed string
	"""
	for tex, html in latex2Html_commands:
		match = re.compile('\\\\%s\{(.*| |\n)?\}'%tex, re.MULTILINE)
		for t in match.finditer(text):
			text = text.replace(t.group(), "<{html}>{cont}</{html}>".format(html = html, cont = t.group(1)))
	for tex, html in latex2Html_strings:
		text = text.replace(tex, html)
	for tex, new in latex_replace:
		match = re.compile('\\\\%s\{(.*| |\n)?\}'%tex, re.MULTILINE)
		for t in match.finditer(text):
			text = text.replace(t.group(), "\\%s{%s}"%(new, t.group(1)))
	return text
