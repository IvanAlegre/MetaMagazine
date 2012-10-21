# -*- coding: utf-8 -*-

# Create your views here.
from django.core.context_processors import csrf
from django.http import HttpResponse,HttpResponseNotFound
from django.shortcuts import render_to_response
from beautifulsoup import BeautifulSoup
import models
import feedparser
import datetime
import re
import urllib2
from django.template import RequestContext, loader
import random
from django.contrib.auth.models import User

def root(request):
    print request.user.username
    
    # Choose one random magazine:
    magas = models.Magazine.objects.all()
    if magas: # There is magazine(s)
        randindex = random.randint(0,len(magas)-1)
    
        t = loader.get_template('root.html')
        c = RequestContext(request, {   'title': magas[randindex].title,
                                                'own': magas[randindex].user==request.user.username,
                                                'usuario': magas[randindex].user,
                                                'login': getUser(request),
                                                'channels': models.Channel.objects.filter(magazine = magas[randindex])})
        return HttpResponse(t.render(c))    
    else:
        t = loader.get_template('root.html')
        c = RequestContext(request, {   'title': 'No hay ninguna revista creada',
                                                'usuario': '',
                                                'login': getUser(request),})
        return HttpResponse(t.render(c))    
        
def changetitle(request):
    if request.method == 'POST':
        if request.user.is_authenticated():
            try:
                maga = models.Magazine.objects.get(user=request.user.username)
                maga.title = request.POST['title']
                maga.save()
                
                success = u'Modificado correctamente <a href="/magazines/'+ request.user.username +'">volver</a>'
            
            except models.Magazine.DoesNotExist:
                success = u'Todavía no has creado tu revista'

        else:
            success = u'No deberías estar aquí, <a href="/">vuelve</a>'
    else:
        success = u''

    t = loader.get_template('changetitle.html')
    c = RequestContext(request, { 'success' : success ,
        'login': getUser(request)})
    return HttpResponse(t.render(c))        
        
def show_magazines(request):
    t = loader.get_template('magazines.html')
    c = RequestContext(request, {   'magazines': models.Magazine.objects.all(),
                                            'user': '',
                                            'login': getUser(request),})
    return HttpResponse(t.render(c))    
    
def show_channels(request):
    t = loader.get_template('channels.html')
    c = RequestContext(request, {   'channels': models.Channel.objects.all(),
                                            'user': '',
                                            'login': getUser(request),})
    return HttpResponse(t.render(c))    

def show_news(request, newsid):
    news = models.News.objects.get(pk=newsid)
    
    t = loader.get_template('news.html')
    c = RequestContext(request, {
        'new': news,
        'login': getUser(request),
    })
    return HttpResponse(t.render(c))

def show_news_api(request, newsid):
    news = models.News.objects.get(pk=newsid)

    t = loader.get_template('apinews.html')
    c = RequestContext(request, {
        'new': news
    })
    return HttpResponse(t.render(c))


def show_magazine(request, user):
    # Try to retrieve magazine:
    try:
        # Check if exists, if so, doesn't update
        maga = models.Magazine.objects.get(user = user)

        t = loader.get_template('magazine.html')
        print user
        c = RequestContext(request, {   'title': maga.title,
                                                'own': user==request.user.username,
                                                'usuario': user,
                                                'login': getUser(request),
                                                'channels': models.Channel.objects.filter(magazine = maga)})
        return HttpResponse(t.render(c))
    
    # If doesn't:
    except(models.Magazine.DoesNotExist):
        # Si visito por primera vez mi revista se crea, si visito una que no existe, no
        if request.user.username == user:
            # Create magazine:
            maga = models.Magazine( user = user,
                                    title = 'Title')
            maga.save()
            t = loader.get_template('magazine.html')
            c = RequestContext(request, {   'title': maga.title,
                                                    'own': user==request.user.username,
                                                    'usuario': user,
                                                    'login': getUser(request),
                                                    'channels': models.Channel.objects.filter(magazine = maga)})
            return HttpResponse(t.render(c))
        else: # Visito otra revista que no existe de la que no soy creador. No hago nada
            t = loader.get_template('magazine.html')
            c = RequestContext(request, {   'title': 'La revista que buscas no existe',
                                                    'own': [],
                                                    'login': getUser(request),
                                                    'channels': []})
            return HttpResponse(t.render(c))
            
    


def invalid_limit(request):
    # Lo hago sin render_to_response porqué peta con el csrf
    t = loader.get_template('user.html')
    c = RequestContext(request, { 'success' : 'El límite introducido no es válido. Introduce un número positivo menor de 10' })
    return HttpResponse(t.render(c))

# Add a channel
def add_channel(request):
    if request.method == 'POST':
        try:
            limit = int(request.POST['limit'])
        except ValueError:
            return invalid_limit(request)
        if (limit > 10) or (limit < 1):
            return invalid_limit(request)
        else:
            if request.user.is_authenticated():
                login = request.user.username
                # Get the magazine from the logged user (if exists)
                try:
                    maga = models.Magazine.objects.get(user=login)
                    user = request.POST['user']
                    create_channel(user, maga, request.POST['type'], limit)
                    t = loader.get_template('user.html')
                    c = RequestContext(request, { 'success' : u'Añadido correctamente <a href="/magazines/'+login+'">ver</a>' 
                        , 'login': getUser(request)})
                    return HttpResponse(t.render(c))
                    
                
                except models.Magazine.DoesNotExist:
                    # Lo hago sin render_to_response porqué peta con el csrf
                    t = loader.get_template('user.html')
                    c = RequestContext(request, { 'success' : u'No has creado todavía tu revista, <a href="/magazines/'+login+u'">créala</a>' ,
                        'login': getUser(request)})
                    return HttpResponse(t.render(c))

            else: # No estoy autenticado
                # Lo hago sin render_to_response porqué peta con el csrf
                t = loader.get_template('user.html')
                c = RequestContext(request, { 'success' : 'No estás autenticado',
                     'login': getUser(request)})
                return HttpResponse(t.render(c))                
                    
    else:
        # There is a GET
        t = loader.get_template('user.html')
        # print getUser(request)
        c = RequestContext(request, { 'success' : 'No deberías estar aquí',
             'login': getUser(request)})
        return HttpResponse(t.render(c))      
        
def get_youtube_code(idvideo):
    return '<iframe width="560" height="315" src="http://www.youtube.com/embed/'+ idvideo \
        +'" frameborder="0" allowfullscreen></iframe>'

def create_news(entry, kind, ch):
    # Create News
    text = u''
    if kind=='twitter':
        text = entry.summary # Tweet in summary
    elif kind=="identica":
        text = entry.title # Tweet in title
    elif kind=="youtube":
        text = entry.title # Consider video title 
        
    new = models.News( href = entry['link'],
                       text = text,
                       channel = ch)
    new.save()

    if kind=='youtube':
        # Create only 1 url with the video
        # It was posted in the forum, that we should consider youtube feeds like a 
        # tweet with an url to the youtube video (news)
        
        # First get the id of the video
        idvideo = entry['link'].replace('http://www.youtube.com/watch?v=','').replace('&feature=youtube_gdata','')
        urldb = models.Url(href=entry['link'],
                            extract=entry.summary,
                            video=get_youtube_code(idvideo),
                            news = new)
        urldb.save()
        
    else:
        # Make regex to find http://
        findhttp = re.compile('http://\S+')

        # Get every http page
        urls = findhttp.findall(text)

        # For each url
        for url in urls:
            try:                
                # Make url request. To get real url and initialize 
                req = urllib2.urlopen(url)

                # Test if the link is from youtube. If so, it's not necessary to download the page
                righturl = req.geturl()
                if righturl.startswith('http://youtu.be') or righturl.startswith('http://www.youtube.com/watch?v='):
                    if righturl.startswith('http://youtu.be'): 
                        # http://youtu.be/xfHjEiJaiAs
                        idvideo = righturl.split('/')[-1]
                    elif righturl.startswith('http://www.youtube.com'): 
                        # http://www.youtube.com/watch?v=xfHjEiJaiAs&asfldla&alsfl
                        idvideo = righturl.split('&')[0].replace('http://www.youtube.com/watch?v=','')
                    # Note: http://youtube.com/watch?v=.... redirects to the same with www. So no need to
                    # difference cases
                        
                    # Create url object:
                    urldb = models.Url(href=url,
                                    extract='<a href="'+righturl+'">'+righturl+'</a>',
                                    video = get_youtube_code(idvideo),
                                    news = new)
                    urldb.save()
                else: 
                    data = req.read()

                    # Build BeautifulSoap object (Like in the doc):
                    soup = BeautifulSoup(''.join(data))

                    # Get first p (if there is):
                    ps = soup('p')
                    p = u''
                    if len(ps) > 0:
                        for par in ps:
                            if len(p) < 50 and par.string!=None:
                                p += par.string
        
                    print p
                
                    # Get videos:
                    videos = soup('iframe')
                
                    # Only one with the src in youtube
                    # Attention! This can be horrible for any that knows BeautifulSoup
                    video = None
                    for v in videos:
                        try:
                            if v['src'].startswith('http://www.youtube.com'):
                                video = v
                                break
                        except KeyError:
                            print 'The iframe element doesn\'t have src attribute'
                
                    if video:
                        video = u'<iframe src="'+ video['src'] +\
                            '" width="560" height="315" frameborder="0" allowfullscreen></iframe>'
                    
                    if not video:
                        video = ''

                    # Create Url Record
                    urldb = models.Url( href = url,
                                     extract = p,
                                     # Video has to be extracted
                                     video = video,
                                     news = new)
                    urldb.save()
                    # Get 5 first imgs (if there are):
                    imgs = soup('img')
                
                    # Now we treat the url as the target url (not shorted)
                    url = req.geturl()
                    try:
                        for img in imgs[:5]:
                            imgsrc = img['src']
                        
                            # Now we should realize local urls from global
                            if imgsrc.startswith('/'): # Local from root url
                                # Get the root domain name 
                                dname = url.split('/')[2] # ['http:','','yonkiblog.com','tag','videos']
                                imgsrc = 'http://'+dname+imgsrc
                        
                            elif imgsrc.startswith('http://') or imgsrc.startswith('https://'):
                                # Global url, don't do anything
                                None
                            else: # Starts with something else, local url
                                # Remove last parameter in the url and 
                                print url
                                imgsrc = url.replace(url.split('/')[-1],'') + imgsrc
                            
                            imgdb = models.Img( src = imgsrc,
                                                url = urldb)
                            imgdb.save()
                    except KeyError:
                        print 'La imagen no tiene src'
    
            except urllib2.HTTPError:
                print 'Socket Error on: '+url
            except urllib2.URLError:
                print 'The url doesn\'t go anywhere'
    
        
def get_kind(idchannel):
    # First retrieve the channel
    ch = models.Channel.objects.get(pk=idchannel)
    if ch.href.startswith('https://twitter.com'):
        return 'twitter'
    elif ch.href.startswith('http://identi.ca'):
        return 'identica'
    elif ch.href.startswith('http://gdata.youtube.com'):
        return 'youtube'
    else:
        return None
        
def conf(request):
    if request.user.is_authenticated():
        if request.method=="POST":
            if not request.POST['pwd'] and not request.POST['pwd2']: # There isn't anything in password
                print 'Sin contraseñas'
                if request.POST['name']: 
                    u = User.objects.get(username__exact=request.user.username)
                    u.first_name = request.POST['name']
                    u.save()
                    success = "Nombre cambiado"
                else:
                    success = "Nada que cambiar"

            elif request.POST['pwd']==request.POST['pwd2']:
                if request.POST['name']:
                    u = User.objects.get(username__exact=request.user.username)
                    u.first_name = request.POST['name']
                    u.set_password(request.POST['pwd'])
                    u.save()
                    success="Nombre y contraseña cambiados"
                    
                else:
                    u = User.objects.get(username__exact=request.user.username)
                    u.set_password(request.POST['pwd'])
                    u.save()
                    success = "Contraseña cambiada"
                
            else:
                success = 'Las contraseñas no coinciden'

            t = loader.get_template('conf.html')
            c = RequestContext(request, { 'success' : success ,
                'login': getUser(request)})
            return HttpResponse(t.render(c))        
        else:
            t = loader.get_template('conf.html')
            c = RequestContext(request, { 'success' : '' ,
                'login': getUser(request)})
            return HttpResponse(t.render(c))        
    else:
        t = loader.get_template('user.html')
        c = RequestContext(request, { 'success' : 'No estás logueado' ,
            'login': getUser(request)})
        return HttpResponse(t.render(c))        
        

def delete_channel(request, idchannel):
    # First retrieve the channel
    ch = models.Channel.objects.get(pk=idchannel)
    news = models.News.objects.filter(channel=ch)
    for new in news:
        urls = models.Url.objects.filter(news=new)
        for url in urls:
            imgs = models.Img.objects.filter(url=url)
            for img in imgs:
                img.delete()
            url.delete()
        new.delete()
    ch.delete()

    t = loader.get_template('user.html')
    # print getUser(request)
    c = RequestContext(request, { 'success' : 'Eliminado correctamente <a href="/magazines/'+\
                                            ch.magazine.user+'">volver</a>',
        'login': getUser(request)})
    return HttpResponse(t.render(c))                
    

def update_channel(request, idchannel):
    # First retrieve the channel
    ch = models.Channel.objects.get(pk=idchannel)

    # Search news
    # Parse it
    parse = feedparser.parse(ch.href)

    # In reverse, the first in the list is the most recent
    # So with this, will be the last, When displayed, will be the first
    parse.entries = parse.entries[:ch.limit]
    parse.entries.reverse()
    
    for entry in parse.entries:
        # If the news is already in the db (filter isn't empty list), don't do anything
        if not models.News.objects.filter(href__exact=entry['link']).filter(channel__exact=ch):
            print 'Must be updated'
            kind = get_kind(idchannel)
            create_news(entry, kind, ch)
            
    ch.last = datetime.datetime.now()
    ch.save()

    t = loader.get_template('user.html')
    # print getUser(request)
    c = RequestContext(request, { 'success' : 'Actualizado correctamente <a href="/magazines/'+\
                                            ch.magazine.user+'">volver</a>',
        'login': getUser(request)})
    return HttpResponse(t.render(c))                
            

def create_channel(user, maga, kind, limit):
    # Make url string:
    if kind=="twitter":
        urlparse = 'https://twitter.com/statuses/user_timeline/'+user+'.rss'
    elif kind=="identica":
        urlparse = 'http://identi.ca/'+user+'/rss'
    elif kind=="youtube":
        urlparse = 'http://gdata.youtube.com/feeds/api/videos?max-results=5&alt=rss&author='+user
    else:
        print 'wrong kind'
        
    # Test if is already in the db
    ch = models.Channel.objects.filter(magazine__user__exact=maga.user).filter(href__exact=urlparse)
    if not ch: # Is empty list -> The channel isn't in the db
        
        # Parse it
        parse = feedparser.parse(urlparse)

        # Create channel    
        ch = models.Channel(href = urlparse,
                            last =datetime.datetime.now(),
                            limit = limit,
                            magazine = maga)
        ch.save()

        # print parse

        parse.entries = parse.entries[:limit]
        
        # We insert in reverse, the first news will be the oldest and so on
        parse.entries.reverse()
        
        for entry in parse.entries:
            create_news(entry, kind, ch)

# Get if the user is authenticated to append it to the topbar
def getUser(request):
   if request.user.is_authenticated():
      return "Usuario: "+request.user.username+' (<a href="/logout">Desautenticarme</a>)';
   else:
      return 'Usuario anonimo (<a href="/login">login</a>)'

