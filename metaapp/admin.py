from django.contrib import admin
from metaapp.models import Magazine
from metaapp.models import Channel
from metaapp.models import News
from metaapp.models import Url
from metaapp.models import Img

admin.site.register(Magazine)
admin.site.register(Channel)
admin.site.register(News)
admin.site.register(Url)
admin.site.register(Img)
