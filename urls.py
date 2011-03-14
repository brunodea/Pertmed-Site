from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'pertmed_site.md_manager.views.index'),
    (r'^index/$', 'pertmed_site.md_manager.views.index'),
    (r'^login/$', 'pertmed_site.md_manager.views.login'),
    (r'^profile/$', 'pertmed_site.md_manager.views.profile'),
    (r'^register/$', 'pertmed_site.md_manager.views.register'),
#    (r'^signup/thanks $', 'pertmed_site.md_manager.views.signup_thanks'),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', logout),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
)
