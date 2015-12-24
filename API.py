# -*- coding: cp1251 -*-
from flask import Flask,redirect,request,render_template,jsonify, url_for
import requests
import random
import math
import string
import pyodbc
import json
import uuid
import urllib
import urlparse
from db import *

app = Flask(__name__, static_path='')
    
        
#авторизация
@app.route("/login", methods=['GET', 'POST'])
def login():
    errorInfo = ''
    callback = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if user_pass_check(username,password) == 0:
            errorInfo = "Incorrect login or password"
        else:
            code = ''.join(random.choice(string.lowercase) for i in range(10))
            code_insert(code, username)
            callback = request.form['callback']
            sCallb = urlparse.parse_qs(urlparse.urlparse(callback).query)
            s = read_redirect(str(sCallb['client_id'][0]))
            state = str(sCallb['state'][0])
            return redirect(s + '?code=' + code + ('' if state is None else '&state=' + state), code=302)
    else:
        callback = request.args.get('callback')
    return render_template('auth.html', errorInfo=errorInfo, callback=callback)


#регистрация
def addUser(request):
    username = request.form['username']
    first_name = request.form['fname']
    last_name = request.form['lname']
    tel = request.form['tel']
    email = request.form['email']
    password = request.form['password']
    insert_user(username, first_name, last_name, tel, email, password)
    
    
@app.route("/register", methods=['GET', 'POST'])
def registerForm():
    errorInfo = ''
    if request.method == 'POST':   
        username = request.form['username']
        
        if user_exist(username) == 1:
            errorInfo = ("User '%s' already exists!"% username)
        else:
            addUser(request)
            return 'Are you registered'
    return render_template('register.html', errorInfo=errorInfo)


#получение кода
@app.route("/api/oauth2/authorize", methods=['GET'])
def userCode():
    callback = request.args.get('callback')
      
    response_type = request.args.get('response_type')#code
    client_id = request.args.get('client_id')
    state = request.args.get('state')
    if client_id is None:
        return 'Require client_id.'
    if client_exist(client_id)==0:
        return 'client_id is invalid.'
    s = read_redirect(client_id)
    if response_type is None:
        return redirect(s.decode(encoding='ISO-8859-1', errors='strict') + '?error=invalid_request' +
            ('' if state is None else '&state=' + state), code=302)
    if response_type != 'code':
        return redirect(s.decode(encoding='ISO-8859-1', errors='strict') + '?error=unsupported_response_type' +
            ('' if state is None else '&state=' + state), code=302)
    arr = request.args
    url = "/api/oauth2/authorize?" + urllib.urlencode(arr)
    return redirect ('/login?callback='+urllib.quote_plus(url))#, state=state,client_id=client_id,client_name='Films')
    


# получение access_token
@app.route('/api/oauth2/token', methods=['POST'])
def get_token():
    try:
        type = request.args.get('type')
        client_id = request.args.get('client_id')
        secret_id = request.args.get('secret_id')
    except KeyError:
        return json.dumps({'error': 'invalid_request'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if client_id is None or type is None or secret_id is None:
        return json.dumps({'error': 'invalid_request'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if client_exist(client_id)==0 or client_secret_check(client_id,secret_id)==0:
        return json.dumps({'error': 'invalid_client'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if type == 'code':
        code = request.args.get('code')
        user = code_check(code)
        if user == 0:
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

    elif type == 'refresh_token':
        try:
            refresh_token = request.args.get('refresh_token')
        except KeyError:
            return json.dumps({'error': 'invalid_request'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        user = refresh_token_check(refresh_token)
        if user == 0:
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
        i = expired_check(refresh_token)
        if i==0:
            return json.dumps({'error': 'invalid_token'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
        expired_refresh(refresh_token)
        return '', 200

    access_token = ''.join(random.choice(string.lowercase) for i in range(30))
    expire_time = 'DATEADD(minute, +10, GETDATE())'
    refresh_token = ''.join(random.choice(string.lowercase) for i in range(30))
    insert_token(user, access_token, expire_time, refresh_token)
    return json.dumps({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 300,
        'refresh_token': refresh_token,
    }), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cache-Control': 'no-store',
        'Pragma': 'no-cache',
    }



########################################

#метод получения статуса пользователя авторизован/не авторизован
@app.route("/api/status")
def myStatus():
    return None


#метод получения информации о пользователе
@app.route("/api/me", methods=["GET"])
def me():
    access_token = request.headers.get('Authorization', '')[len('Bearer '):]
    Info = get_me(access_token)

    if not Info:
        return json.dumps({'error': 'invalid_token'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
    return jsonify(UserName=Info.UserName,
                FirstName=Info.FirstName,
                LastName=Info.LastName,
                Telephone=Info.Telephone,
                Email=Info.Email)

#########################################
#Artist
@app.route('/artist/', methods=['GET'])
def get_artist():
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db_dirs()
        print lendb
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return '', 400

    items = []
    items = artist_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }

#########################################
#Tracks
@app.route('/tracks/', methods=['GET'])
def get_track():
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    
    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return 'error', 400

    items = []
    items = tracks_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4),200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }


@app.route('/tracks/<id>', methods=['GET'])
def get_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    print row
    if row == 0:
        return '', 404
    else:
        return json.dumps({
            'id': row.track_id,
            'track': row.track,
            'album': row.album,
            'year': row.year,
            'genre': row.genre
        }, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/tracks/<id>', methods=['POST'])
def post_track(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        artist_id = request.args.get('artist_id')
        track = request.args.get('track')
        album = request.args.get('album')
        year = request.args.get('year')
        genre = request.args.get('genre')
        if artist_id is None or year is None:
            raise Exception()
        if album is None or track is None or genre is None:
            raise Exception()
    except:
        return '', 400

    i = insert_track(id, track, artist_id, album, year, genre)
    if i == 0:
        return '', 400
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 201, {
            'Content-Type': 'application/json;charset=UTF-8',
        }


@app.route('/tracks/<id>', methods=['PUT'])
def put_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    if row == 0:
        return '', 404
    try:
        artist_id = request.args.get('artist_id')
        track = request.args.get('track')
        album = request.args.get('album')
        year = request.args.get('year')
        genre = request.args.get('genre')
        if artist_id is None and year is None and album is None and track is None and genre is None:
            raise Exception()
    except:
        return '', 400
    if artist_id is not None:
        i = update_track(id, 'artist_id', artist_id)
    if track is not None:
        i = update_track(id, 'track', track)
    if album is not None:
        i = update_track(id, 'album', album)
    if year is not None:
        i = update_track(id, 'year', year)
    if genre is not None:
        i = update_track(id, 'genre', genre)
    if i == 0:
        return '', 400
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/tracks/<id>', methods=['DELETE'])
def delete_track(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    if row == 0:
        return '', 404
    del_track(id)
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

if __name__ == "__main__":
 app.run(debug=True, port=27010)
