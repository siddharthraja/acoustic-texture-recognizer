from flask import Flask, url_for, request, make_response
from flask.ext.cors import CORS
app = Flask(__name__)
cors = CORS(app)

option=0
opt=1
li = ['voldown', 'volup', 'next', 'prev']

@app.route('/')
def api_root():
    option = opt-1
    return li[option]

@app.route('/1')
def api_articles():
    return li[opt]

@app.route('/articles/<articleid>')
def api_article(articleid):
    return 'You are reading ' + articleid

if __name__ == '__main__':
    app.run()