import os.path
import re, os, sys, shlex, subprocess

from pprint import pprint

import urllib.request
from urllib import request, parse
from urllib.parse import urlencode, quote_plus

from bs4 import BeautifulSoup

import html, time, json, asyncio

import youtube_dl
from youtube_search import YoutubeSearch

DEFAULT_HEADER = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

def shorten_url(url):
    data = { "url": url }
    tinyURL = 'https://tinyurl.com/api-create.php'
    req = request.Request(
            "{}?{}".format(tinyURL,urlencode(data, quote_via=quote_plus)),
            headers=DEFAULT_HEADER) # GET
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
        #elif '[download] Downloading playlist:' in msg:
        #    YouTubePlugin.playListName = msg[len('[download] Downloading playlist: '):]
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
        'format': 'bestaudio'
    }
    if vid: ydl_opts['forceid'] = True
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return logger.data

#def urls_by_url(url, classname, retry=True):
#    print("search url is:", url)
#    response = urllib.request.urlopen(url)
#    html = response.read()
#    soup = BeautifulSoup(html, 'html.parser')
#    rtn = ['https://www.youtube.com' + vid['href']
#            for vid in soup.findAll('a', href=True, attrs={'class': classname})
#            if not vid['href'].startswith("https://")]
#    if rtn: return rtn
#    elif retry: urls_by_url(url, classname, False)
#    else: raise Exception("No song found by the keyword QwQ")

#def infos_by_url(url, classname, retry=True):
#    print("search url is:", url)
#    response = urllib.request.urlopen(url)
#    html = response.read()
#    soup = BeautifulSoup(html, 'html.parser')
#    with open("out.html", 'wb') as w:
#        w.write(html)
#    rtn = [{
#            'name': vid['title'],
#            'link': 'https://www.youtube.com' + vid['href']
#            } for vid in soup.findAll('a', href=True, attrs={'class': classname})
#            if not vid['href'].startswith("https://")]
#    if rtn: return rtn
#    elif retry: urls_by_url(url, classname, False)
#    else: raise Exception("No song found by the keyword QwQ")


def url_by_list_id(list_id):
    return 'https://www.youtube.com/playlist?list=' + list_id

def url_by_vid(vid):
    return 'https://www.youtube.com/watch?v=' + vid

def youtube_id_parser(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """
    try:
        # python 3
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        # python 2
        from urlparse import urlparse, parse_qs

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if not query or not query.hostname:
        return None

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError

def urls_by_term(textToSearch):

    yid = youtube_id_parser(textToSearch)
    if yid:
        textToSearch = yid
    else: print('not match')

    if re.search(re.compile(r'[a-zA-Z0-9_-]{11}'), textToSearch):
        url = 'https://www.youtube.com/watch?v=' + textToSearch
        req = request.Request(url, headers=DEFAULT_HEADER)
        if request.urlopen(req).getcode() == 200:
            return [url]

    results = YoutubeSearch(textToSearch, max_results=10).to_dict()
    return ['https://www.youtube.com' + e['url_suffix'] for e in results]

def title_by_vid(vid):
    url = 'https://youtube.com/get_video_info?video_id=' + vid
    req = request.Request(url, headers=DEFAULT_HEADER)
    resp = request.urlopen(req)
    ret = resp.read().decode('utf-8')
    ret = parse.parse_qs(ret)
    print(ret.keys())
    if 'ok' in ret['status']:
        data = ret['player_response'][0]
        return json.loads(data)['videoDetails']['title']
    elif 'fail' in ret['status']:
        return None

def infos_by_term(textToSearch):

    vid = youtube_id_parser(textToSearch)

    if vid:
        textToSearch = vid
    if re.search(re.compile(r'[a-zA-Z0-9_-]{11}'), textToSearch):
        title = title_by_vid(textToSearch)
        url = 'https://www.youtube.com/watch?v=' + textToSearch
        if title: return [{ 'name': title, 'link': url}]

    results = YoutubeSearch(textToSearch, max_results=10).to_dict()
    return [{ 'name': e['title'], 'link': 'https://www.youtube.com' + e['url_suffix'] } for e in results]

def url_by_term(textToSearch):
    try:
        c = urls_by_term(textToSearch)[0]
        return c
    except Exception as e:
        return []

cache_list = []
def next_url(url):
    return None
    #rtn = urls_by_url(url, 'content-link spf-link yt-uix-sessionlink spf-link')
    ## prevent repeat recommendation
    #while len(rtn) > 1:
    #    if rtn[0] not in cache_list: break
    #    else: rtn.pop(0)
    #return rtn[0]

if __name__ == '__main__':
    #term = sys.argv[1]
    #urls = infos_by_term(term)
    #urls = [u for u in urls if 'list' not in u]
    #data = {
    #        'songs': [{
    #            'name': title,
    #            'link': url
    #        } for title, url, duration in [fetch_meta(u) for u in urls[:5]]]
    #    }
    #print(data)
    #print(urls)
    print(infos_by_term('沒離開過'))
