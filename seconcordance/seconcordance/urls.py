from django.conf.urls import patterns, include, url
from concordance import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seconcordance.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^passages/$', views.get_passages, name='get_passages'),
    url(r'^passages/(?P<filter_range>.+)$', views.passages, name='passages'),
    url(r'^answers/$', views.get_answers, name='get_answers'),
    url(r'^answers/(?P<filter_range>.+)$', views.answers, name='answers'),
    url(r'^questions/$', views.get_questions, name='get_questions'),
    url(r'^questions/(?P<filter_range>.+)$', views.questions, name='questions'),
)


# Exmaple Urls:
#	/answers 					returns a page showing every answer
#	/answers/Matthew			returns a page showing all answers in Matthew
#	/answers/?filter_range=Matthew-John		same as above, only in GET syntax, and I've expanded the range to be the entire set of the Gospels

#	/questions 					shows only questions.  Same 3 forms as above
#	/passages 					shows both questions and answers.  Same 3 forms as above
