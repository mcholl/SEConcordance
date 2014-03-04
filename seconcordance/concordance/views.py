from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import django.shortcuts
from django.http import Http404

from VerseReference import *
import pprint

from concordance.models import *

# Create your views here.
per_page_count=100

def index(request):
	return passages(request, "")

def answers(request, filter_range):
	return generic_results(request, VerseReference.answers, filter_range)

def get_answers(request):
	filter_range = request.GET.get('filter_range', '')
	return answers(request, filter_range)

def questions(request, filter_range):
	return generic_results(request, VerseReference.questions, filter_range)

def get_questions(request):
	filter_range = request.GET.get('filter_range', '')
	return answers(request, filter_range)

def passages(request, filter_range):
	#Displays Matching Passages in the passed filter_range (e.g. "Matthew 3 - 10" or "Joshua - Ezra")
	return generic_results(request, VerseReference.passages, filter_range)

def get_passages(request):
	#Helper Function to display passages when passed in the form /passages/?filter_range=Matthew-John
	filter_range = request.GET.get('filter_range', '')
	return passages(request, filter_range)


def paginate(request, found_references):
	#Helper method to paginate the result set.  found_references is a list containing results of the queryset.  Need request to read the page parameter, if passed

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


def generic_results(request, filter_method, filter_range):
	#Helper function - answers, questions, and passages all work the same way: VerseReference.answers.in_range, for example is the population
	try:
		if filter_range is None or filter_range == "":
			population = filter_method.all()
		else:
			population = filter_method.in_range(filter_range)
	except:
		raise Http404 

	context = {
		'found_references_list': paginate(request, list(population)),
		'filter_range': filter_range,
	}
	return render(request, 'concordance/index.html', context) 

