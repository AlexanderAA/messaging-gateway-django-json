__author__="Aliaksandr Abushkevich"
__version__ = "0.0.1"

import datetime
import jsonrpclib
import inspect
from custom.demjson import decode, encode

class TestJSON():
    def __init__(self, request_patterns, server_url):
        self.proxy = jsonrpclib.ServerProxy(server_url, verbose=5)
        for rq in request_patterns:
            rq.append(getattr(self.proxy, str(rq[0]))(*rq[1]))
        self.patterns = request_patterns
    
request_patterns_correct = [
                ['task_add',['anothertask']],
                ['task_delete',[36]],
                ['task_done',[35]],
                ['task_undone',[1]],
                ['task_list',[]],
                ['task_history',[30]],
                ]
    
request_patterns_incorrect = [
                ['task_add',[23243]],
                ['task_delete',[]],
                ['task_done',[]],
                ['task_undone',[]],
                ['task_list',[]],
                ['task_history',['zz']],
                ['task_history',[]],
                ['task_history',[1,2,'efder']],
                ]    
        
request_patterns_boundary = [
                ['task_add',['anothertask']],
                ['task_delete',[1]],
                ['task_done',[1]],
                ['task_undone',[1]],
                ['task_list',[]],
                ['task_history',[30]],
                ]

all_patterns = {'correct patterns':request_patterns_correct, 
                'incorrect patterns':request_patterns_incorrect, 
                'boundary tests':request_patterns_boundary}

if __name__ == "__main__":
    for patterns in all_patterns.items():
        print '\n\n=== ' + str(patterns[0]).capitalize() + ' ===\n'
        #t = TestJSON(patterns[1], "http://blog.extensibl.com/microtasks/json/")
        t = TestJSON(patterns[1], "http://localhost:8000/microtasks/json/")
        for p in t.patterns:
            print '>>>\n' + str(p) + '\n<<<'

