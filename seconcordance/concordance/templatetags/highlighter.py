from django import template
import re
import json

register = template.Library()

#TODO: I should do the same sort of highlighting on title as body, but i twould be a separate tage, albeit using similiar code...


@register.simple_tag
def highlight_search_term(base_text, search_term):
	#This function will highlight the passed search term in the template
	if (search_term != ""):
		p = re.compile(search_term, re.IGNORECASE)
		base_text = p.sub("<SPAN class='search_term'>"+search_term+"</SPAN>", base_text)
		nStartPos = base_text.find('<SPAN class')
	else:
		nStartPos = 0

	return get_snippet(base_text, nStartPos, 300)

@register.simple_tag
def highlight_verse_reference(found_ref):
	base_text = found_ref.sepost.body[:found_ref.start_index]+"<SPAN class='verse_reference'>"+found_ref.sepost.body[found_ref.start_index:found_ref.start_index+found_ref.length]+"</SPAN>"+found_ref.sepost.body[found_ref.start_index+found_ref.length]
	return get_snippet(base_text, found_ref.start_index, 300)


def get_snippet(base_text, nStartPos, nLength):
	#Return only a snippet, based on a number of characters before and after the result

	nLength = nLength + (nLength % 2)  #Odd numbers could make it funky

	if (nStartPos > 0):
		return base_text[max(0, nStartPos - (nLength/2)):nStartPos + (nLength/2)]

	return base_text[0:nLength]

	#TODO: I could apply some intelligence to the snippet to look for unbalanced tags


