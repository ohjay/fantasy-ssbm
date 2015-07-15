from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^fantasy_draft/', include('fantasy_draft.urls', namespace='fantasy_draft')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_login/$', 'fantasy_draft.views.user_login', name='user_login'),
)
