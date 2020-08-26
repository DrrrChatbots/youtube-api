import os, sys, re, json, time
from functools import wraps
from flask import Flask, request, abort, jsonify, Response

from ytube import fetch_meta, url_by_term, shorten_url, urls_by_term, infos_by_term

app = Flask(__name__)

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data).replace('"', '')[1:] + ')'
            return app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)

    return decorated_function

"""
YouTube API
"""
@app.route("/youtube", methods=['GET'])
@support_jsonp
def get_youtube_source():
    term = request.args.get('term')
    vid = request.args.get('vid')
    if term:
        #url = ytube.get_top_aurl(ytube.url_by_term(term)[0])
        urls = [u for u in urls_by_term(term) if 'list' not in u]
        title, url, duration, *_ = fetch_meta(urls)
    if vid:
        title, url, duration, *_ = fetch_meta('https://www.youtube.com/watch?v=' + vid)
    return jsonify(shorten_url(url))

def groupby(c, xss):
    rtn = []
    while xss:
        rtn.append(xss[:c])
        xss = xss[c:]
    return rtn

@app.route("/yt", methods=['GET'])
def get_yt_source():
    term = request.args.get('term')
    vid = request.args.get('vid')
    if term:
        urls = [u for u in urls_by_term(term) if 'list' not in u][:5]
        print(urls)
        try:
            tmp = [fetch_meta(u) for u in urls]
            metas = []
            for s in tmp:
                metas = metas + groupby(3, s)
            data = {
                'songs': [{
                    'name': title,
                    'link': url
                } for title, url, duration in metas[:10]]
            }
        except Exception as e:
            print(metas)
            raise e
    return Response(json.dumps(data), mimetype='application/json')

@app.route("/kw", methods=['GET'])
def get_kw_source():
    term = request.args.get('term')
    data = {}
    try:
        infos = infos_by_term(term)
    except Exception as e:
        infos = []
        print(e)
    infos = infos[:10] if infos else []
    if term: data = { 'songs': infos }
    return Response(json.dumps(data), mimetype='application/json')

@app.route("/lk", methods=['GET'])
def get_lk_source():
    urls = [request.args.get('url')]
    tmp = [fetch_meta(u) for u in urls]
    metas = []
    for s in tmp:
        metas = metas + groupby(3, s)
    data = {
        'songs': [{
            'name': title,
            'link': url
        } for title, url, duration in metas[:10]]
    }
    return Response(json.dumps(data), mimetype='application/json')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port)
#{{{ vim:fdm=marker:ts=2
#}}}
