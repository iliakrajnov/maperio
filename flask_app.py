from flask import Flask, render_template, request, url_for
from data import db_session, add_user_api, users, sessions
import time
import json
import hashlib
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



def main():
    db_session.global_init("db/data.sqlite")
    app.register_blueprint(add_user_api.blueprint)
    app.run()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', style=url_for('static', filename='css/main.css'))
    elif request.method == 'POST':
        print(add_user_api.get_users(request.form["user"]))
        if add_user_api.get_users(request.form["user"]) == '{}':
            nick = request.form["user"].lower()
            user = users.User()
            user.name = nick
            user.hashed_password = hashlib.md5(bytes(request.form["hashed_password"], 'utf-8')).hexdigest()

            session = db_session.create_session()
            session.add(user)
            session.commit()

            sess = sessions.Session()
            sess.name = nick
            sess.hashed = hashlib.md5(bytes(nick + str(time.time()), 'utf-8')).hexdigest()
            session = db_session.create_session()
            session.add(sess)
            session.commit()
            return render_template('index.html', style=url_for('static', filename='css/main.css'), text_in_login="OK")
        else:
            nick = request.form["user"]
            d = dict(json.loads(add_user_api.get_users(nick)))
            if hashlib.md5(bytes(request.form["hashed_password"], 'utf-8')).hexdigest() == str(d[str(nick)]):
                sess = sessions.Session()
                sess.name = nick
                sess.hashed = hashlib.md5(bytes(nick + str(time.time()), 'utf-8')).hexdigest()
                session = db_session.create_session()
                session.add(sess)
                session.commit()
                return render_template('index.html', style=url_for('static', filename='css/main.css'), text_in_login="Успешно!")
            else:
                return str(hash(request.form["hashed_password"])) + ' ' + str(d[str(nick)])
                return render_template('index.html', style=url_for('static', filename='css/main.css'), text_in_login="Логин занят, пароль неверный")

@app.route('/api/geolocation')
def geo():
    return render_template('get_geo.html')

@app.route('/score', methods=['GET', 'POST'])
def score():
    if request.method == 'GET':
        session = db_session.create_session()
        sb = dict()
        k = 0
        for user in session.query(users.User).all():
            k += 1
            if user.score in sb:
                sb[user.score] = sb[user.score] + ', ' + user.name
            else:
                sb[user.score] = user.name
        return render_template('score.html', style=url_for('static', filename='css/score.css'), sb=sb,
                               sb2=sorted(sb, reverse=True)[:32])
    elif request.method == 'POST':
        session = db_session.create_session()
        ok = 0
        for s in session.query(sessions.Session).all():
            print(s.hashed)
            if s.hashed == request.form["session"] and s.name == request.form["user"].lower():
                ok = 1
                break

        if ok:
            session = db_session.create_session()
            session.query(users.User).filter_by(name=request.form["user"].lower()).update({'score': int(request.form["score"])})
            session.commit()
            return 'ok'
        else:
            return 'False session id'


@app.route('/store')
def store():
    return render_template('store.html', style=url_for('static', filename='css/main.css'))



if __name__ == '__main__':
    main()