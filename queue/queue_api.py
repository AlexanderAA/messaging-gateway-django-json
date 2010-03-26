import settings
DEBUG = settings.DEBUG

import sys
import time
import django.db
from json_queue.models import QIModel
import json_queue.models

#---protocol specific:
##Protocol fields:
KEY_QI_ID = 'qi_id'
KEY_METHOD = 'method'
KEY_PARAMS = 'params'
KEY_RESULT = 'result'
KEY_ERROR = 'error'
KEY_IN_PROCESS_FROM = 'in_process'

##Errors:
ERROR_NOT_IN_QUEUE = 'not in queue'
ERROR_NOT_PROCESSED_YET = 'not processed yet'
ERROR_QUEUE_EMPTY = 'queue is empty'
ERROR_DUPLICATE_QI_ID = 'duplicate qi_id'
ERROR_WRONG_ARGUMENT = 'wrong argument'
ERROR_UNSPECIFIED = 'unspecified error, please report me to developer'
RESULT_OK = 'success'

##Methods:
METHOD_GET_TAGS = 'get_tags'
METHOD_HIGHLIGHT_COMPANIES = 'extract_companynames'
#---end protocol specific

LOW_RESOURCES_MODE = True
MAX_ITEMS_IN_QUEUE = 10000

def qi_dict(qi_id = None, method=None, params=None, result=None, error = None, in_process_from = None):
    '''
    Returns queue item
    '''
    return {KEY_QI_ID: qi_id, 
            KEY_METHOD: method,
            KEY_PARAMS: params, 
            KEY_RESULT: result, 
            KEY_ERROR: error, 
            KEY_IN_PROCESS_FROM: in_process_from}

def qimodel_to_dict(qi_model_instance):
    '''
    Returns queue item
    '''
    try:
        assert type(qi_model_instance) == QIModel
    except AssertionError:
        return qi_dict(error = ERROR_WRONG_ARGUMENT)
        
    return qi_dict(qi_id = qi_model_instance.qi_id, 
                   method = qi_model_instance.method,
                   params = qi_model_instance.params, 
                   result = qi_model_instance.result, 
                   error = qi_model_instance.error, 
                   in_process_from = qi_model_instance.in_process_from)



class DBQueue():
    '''
    Contains methods to implement a query of items needed to be processed, 
    using any database backend available in Django.
    
    Abbreviations:
    Query item is 'qi'.
    Every qi is a dictionary with keys, accoding to protocol spec 
    (you could see 'constant' values beginning with 'KEY_' to realize what keys must be in qi.
    '''
    def add_qi(self, qi_id, method, params):
        '''
        Adds qi to the database/queue.
        '''
        #try:
            #assert type(qi_id) == unicode
            #assert type(qi) == unicode
        #except AssertionError:
            #return qi_dict(error=ERROR_WRONG_ARGUMENT)
            
        try:
            q = QIModel(qi_id = qi_id, method = method, params = params, result = None, error = None, in_process_from = None)
            q.save()
            if LOW_RESOURCES_MODE:
                if QIModel.objects.all().count()> MAX_ITEMS_IN_QUEUE:
                    self.clear_queue(time_interval = 3600) #remove older than 1 hour
                    if QIModel.objects.all().count()> MAX_ITEMS_IN_QUEUE:
                        self.clear_queue(time_interval = 600) #remove older than 10 min
                        if QIModel.objects.all().count()> MAX_ITEMS_IN_QUEUE:
                            self.clear_queue() # remove all

            return qimodel_to_dict(q)
        except django.db.IntegrityError:
            return qi_dict(qi_id = qi_id, params = params, method = method, error = ERROR_DUPLICATE_QI_ID)
       

    
    def get_qi(self):
        '''
        Returns some queue item from queue for processing
        '''
        if QIModel.objects.filter(in_process_from = None).count() > 0:
            q = QIModel.objects.filter(in_process_from = None)[0]
            q.in_process_from = int(time.time())
            q.save()
            return qimodel_to_dict(q)
        else:
            return qi_dict(error = ERROR_QUEUE_EMPTY)

    def get_all_qi(self):
        '''
        Returns all entries from queue. For testing purposes only!
        '''
        result = {}
        for q in QIModel.objects.all():
            result[q.qi_id] = qimodel_to_dict(q)

        return result
        
    def add_result(self, qi_id, result):
        try:
            pass
            #assert type(qi_id) == unicode
            #assert type(result) == unicode
        except AssertionError:
            return qi_dict(error = ERROR_WRONG_ARGUMENT)
        
        try:
            q = QIModel.objects.all().get(qi_id = qi_id)
            q.result = result
            q.save()
            return qimodel_to_dict(q)
        except:
            return qi_dict(qi_id = qi_id, error = ERROR_NOT_IN_QUEUE)
        
    def get_result(self, qi_id):
        '''
        Reads result by qi_id and removes qi from query
        '''
        try:
            '''
            If qi with given qi_id exists in queue...
            '''
            q = QIModel.objects.all().get(qi_id = qi_id)
            
            if q.result!=None:
                result = qimodel_to_dict(q)
                #delete qi
                q.delete()
                return qimodel_to_dict(q)
            
            elif q.result == None:
                '''                
                Queue item have not been processed yet. Try again later.
                '''
                return qi_dict(qi_id = q.qi_id, method = q.method, params = q.params, error = ERROR_NOT_PROCESSED_YET)
            
        except QIModel.DoesNotExist:
            '''
            There is no such qi
            '''
            return qi_dict(error=ERROR_NOT_IN_QUEUE)


    def clear_queue(self, time_interval = 0):
        '''
        Removes all entries from queue if (time_interval == 0)

        @time_interval: 
        if 
            time_interval (in seconds) is in range(1, sys.maxint), 
        then 
            clear all entries, that were previously sent for processing time_interval or earlier in the past
        '''
        try:
            assert (type(time_interval) == float) or (type(time_interval) == int)
            assert (time_interval>=0) and (time_interval<=sys.maxint)
        except AssertionError:
            return qi_dict(error = ERROR_WRONG_ARGUMENT)
        
        if time_interval == 0:
            QIModel.objects.all().delete()
            
        elif time_interval > 0:
            #clear all entries, that were previously sent for processing time_interval or earlier in the past
            for q in QIModel.objects.filter(in_process_from__isnull=False, in_process_from__lt=time_interval):
                q.delete()
        #return empty qi dictionary
        return qi_dict(result =  RESULT_OK)

    def resend_qi(self, qi_id):
        '''
        Marks all old entries to resend for processing
        '''
        try:
            q = QIModel.objects.all().get(qi_id = qi_id)
            q.in_process_from = None
            q.save()
            return qimodel_to_dict(q)
        except:
            return qi_dict(error=ERROR_NOT_IN_QUEUE)
          
    
    
    
    def resend_all(self):
        '''
        Marks all old entries to resend for processing
        '''
        for q in QIModel.objects.filter(in_process_from__isnull=False):
            q.in_process_from = None
            q.save()
            
        return qi_dict(result =  RESULT_OK)
    
    def queue_length(self):
        '''
        Elements in queue. For testing purposes only.
        '''
        return qi_dict(result=QIModel.objects.all().count())
    
    
                
