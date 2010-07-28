from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^index/$', 'pertmed_site.md_manager.views.index'),
    (r'^login/$', 'pertmed_site.md_manager.views.login'),
    (r'^profile/(?P<object_id>\d+)/$', 'pertmed_site.md_manager.views.profile'),
    (r'^profile/(?P<object_id>\d+)/change/$', 'pertmed_site.md_manager.views.profile_change'),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
)
