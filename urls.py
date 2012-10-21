from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MetaMagazine.views.home', name='home'),
    # url(r'^MetaMagazine/', include('MetaMagazine.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Django built-in users system
    url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
    
    # Static files:
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/css'}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/js'}),    
    url(r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/img'}),        
    
    url(r'^magazines/add', 'metaapp.views.add_channel'),
    url(r'^magazines/(?P<user>.*)$', 'metaapp.views.show_magazine'),
    url(r'^magazines$', 'metaapp.views.show_magazines'),

    url(r'^channels$', 'metaapp.views.show_channels'),
    
    url(r'^news/(?P<newsid>.*)$', 'metaapp.views.show_news'),        
    url(r'^api/news/(?P<newsid>.*)$', 'metaapp.views.show_news_api'),        
    
    url(r'^changetitle$','metaapp.views.changetitle'),
    
    url(r'^update/(?P<idchannel>.*)$', 'metaapp.views.update_channel'),    
    url(r'^delete/(?P<idchannel>.*)$', 'metaapp.views.delete_channel'),    
    url(r'^conf$', 'metaapp.views.conf'),    

    url(r'^$', 'metaapp.views.root'),
    
)
