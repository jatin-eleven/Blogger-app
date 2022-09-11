# --------------------------------------------------
# Creating Env = virtualenv env 
# Activate env = .\env\Scripts\activate.ps1
# --------------------------------------------------

from flask import Flask, render_template, request, flash, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from requests.models import HTTPError
import pyrebase

from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager



# Setup....
cred = credentials.Certificate('firebase-service.json')
# cred = credentials.Certificate('E:/APP2/firebase-service.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()


# # Firebase PyreBase Authentication.....
firebaseConfig = {
    "apiKey": "AIzaSyBeUAA7qLFY1AQ8XSvUMw1zjA80eEpkEq0",
    "authDomain": "blog-application-1af2b.firebaseapp.com",
    "databaseURL":"",
    "projectId": "blog-application-1af2b",
    "storageBucket": "blog-application-1af2b.appspot.com",
    "messagingSenderId": "712551889801",
    "appId": "1:712551889801:web:86adff77bd27491bd23f58",
    "measurementId": "G-GTDK162EJL"
    }
firebaseAuth = pyrebase.initialize_app(firebaseConfig)
pyrebaseAuth = firebaseAuth.auth()



app = Flask(__name__)
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"


# checking if user is authenticated or not, by doing this we can use auth and unauth propeties in html page(displaying diff. content for both profile)...
is_user_auth = False

login_manager = LoginManager()
# when user is not logged in it redirects to the login page...
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
    return db.collection("AUTHENTICATION").document(uid).get()



user_data = {
    "uid" : "",
    "name" : "",
    "gender" : "",
    "email" : "",
    "password" : "",
    "phone" : "",
    "pincode" : ""
}
curr_user_uid = []



# # Function...
@login_required
@app.route("/", methods=["GET", "POST"])
def home():
    print("\n\nUSER AUTH : ", is_user_auth)
    return render_template("home.html", user=is_user_auth)




@app.route("/signout", methods=["GET", "POST"])
def signout():
    global is_user_auth
    is_user_auth = False
    return redirect(url_for("login"))



@app.route("/login", methods=["GET", "POST"])
def login():
    global is_user_auth
    # is_user_auth = False
    user_check = False
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        print(password)

        try:
            user = pyrebaseAuth.sign_in_with_email_and_password(email, password)
            # userr = email
            print(">>> Existing User")
            user_check = True
        except HTTPError as he:
            flash("Incorrect Password! Try Again", category="error")
            print(">>> Error generated -> new user")
            
        if user_check:
            user_uid = pyrebaseAuth.get_account_info(user["idToken"]) 
            uid = user_uid["users"][0]["localId"]
            user_data["uid"] = str(uid)
            is_user_auth = True
            user_data_extraction(email, password)
            return render_template("home.html", user=is_user_auth)

    return render_template("login.html", user=is_user_auth)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    global is_user_auth
    user_check = False
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        email = request.form.get("email")
        password = request.form.get("password")
        terms = request.form.get("check")
        phone = request.form.get("phone")
        pin = request.form.get("pin")
        print(name)
        print(gender)
        print(email)
        print(password)
        print(terms)
        print(phone)
        print(pin)
    

        print(user_check)
        if email != "" and name != "" and gender != "Select a Gender" and password != "" and terms != None:
            try:
                user = pyrebaseAuth.create_user_with_email_and_password(email, password)
                print(">>> User signed up")
                user_check = True
            except HTTPError as he:
                print("Error : ", he)
                print("\n\nError Occured - exit\n\n")

            if user_check:
                is_user_auth = True
                user_uid = pyrebaseAuth.get_account_info(user["idToken"]) 
                uid = user_uid["users"][0]["localId"]
                print("\n>>> UID : ", uid, "\n")

                curr_user_uid.append(uid)
                check_user_db = db.collection("AUTHENTICATION").document(uid).get().exists

                if check_user_db:
                    pass
                else:
                    db.collection("AUTHENTICATION").document(uid).set(
                        {
                            "name" : name,
                            "gender" : gender,
                            "uid" : uid,
                            "username" : email.lower(),
                            "password" : password,
                            "phone" : phone,
                            "pincode" : pin,
                        })
                    print("Player Added in Database")
                print("HOME")

                user_data_extraction(email, password)

                return render_template("home.html", user=is_user_auth)
            else:
                flash("User already exist, please login !", category="error")
        else:
            flash("Fill all the info. to proceed !", category="error")


    return render_template("signup.html")



@app.route("/accsetting", methods=["GET", "POST"])
def account_setting():
    if request.method == "POST":
        print(">>>>IF")
        global is_user_auth
        is_user_auth = True

        name = request.form.get("name")
        gender = request.form.get("gender")
        phone = request.form.get("phnumber")
        pin = request.form.get("pin")
        print(name)
        print(gender)
        print(phone)
        print(pin)

        if name != "":
            doc_ref = db.collection('AUTHENTICATION').document(user_data["uid"]).update(
            {
                "name" : name,
            })
        
        if gender != "Gender":
            doc_ref = db.collection('AUTHENTICATION').document(user_data["uid"]).update(
            {
                "gender" : gender
            })
        
        if phone != "":
            doc_ref = db.collection('AUTHENTICATION').document(user_data["uid"]).update(
            {
                "phone" : phone
            })
        if pin != "":
            doc_ref = db.collection('AUTHENTICATION').document(user_data["uid"]).update(
            {
                "pincode" : pin
            })
        


        user_data_extraction(user_data["email"], user_data["password"])

        return render_template("account_setting.html", name=user_data["name"], gender=user_data["gender"], email=user_data["email"], uid=user_data["uid"], user=is_user_auth)


    print(">>>>NOT IF")
    return render_template("account_setting.html", name=user_data["name"], gender=user_data["gender"], email=user_data["email"], uid=user_data["uid"], user=is_user_auth)



@app.route("/info", methods=["GET", "POST"])
def info():
    return render_template("info.html", user=is_user_auth)























def user_data_extraction(email, password):
    try:
        user = pyrebaseAuth.sign_in_with_email_and_password(email, password)
        user_uid = pyrebaseAuth.get_account_info(user["idToken"]) 
        uid = user_uid["users"][0]["localId"]
        user_data["uid"] = str(uid)

        doc = db.collection("AUTHENTICATION").document(user_data["uid"]).get()
        coll = doc.to_dict()
        
        user_data["name"] = coll["name"]
        user_data["gender"] = coll["gender"]
        user_data["email"] = coll["username"]
        user_data["password"] = coll["password"]
        user_data["phone"] = coll["phone"]
        user_data["pincode"] = coll["pincode"]

        print("\n\nUSER DATA : ", user_data, "\n\n")

    except HTTPError as he:
        print(">>> Error in user data extraction", he)
    

    

if __name__ == "__main__":
    app.run(debug=True, port=4300)

