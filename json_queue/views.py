from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.core.signals import request_finished
import settings
import datetime
import re
import math
import time
import settings
import queue.queue_api
from JSON.custom.myjsonrpc import JSONRPC, JSONRPCMethod


class OEDQueueRpcService:
    def __init__(self, service_url):
        self.url = service_url
        self.q = queue.queue_api.DBQueue()
        
    @JSONRPCMethod
    def add_qi(self, qi_id, method, params):
        '''
        @qi_id: string
            task_id used to get the task from queue. It MUST be unique!
            #TODO: ensure given task_id is unique.
        @method: string
        @params: string
        => dict
        '''
        #Valid task for queue is:
        #{'task_id':'string', 'task':'string', result:'string', error:}
        result = self.q.add_qi(qi_id, method, params)
        return result
    
    @JSONRPCMethod
    def resend_qi(self, qi_id):
        '''
        @qi_id: string
            task_id used to get the task from queue. It MUST be unique!
            #TODO: ensure given task_id is unique.
        '''
        #Valid task for queue is:
        #{'task_id':'string', 'task':'string', result:'string', error:}
        result = self.q.resend_qi(qi_id)
        return result

    
    @JSONRPCMethod
    def get_qi(self):
        '''
        Asks the server to choose the task to process from query
        returns task in the following format:
        '''
        return self.q.get_qi()
        
    @JSONRPCMethod 
    def add_result(self, qi_id, result):
        '''
        Adds result of processing by queue_item ID
        '''
        return self.q.add_result(qi_id, result)
        
    @JSONRPCMethod
    def get_result(self, qi_id):
        '''
        Returns result of processing and removes item from queue
        '''
        return self.q.get_result(qi_id)
    
    @JSONRPCMethod
    def get_all_qi(self):
        '''
        For testing purposes only! Could overload the server!
        '''
        return self.q.get_all_qi()
    
    @JSONRPCMethod
    def clear_queue(self, time_interval = 0):
        '''
        Removes all entries from queue if (time_interval == 0)

        @time_interval: 
        if 
            time_interval (in seconds) is in range(1, sys.maxint), 
        then 
            clear all entries, that were previously sent for processing time_interval or earlier in the past
        '''
        return self.q.clear_queue(time_interval)

    @JSONRPCMethod
    def resend_all(self):
        '''
        Marks all old entries to resend for processing
        '''
        return self.q.resend_all()

    @JSONRPCMethod
    def queue_length(self):
        '''
        Elements in queue. For testing purposes only.
        '''
        return self.q.queue_length()

import urllib2
def jsonq(request):
    #from .microtasks.views import json_service
    SERVICE_URL = urllib2.urlparse.urljoin(settings.SITE_URL, reverse(jsonq))
    result  = JSONRPC(OEDQueueRpcService(SERVICE_URL)).handle_request(request)
    return result
