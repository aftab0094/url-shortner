from flask import Flask, url_for, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

def generate_short_url(length=6):
    text = string.digits + string.ascii_letters
    return ''.join(random.choice(text) for _ in range(length))

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String, unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Url {self.short_url}>'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        given_url = request.form['long_url']
        short_url = generate_short_url()

        while Url.query.filter_by(short_url=short_url).first():
            short_url = generate_short_url()

        _url = Url(url=given_url, short_url=short_url)

        try:
            db.session.add(_url)
            db.session.commit()
            return render_template('index.html', short_url=short_url, long_url=given_url)
        except Exception as e:
            return e
    else:
        return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    _url = Url.query.filter_by(short_url=short_url).first()
    if _url is None:
        return f'Error: URL with short URL {short_url} not found.', 404
    else:
        return redirect(_url.url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')