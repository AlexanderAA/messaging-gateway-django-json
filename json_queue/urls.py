from django.conf.urls.defaults import *

urlpatterns = patterns('json_queue.views',
    (r'^$', 'jsonq'),
)
