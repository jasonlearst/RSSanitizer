import re
import requests
import flask
from lxml import etree
from flask import Flask, render_template, Response, make_response

app = Flask(__name__)
XKCD_RSS_URL = "https://podcast.wandwmusic.nl/podcast.php"
XKCD_ATOM_URL = "https://www.xkcd.com/atom.xml"

XKCD_REQ_UA = 'xkcdmobile-feed-proxy jeremie@miserez.org'
XKCD_REQ_TIMEOUT=2.0

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

REPLACEMENTS = {
u"http://xkcd.com": u"http://m.xkcd.com",
u"https://xkcd.com": u"https://m.xkcd.com",
u"http://www.xkcd.com": u"http://m.xkcd.com",
u"https://www.xkcd.com": u"https://m.xkcd.com",
}

@app.errorhandler(Exception)
def all_exception_handler(error):
    flask.abort(Exception)

@app.errorhandler(404)
def all_exception_handler(error):
    return render_template('index.html'), 404

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/rss.xml", methods=['GET'])
def rss():
    return proxy_xkcd(XKCD_RSS_URL)

@app.route("/atom.xml", methods=['GET'])
def atom():
    return proxy_xkcd(XKCD_ATOM_URL)

def proxy_xkcd(feed_url):
    try:
        req_headers = {}
        for h,v in flask.request.headers:
            if h in COPY_HEADERS:    
                req_headers[h] = v
        req_headers['Accept'] = '*/*' # needed, otherwise xkcd doesnt send etag header!?!
        req_headers['User-Agent'] = XKCD_REQ_UA

        req = requests.Request('GET', feed_url, headers=req_headers).prepare()
        r = requests.Session().send(req, verify=False, timeout=XKCD_REQ_TIMEOUT)
        return get_modified_response(r)
    except Exception as e:
        print(e)
        flask.abort(e)

def get_modified_response(r):
    new_content = r.content
    my_parser = etree.XMLParser(recover=True)
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