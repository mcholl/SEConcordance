from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import django.shortcuts
from django.http import Http404
from django.db.models import Q

from VerseReference import *
import pprint
import json

from concordance.models import *

# Create your views here.
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

	per_page_count=request.GET.get('per_page_count', 25)
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

	#Allow for filters of score=positive (1 or more), negative, zero_or_more
	filter_score = request.GET.get('score', '')
	if filter_score != "":
		if filter_score[0:1].lower() == "p":
			population = population.filter(sepost__score__gt=0)
		elif filter_score[0:1].lower() == "n":
			population = population.filter(sepost__score__lt=0)
		else:
			population = population.filter(sepost__score__gte=0)

	#Allow for filters of site=christianity, hermeneutics
	filter_site = request.GET.get('site','')
	if filter_site != "":
		population = population.filter(sepost__se_link__contains=filter_site)

	#Return references to posts containing search terms only...
	filter_terms = request.GET.get('terms','')
	if filter_terms != "":
		population = population.filter(Q(sepost__posttitle__contains=filter_terms) | Q(sepost__body__contains=filter_terms))


	per_page_count=request.GET.get('per_page_count', 25)

	#Pass the results to the rendered template
	context = {
		'found_references_list': paginate(request, list(population)),
		'filters': {
			'range': filter_range,
			'score': filter_score,
			'site': filter_site,
			'terms': filter_terms,
			'per_page_count': per_page_count,
		}
	}
	return render(request, 'concordance/base_results.html', context) 

def show_logs(request):
	#Reads the Last Run Dates and reports them
	lastruns = report_last_runs()
	context = {
		'sites_list': lastruns,
	}
	return render(request, 'concordance/base_diagnostics.html', context) 

