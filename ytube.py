import os
import os.path
import shlex
import subprocess

from pprint import pprint

import urllib.request
from urllib import request, parse
from urllib.parse import urlencode, quote_plus

from bs4 import BeautifulSoup

import html
import asyncio
import time

import youtube_dl

def shorten_url(url):
    data = { "url": url }
    tinyURL = 'https://tinyurl.com/api-create.php'
    req = request.Request(
            "{}?{}".format(tinyURL,urlencode(data, quote_via=quote_plus)),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }) # GET
    try:
        short = request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print("""

                """)
        print(url, e)
        print("""

                """)

        raise e
    print(short)
    return short

def extract_vid(url):
    return url[url.find('v=') + 2:]

def to_second(time):
    s = 0
    for l in map(int, time.split(':')):
        s = s * 60 + l
    return s

def playlist_by_id(list_id):
    """
    (title, yurl, aurl, duration)
    """
    playlist = []
    data = fetch_meta(url_by_list_id(list_id), vid=True)
    for _ in range(len(data) // 4):
        title, vid, aurl, duration, *data = data
        playlist.append((title, url_by_vid(vid), aurl, duration))
    if playlist:
        return playlist
    else:
        raise Exception ("Empty playlist or playlist not found")

class Logger(object):
    def __init__(self):
        self.data = []
    def debug(self, msg):
        _ = msg.split()
        if not any([msg.startswith('[download'),
                msg.startswith('[youtube'),
                msg.startswith('[info')]):
            self.data.append(msg)
        elif '[download] Downloading playlist:' in msg:
            YouTubePlugin.playListName = msg[len('[download] Downloading playlist: '):]
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

#geo_bypass:        
#geo_bypass_country:
#https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

def fetch_meta(url, vid=False):
    logger = Logger()
    ydl_opts = {
        'logger': logger,
        'simulate': True,
        'forceurl': True,
        'forcetitle': True,
        'forceduration': True,
        #'forcedescription': True,
        #'dump_single_json': True,
        'quiet': True,
        'format': 'bestaudio/best'
    }
    if vid: ydl_opts['forceid'] = True
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return logger.data

def urls_by_url(url, classname, retry=True):
    print("search url is:", url)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    rtn = ['https://www.youtube.com' + vid['href']
            for vid in soup.findAll('a', href=True, attrs={'class': classname})
            if not vid['href'].startswith("https://")]
    if rtn: return rtn
    elif retry: urls_by_url(url, classname, False)
    else: raise Exception("No song found by the keyword QwQ")

def url_by_list_id(list_id):
    return 'https://www.youtube.com/playlist?list=' + list_id

def url_by_vid(vid):
    return 'https://www.youtube.com/watch?v=' + vid

def urls_by_term(textToSearch):
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    return urls_by_url(url, 'yt-uix-tile-link')

def url_by_term(textToSearch):
    return urls_by_term(textToSearch)[0]

cache_list = []
def next_url(url):
    rtn = urls_by_url(url, 'content-link spf-link yt-uix-sessionlink spf-link')
    # prevent repeat recommendation
    while len(rtn) > 1:
        if rtn[0] not in cache_list: break
        else: rtn.pop(0)
    return rtn[0]

if __name__ == '__main__':
    print([fetch_meta(u) for u in urls_by_term('魚')[:10]])

