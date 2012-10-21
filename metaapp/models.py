from django.db import models

# Create your models here.
class Magazine(models.Model):
   user = models.TextField(primary_key=True)
   title = models.TextField()
   
class Channel(models.Model):
   href = models.TextField()
   last = models.DateField()
   limit = models.IntegerField()
   magazine = models.ForeignKey(Magazine)
   
class News(models.Model):
   text = models.TextField()
   href = models.TextField()
   channel = models.ForeignKey(Channel)

class Url(models.Model):
   href = models.TextField()
   extract = models.TextField()
   video = models.TextField()
   news = models.ForeignKey(News)
    
class Img(models.Model):
   src = models.TextField()
   url = models.ForeignKey(Url)
