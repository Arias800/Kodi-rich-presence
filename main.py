#-*- coding: utf-8 -*-
import urllib.request
try:
    from pypresence import Presence
except ImportError as e:
    import os
    os.system('pip install pypresence')
    from pypresence import Presence
    
import re, time, random, unicodedata, json, base64

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
port = config['Web Interface']['Port']
credential = str(config['Web Interface']['Credential'])
if not 'username:password' in credential:
    ids = base64.b64encode(bytes(credential,encoding='utf8'))
    ids = 'Basic ' + ids.decode('utf-8')
else:
    ids = False
apiMovieKey = config['API']['tmdbApi']

client_id = '527810733317029889'
RPC = Presence(client_id)
RPC.connect()
icon = ''
oldTitle = ''

def getTitle():
    url ='http://localhost:'+port+'/jsonrpc?request={%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Player.GetItem%22,%20%22params%22:%20{%20%22properties%22:%20[%22title%22,%20%22album%22,%20%22artist%22,%20%22season%22,%20%22episode%22,%20%22duration%22,%20%22showtitle%22,%20%22tvshowid%22,%20%22thumbnail%22,%20%22file%22,%20%22fanart%22,%20%22streamdetails%22],%20%22playerid%22:%201%20},%20%22id%22:%20%22VideoGetItem%22}'
    if ids != False:
        headers = {'Authorization' : ids}
        req = urllib.request.Request(url, None,headers)
        with urllib.request.urlopen(req) as response:
           html = response.read()
    else:
        with urllib.request.urlopen(url) as response:
           html = response.read()        

    getAddon = re.findall('"file":"plugin://plugin..+?\.(.+?)/',str(html))
    
    if 'vstream' in getAddon:
        icon = 'vstream'
    else:
        icon = 'kodi'
        
    getTitle = re.findall('"label":"(.+?)"',str(html))
    
    try:
        Title, rest = getTitle[0].replace('[COLOR lightcoral]','').replace('[/COLOR]','').split('[COLOR skyblue]')
    except ValueError:
        old = str(getTitle[0])
        return False,False

    splitTitle = re.match('(?:S(.+?)E(.+?) |)([^"]+)',Title)
    return splitTitle, icon

def getGenreSerie(Title1):
    Title1 = Title1.replace(' ','-')
    if Title1.endswith('--'):
        Title1 = Title1[:-2]
    elif Title1.endswith('-'):
        Title1 = Title1[:-1]
    with urllib.request.urlopen('https://www.thetvdb.com/series/'+Title1) as response:
       html = response.read()
    genre = re.findall('<strong>Genres</strong>.+?<span>(.+?)</span>',str(html))
    return genre

def getGenreMovie(Title1):
    with urllib.request.urlopen('https://api.themoviedb.org/3/search/movie?api_key=' +apiMovieKey+ '&language=fr-FR&query='+ Title1.replace(' ','+')) as response:
        html = response.read()
    idMovie = re.findall('"results":.+?"id":(.+?),',str(html))
    if idMovie:
        data = urllib.request.urlopen('https://api.themoviedb.org/3/movie/'+str(idMovie[0])+'?api_key='+apiMovieKey+'&language=fr-FR').read()
        jsonData = json.loads(data)
        genre = jsonData["genres"]
        genre1 = re.findall("name.+?'(.+?)'",str(genre))
        return genre1
    else:
        genre1 = ''
        return genre1
                                
while True:
    Title, icon = getTitle()
    if Title == False and oldTitle != False:
        RPC.update(small_image='kodi', small_text='kodi', large_image='kodi', large_text='kodi', details=str('Watch Nothing'))
        oldTitle = False
        time.sleep(15)
    else:
        time.sleep(15)
        
    if Title == False and oldTitle == False:
        pass
    elif str(Title[0]) == str(oldTitle):
        time.sleep(15)
    else:
        Title1 = str(Title.group(3))
        if '[' in Title1:
             Title1 = re.sub('([\[].+?[\]])','',Title1)
        if Title.group(1) == None:
            if not 'ApiKeyHere' in apiMovieKey:
                genre = getGenreMovie(Title1)
            else:
                genre = ['unknow']
            if genre == '':
                genre = ['unknow']
            Title1 = unicodedata.normalize('NFD', Title1).encode('ascii', 'ignore').decode("unicode_escape").encode("latin1").decode()
            RPC.update(small_image='kodi', small_text='kodi', large_image=icon, large_text=icon, details=Title1, state=str(','.join(genre)))
        else:
            genre = getGenreSerie(Title1)
            if not genre:
                genre = ['unknow']
            Title1 = unicodedata.normalize('NFD', Title1).encode('ascii', 'ignore').decode("unicode_escape").encode("latin1").decode()
            RPC.update(small_image='kodi', small_text='kodi', large_image=icon, large_text=icon, details='S' + Title.group(1) + ' E' + Title.group(2) + ' ' +Title1, state=str(','.join(genre)))
        oldTitle = str(Title[0])
        time.sleep(15)
