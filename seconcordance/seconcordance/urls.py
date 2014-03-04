from django.conf.urls import patterns, include, url
from concordance import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

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
#	/answers/Matthew-John		same as above, only I've expanded the range to be the entire set of the Gospels

#	/questions 					shows only questions.  Same 3 forms as above
#	/passages 					shows both questions and answers.  Same 3 forms as above

# Additionally, results can be filtered by adding any or all of the following ?parameters=value

#   ?per_page_count=#           only shows # entries per page
#   ?page=#                     shows page #

#   ?score=[positive|negative|zero_or_more]     shows only references to questions or answers where the score is [>=1|<=-1|0 or more]
#   ?site=[christianity|hermeneutics]           shows only references when the site is the one passed
#   ?filter_range=(range)                       like form 3 above (e.g. "/answers/Matthew+5-7") only shows references that fall within the passed scope.  
#                                               References can be within multiple books, but they remain within canonical order.  If the reference falls
#                                               anywhere within the range, it is conisdered to be in the range. (e.g. John 3:16-20 would fall in the range John 3:1-17)

