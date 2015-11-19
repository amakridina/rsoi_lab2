from flask import Flask,redirect,request,session
import requests

app = Flask(__name__)

@app.route("/")
def test():
    return "Test";

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return 'WELCOME TO MUSIC LIB'
    return app.send_static_file('auth.html')

@app.route("/register", methods=['GET', 'POST'])
def registerForm():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_nsme']
        last_name = request.form['last_name']
        tel = request.form['tel']
        email = request.form['email']
        password = request.form['password']
        return 'Are you registered'
    return app.send_static_file('register.html')


if __name__ == "__main__":
 app.run(debug=True, port=27010)
