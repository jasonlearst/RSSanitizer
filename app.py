import re
import requests
import flask
from lxml import etree
from flask import Flask, render_template, Response, make_response

app = Flask(__name__)
WW_RSS_URL = "https://podcast.wandwmusic.nl/podcast.php"

FEED_REQ_UA = 'ww-rssanitizer jason@jasonlearst.com'
FEED_REQ_TIMEOUT=2.0

COPY_HEADERS = [
'Last-Modified', 
'Date', 
'Expires', 
'ETag',
'Cache-Control',
'Age',
'If-Modified-Since',
'If-None-Match',
'If-Unmodified-Since',
]

@app.errorhandler(Exception)
def all_exception_handler(error):
    flask.abort(Exception)

@app.errorhandler(404)
def not_available_handler(error):
    return render_template('index.html'), 404

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/rss.xml", methods=['GET'])
def rss():
    return proxy_rss(WW_RSS_URL)

def proxy_rss(feed_url):
    try:
        req_headers = {}
        for h,v in flask.request.headers:
            if h in COPY_HEADERS:    
                req_headers[h] = v
        req_headers['Accept'] = '*/*' # needed, otherwise xkcd doesnt send etag header!?!
        req_headers['User-Agent'] = FEED_REQ_UA

        req = requests.Request('GET', feed_url, headers=req_headers).prepare()
        r = requests.Session().send(req, verify=False, timeout=FEED_REQ_TIMEOUT)
        return get_modified_response(r)
    except Exception as e:
        print(e)
        flask.abort(e)

def get_modified_response(r):
    new_content = r.content
    my_parser = etree.XMLParser(recover=True) # from SO: https://stackoverflow.com/a/59645304
    xml = etree.fromstring(new_content, parser=my_parser)
    cleaned_xml_string = etree.tostring(xml)

    resp = make_response(cleaned_xml_string, r.status_code) # use status code of request
    resp.mimetype = "text/xml" # both rss/atom feeds use same text/xml utf-8 content type
    for h in COPY_HEADERS:
        if h in r.headers:
            resp.headers[h] = r.headers[h]
    return resp

application = app
if __name__ == "__main__":
#    application.run(debug=True)
    application.run()