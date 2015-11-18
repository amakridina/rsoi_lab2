from flask import Flask,redirect,request,session
import requests

app = Flask(__name__)

@app.route("/")
def test():
    return "Test";

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'POST LOGIN';
    return app.send_static_file('auth.html')

@app.route("/register", methods=['GET', 'POST'])
def registerForm():
    if request.method == 'POST':
        return 'POST REGISTER';
    return app.send_static_file('register.html')

if __name__ == "__main__":
 app.run(debug=True, port=27010)
