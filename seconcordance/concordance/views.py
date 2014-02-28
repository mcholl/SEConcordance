from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

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