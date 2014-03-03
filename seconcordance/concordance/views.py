from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from VerseReference import *
import pprint

from concordance.models import *

# Create your views here.
def index(request):

	found_references_list = VerseReference.objects.order_by('book_num', 'start_chapter', 'start_verse')

	template = loader.get_template('concordance/index.html')
	context = RequestContext( request, {
		'found_references_list': found_references_list,
		})
	return HttpResponse(template.render(context))

def detail(request, found_ref):
	return HttpResponse("Not implemented")

def search(request, filter_range):
	search_ref = BibleReference(filter_range)
	qry_in_range = "SELECT * FROM concordance_reference WHERE ref_book_num>=%s AND ref_book_num<=%s AND ref_endchapter_num >= %s AND ref_endverse_num >= %s AND ref_startchapter_num <= %s AND ref_startverse_num <= %s ORDER BY ref_book_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num"
	params = tuple([search_ref.book_num, search_ref.end_book_num, search_ref.start_chapter, search_ref.start_verse, search_ref.end_chapter, search_ref.end_verse]) 

	found_references_list = VerseReference.objects.raw(qry_in_range, params)

	template = loader.get_template('concordance/index.html')
	context = RequestContext( request, {
		'filter_range': filter_range,
		'filter_ref': search_ref,
		'found_references_list': found_references_list,
		})
	return HttpResponse(template.render(context))

def empty_search(request):
	filter_range = request.GET.get('filter_range', '')
	return search(request, filter_range)
