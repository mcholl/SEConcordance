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
	#filter_ref = VerseReference(filter_range)

	filter_ref = VerseReference("John 3:16")
	a_string = "This is a string"

	#found_references_list = VerseReference.show.in_range(filter_ref)
	#found_references_list = VerseReference.objects.order_by('book_num', 'start_chapter', 'start_verse')
	found_references_list = None

	template = loader.get_template('concordance/index.html')
	context = RequestContext( request, {
		'filter_range': filter_range,
		'filter_ref': filter_ref,
		'found_references_list': found_references_list,
		'a_string': a_string,
		})
	return HttpResponse(template.render(context))
