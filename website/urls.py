from django.conf.urls import include, url
from django.contrib import admin
import fantasy_draft.views

urlpatterns = [
    url(r'', include('fantasy_draft.urls', namespace='fantasy_draft')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_login/$', fantasy_draft.views.user_login, name='user_login'),
]
