from django.conf.urls import patterns, include, url
from concordance import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seconcordance.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
	url(r'^(?P<foundref_id>\d+)/$', views.detail, name='detail'),
)
