from django.db import models

class QIModel(models.Model):
    
    qi_id = models.TextField(unique=True, null=False)
    
    method = models.TextField(null=True)
    params = models.TextField(null=True)
    result = models.TextField(null=True)
    error = models.TextField(null=True)
    
    in_process_from = models.IntegerField(null=True)