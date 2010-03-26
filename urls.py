from django.conf.urls.defaults import *
from django.contrib import admin
import settings

admin.autodiscover()


urlpatterns = patterns('',
    (r'^gateway/', include('json_queue.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True})
    )
