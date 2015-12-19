# -*- coding: cp1251 -*-
from flask import Flask,redirect,request,render_template,jsonify, url_for
import requests
import pyodbc
import json
import uuid
import urllib
from db import *

app = Flask(__name__, static_path='')



#проверка токена в бд
def UserToken(DB, token):
    if not token:
        return None
    select_str = ("select UserName from Tokens where AccessToken = '%s'" % token)
    cursor = DB.execute(select_str)
    row = cursor.fetchone()
    if not row:
        return None
    return row.UserName   
    
        
#авторизация
@app.route("/login", methods=['GET', 'POST'])
def login():
    errorInfo = ''
    callback = 'https://www.google.ru'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        callback = request.form['callback']
        
        if user_pass_check(username,password) == 0:
            errorInfo = "Incorrect login or password"
        else:
            #TODO AUTH
            return redirect(callback)
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
    #in: appId, redirectUri
    #out: code
    username = request.args.get('username')
    arr = request.args
    if not username :
        #return redirect ('/login?'+urllib.urlencode(arr))
        url = "/api/oauth2/authorize?" + urllib.urlencode(arr)
        return redirect ('/login?callback='+urllib.quote_plus(url))
    return "code"

# получение access_token
@app.route("/api/oauth2/token", methods=['POST'])
def access_token():
    return None


########################################

#метод получения статуса пользователя авторизован/не авторизован
@app.route("/api/status")
def myStatus():
    return None


#поиск пользователя
def UserInfo(DB, username):
    if username == '':
        return None
    select_str = ("select "+
                  "UserName,FirstName,LastName,Telephone,Email "+
                  "from Users where UserName = '%s'" % username)
    cursor = DB.execute(select_str)
    row = cursor.fetchone()
    if not row:
        return None
    return row 

#метод получения информации о пользователе
@app.route("/api/me", methods=["GET"])
def me():
    access_token = request.headers.get('Authorization', '')[len('Bearer '):]
    #if not (access_token == "AccessToken"):
     #   return '', 403
    
    #db = connectDB()
    #username = UserToken(db, access_token)
    Info = get_me(access_token)
    
    return jsonify(UserName=Info.UserName,
                FirstName=Info.FirstName,
                LastName=Info.LastName,
                Telephone=Info.Telephone,
                Email=Info.Email)

if __name__ == "__main__":
 app.run(debug=True, port=27010)
