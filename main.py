#-*- coding: utf-8 -*-
import urllib.request
try:
    from pypresence import Presence
except ImportError as e:
    import os
    os.system('pip install pypresence')
    from pypresence import Presence
    
import re, time, random, unicodedata, json

client_id = '527810733317029889'
RPC = Presence(client_id)
RPC.connect()
icon = ''
oldTitle = ''

def getTitle():
    with urllib.request.urlopen('http://localhost:8080/jsonrpc?request={%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Player.GetItem%22,%20%22params%22:%20{%20%22properties%22:%20[%22title%22,%20%22album%22,%20%22artist%22,%20%22season%22,%20%22episode%22,%20%22duration%22,%20%22showtitle%22,%20%22tvshowid%22,%20%22thumbnail%22,%20%22file%22,%20%22fanart%22,%20%22streamdetails%22],%20%22playerid%22:%201%20},%20%22id%22:%20%22VideoGetItem%22}') as response:
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

    splitTitle = re.match('(?:S(.+?)E(.+?) |)([^"]+) ',Title)
    return splitTitle, icon
    
while True:
    Title, icon = getTitle()
    if Title == False and oldTitle != False:
        print(RPC.update(small_image='kodi', small_text='kodi', large_image='kodi', large_text='kodi', details=str('Watch Nothing')))
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
        Title1 = unicodedata.normalize('NFD', Title1).encode('ascii', 'ignore').decode("unicode_escape").encode("latin1").decode()
        if Title.group(1) == None:
            print(RPC.update(small_image='kodi', small_text='kodi', large_image=icon, large_text=icon, details=Title1))
        else:
            print(RPC.update(small_image='kodi', small_text='kodi', large_image=icon, large_text=icon, details=Title1, state=str('Saison ' + Title.group(1) + ' Episode ' + Title.group(2))))
        oldTitle = str(Title[0])
        time.sleep(15)
