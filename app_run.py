import os, sys, re, json, time
from flask import Flask, request, abort, jsonify, Response

from ytube import fetch_meta, url_by_term, shorten_url

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
        title, url, duration, *_ = fetch_meta(url_by_term(keyword))
    if vid:
        title, url, duration, *_ = fetch_meta('https://www.youtube.com/watch?v=' + vid)
    return jsonify(shorten_url(url))

@app.route("/yt", methods=['GET'])
def get_yt_source():
    term = request.args.get('term')
    vid = request.args.get('vid')
    if term:
        data = {
            'songs': [{
                'name': title,
                'link': url
            } for title, url, duration in [fetch_meta(u) for u in urls_by_term(keyword)[:10]]]
        }
    if vid:
        title, url, duration = fetch_meta('https://www.youtube.com/watch?v=' + vid)
        data = {'songs': [{'name': title, 'link': url}]}

    return Response(json.dumps(data), mimetype='application/json')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port)
#{{{ vim:fdm=marker:ts=2
#}}}
