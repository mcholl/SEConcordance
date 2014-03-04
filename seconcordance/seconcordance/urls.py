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

    url(r'^search/$', views.empty_search, name='empty_search'),
    url(r'^search/(?P<filter_range>.+)$', views.search, name='search'),

    url(r'^answers/$', views.empty_answers, name='empty_answers'),
    url(r'^answers/(?P<filter_range>.+)$', views.answers, name='answers'),

    url(r'^passages/$', views.get_passages, name='get_passages'),
    url(r'^passages/(?P<filter_range>.+)$', views.passages, name='passages'),

)
