from django.db import models

class message(models.Model):
    def __unicode__(self):
        return self.message
    username = models.CharField(max_length=30)
    time = models.CharField(max_length=35)
    message = models.CharField(max_length=1000)
