# -*- coding: cp1251 -*-
from flask import Flask,redirect,request,render_template
import requests
import pyodbc

app = Flask(__name__, static_path='')

@app.route("/")
def test():
    return "Test";

#подключение к БД
def connectDB():
    connStr = (
            r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=rsoi;' +
            r'UID=rsoi;PWD=Aa123456'
            )
    return pyodbc.connect(connStr)

#авторизация
@app.route("/login", methods=['GET', 'POST'])
def login():
    errorInfo = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = connectDB()
        select_str =("select count(*) as num from Users"+
                     " where UserName = '%s' and Password = '%s'"
                     % (username, password))
        cursor = db.execute(select_str)
        row = cursor.fetchone()
        if row.num == 0:
            errorInfo = "Incorrect login or password"
        else:
            return 'WELCOME TO MUSIC LIB'
    return render_template('auth.html', errorInfo=errorInfo)


#регистрация
def addUser(db, request):
    username = request.form['username']
    first_name = request.form['fname']
    last_name = request.form['lname']
    tel = request.form['tel']
    email = request.form['email']
    password = request.form['password']
    insert_str  = ("insert into Users"+
                       " (UserName, FirstName, LastName, Telephone, Email, Password)"+
                       " values ('%s','%s','%s','%s','%s','%s' )"
                       % (username, first_name, last_name, tel, email, password))
    db.execute(insert_str)
    db.commit()
    
@app.route("/register", methods=['GET', 'POST'])
def registerForm():
    errorInfo = ''
    if request.method == 'POST':
        db = connectDB()
        username = request.form['username']

        select_str = ("select count(*) as num from Users where UserName = '%s'"
                      % request.form['username'])
        cursor = db.execute(select_str)
        row = cursor.fetchone()
        
        if row.num > 0:
            errorInfo = ("User '%s' already exists!"% username)
        else:
            addUser(db, request)
            return 'Are you registered'
    return render_template('register.html', errorInfo=errorInfo)


#получение кода
@app.route("/api/oauth2/authorize", methods=['GET'])
def userCode():
    #in: appId, redirectUri
    #out: code
    
    return "code"

# получение access_token
@app.route("/api/oauth2/token", methods=['POST'])
def access_token():
    return None

#метод получения статуса пользователя авторизован/не авторизован
#@app.route("/api/status")
#def myStatus:
    

#метод получения информации о пользователе
@app.route("/api/me", methods=["GET"])
def userInfo():
    userInfo = "kj"
    return userInfo

if __name__ == "__main__":
 app.run(debug=True, port=27010)
