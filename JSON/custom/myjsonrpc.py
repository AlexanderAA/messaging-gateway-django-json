#from JSON.custom.demjson import encode, decode
from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import simplejson 
import time
        
class JSONRPCMethod(object):

    def __init__(self, method):
        self.method = method
        self.__rpc__ = True

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def get_args(self):
        from inspect import getargspec
        args = []
        for a in getargspec(self.method)[0]: 
            if (a != "self"):
                args.append(a)
                
        return args

class JSONRPC(object):

    def __init__(self, rpc_service_class_instance, allow_errors=True, report_methods=True):

        self.rpc_service_instance = rpc_service_class_instance
        self.allow_errors = allow_errors
        self.report_methods = report_methods

        if not hasattr(self.rpc_service_instance, "url"):
            raise Exception("'url' not present in supplied instance")

    def get_public_methods(self):
        methods = []
        for attr in dir(self.rpc_service_instance):
            if hasattr(getattr(self.rpc_service_instance, attr),'__rpc__'):
                methods.append(attr)
        return methods

    def generate_smd(self):

        smd = {
            "serviceType": "JSON-RPC",
            "serviceURL": self.rpc_service_instance.url,
            "methods": []
        }

        if self.report_methods:
            smd["methods"] = [
                {"name": method, "parameters": getattr(self.rpc_service_instance, method).get_args()} \
                for method in self.get_public_methods()
            ]

        return HttpResponse(simplejson.dumps(smd), content_type = 'application/json')

 
    def dispatch(self, method, params):
        #assert (type(params) == dict) or (type(params) == list)
        #if hasattr(self.rpc_service_instance, "dispatch") and callable(self.rpc_service_instance.dispatch):
            #return self.rpc_service_instance.dispatch(method, params)
        
        if method in self.get_public_methods():
            #func_arg_names = getattr(self.rpc_service_instance, method).get_args()
            #func_args = []
            #for arg in func_arg_names:
            #    func_args.append(params.get(arg, None))
            if type(params) == dict:
                result = getattr(self.rpc_service_instance, method)(self.rpc_service_instance, **params)
            elif type(params) == list:
                result = getattr(self.rpc_service_instance, method)(self.rpc_service_instance, *params)
                
            return result 
        else:
            return "no such method"

    def serialize(self, raw_post_data):
        #json_str = raw_post_data.keys()[0]
        #post_data = decode(json_str)
        post_data = simplejson.loads(raw_post_data)
        request_id = post_data.get("id", 0)
        request_method = post_data.get("method")
        request_params = post_data.get("params", [])
        response = {"id": request_id}
        
        try:
            response.__setitem__("result", self.dispatch(request_method, request_params))
        except:
            if self.allow_errors:
                from sys import exc_type, exc_value
                response.__setitem__("error", "%s: %s" % (exc_type, exc_value))
                response.__setitem__("result", None)
            else:
                response.__setitem__("error", "error")
                response.__setitem__("result", None)
        return response

    def handle_request(self, request):
        data_to_process = {}
        if request.method == "POST":
            data_to_process = request.raw_post_data
            
        if len(data_to_process) > 0: 
            self.time0 = time.time()
            response = self.serialize(data_to_process)
            self.time1 = time.time()
            time_string = '%.4f' % (self.time1 - self.time0)
            response.__setitem__('time_to_process', time_string)
            #return HttpResponse(encode(response), content_type="application/json")
            return HttpResponse(simplejson.dumps(response), content_type="application/json")
        
        return self.generate_smd()
