from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import django.shortcuts

from VerseReference import *
import pprint

from concordance.models import *

# Create your views here.
per_page_count=100

def index(request):

	found_references = VerseReference.objects.order_by('book_num', 'start_chapter', 'start_verse')
	paginator = Paginator(found_references, per_page_count)

	page = request.GET.get('page')
	try:
 		found_references_list = paginator.page(page)
 	except PageNotAnInteger:
        # If page is not an integer, deliver first page.
 		found_references_list = paginator.page(1)
 	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		found_references_list = paginator.page(paginator.num_pages)

	#return render_to_response('concordance/index.html', {"found_references_list": found_references_list})

	template = loader.get_template('concordance/index.html')
	context = RequestContext( request, {
		'found_references_list': found_references_list,
		})
	return HttpResponse(template.render(context))

def search(request, filter_range):
	search_ref = BibleReference(filter_range)
	qry_in_range = "SELECT * FROM concordance_reference WHERE ref_book_num>=%s AND end_book_num<=%s AND ref_endchapter_num >= %s AND ref_endverse_num >= %s AND ref_startchapter_num <= %s AND ref_startverse_num <= %s ORDER BY ref_book_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num"
	params = tuple([search_ref.book_num, search_ref.end_book_num, search_ref.start_chapter, search_ref.start_verse, search_ref.end_chapter, search_ref.end_verse]) 
	found_references_list = paginate(request, list(VerseReference.objects.raw(qry_in_range, params)))

	template = loader.get_template('concordance/index.html')
	context = RequestContext( request, {
		'found_references_list': found_references_list,
		'filter_range': filter_range,
		})
	return HttpResponse(template.render(context))


def paginate(request, found_references):
	paginator = Paginator(found_references, per_page_count)

	page = request.GET.get('page')
	try:
 		found_references_list = paginator.page(page)
 	except PageNotAnInteger:
        # If page is not an integer, deliver first page.
 		found_references_list = paginator.page(1)
 	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		found_references_list = paginator.page(paginator.num_pages)

	return found_references_list

def empty_search(request):
	filter_range = request.GET.get('filter_range', '')
	return search(request, filter_range)

def answers(request, filter_range):
	search_ref = BibleReference(filter_range)
	qry_in_range = "SELECT * FROM concordance_reference WHERE ref_book_num>=%s AND end_book_num<=%s AND ref_endchapter_num >= %s AND ref_endverse_num >= %s AND ref_startchapter_num <= %s AND ref_startverse_num <= %s ORDER BY ref_book_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num"
	params = tuple([search_ref.book_num, search_ref.end_book_num, search_ref.start_chapter, search_ref.start_verse, search_ref.end_chapter, search_ref.end_verse]) 

	found_references_list = paginate(request, list(VerseReference.answers.raw(qry_in_range, params)))
	return render_to_response('concordance/index.html', {"found_references_list": found_references_list})

def empty_answers(request):
	context = {'found_references_list': VerseReference.answers.all()}
	return render(request, 'concordance/index.html', context) 

	# filter_range = request.GET.get('filter_range', '')
	# return answers(request, filter_range)

def passages(request, filter_range):
	#Displays Matching Passages in the passed filter_range (e.g. "Matthew 3 - 10" or "Joshua - Ezra")
	results = VerseReference.passages.in_range(filter_range)
	context = {
		'found_references_list': paginate(request, list(results)),
		'filter_range': filter_range,
	}
	return render(request, 'concordance/index.html', context) 

def get_passages(request):
	#Helper Function to display passages when passed in the form /passages/?filter_range=Matthew-John
	filter_range = request.GET.get('filter_range', '')
	return passages(request, filter_range)

