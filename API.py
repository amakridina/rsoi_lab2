from flask import Flask,redirect,request
import requests
import pyodbc

app = Flask(__name__)

@app.route("/")
def test():
    return "Test";

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connStr = (
            r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=rsoi;' +
            r'UID=rsoi;PWD=Aa123456'
            )

        db = pyodbc.connect(connStr)
        select_str = 'select count(*) as num from Users'
        cursor = db.execute(select_str)
        row = cursor.fetchone()
        if row:
            return str(row.num)
        return 'WELCOME TO MUSIC LIB'
    return app.send_static_file('auth.html')

@app.route("/register", methods=['GET', 'POST'])
def registerForm():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['fname']
        last_name = request.form['lname']
        tel = request.form['tel']
        email = request.form['email']
        password = request.form['password']

        connStr = (
            r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=rsoi;' +
            r'UID=rsoi;PWD=Aa123456'
            )

        db = pyodbc.connect(connStr)
        insert_str  = ("insert into Users"+
                       " (UserName, FirstName, LastName, Telephone, Email, Password)"+
                       " values ('%s','%s','%s','%s','%s','%s' )"
                       % (username, first_name, last_name, tel, email, password))
        db.execute(insert_str)
        db.commit()
        return 'Are you registered'
    return app.send_static_file('register.html')


if __name__ == "__main__":
 app.run(debug=True, port=27010)
