from flask_app import app
from flask import Flask, render_template, redirect, request, session, flash
from flask_app.models.user import User 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


@app.route("/")
def groot():
    return render_template("home_page.html")

#-- -------------------------Registration (Create User Step 2 of 3) --------------------------
@app.route("/create_user", methods=["POST"])
def create_user():
    print(request.form)
    # --------------------validation (step 2 of 3)-----------------------------------
    if not User.validate_create(request.form):
        return redirect("/") #redirect back to the create form
    # -------------(Bcrypt) Hash password after validation but before data dictionary-----------
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    # put the pw_hash into the data dictionary instead of the request.form password
    data ={
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": pw_hash
        #we do not need password Conf because we only need to store the password once
    }
    user_id = User.create(data) 
    session["user_id"] = user_id  #storing "key" in session, Once it's saved in session can be access from any route
    return redirect("/dashboard") 


# --------------------Login (Comparing Upon Login step 2 of 3)-----------------------------
# We'll need to make sure the users login info and the provided password with the hash in the database are in the same row
@app.route("/login", methods =["POST"])
def login():
    print(request.form)
    # see if the user's email provided exists in the database 
    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data) #we need to create this class method 
    # user is not registered in the db, they will get the flash message and redirected
    if not user_in_db:
        flash("Invalid Email/Password", "login") #"login" is the validation catagory filter
        return redirect("/")
        #this is to check that the email and password are in the same row in the database table
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        # if we get False after checking the password, we flash message and redirect
        flash("Invalid Email/Password", "login")
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect("/dashboard")




# *********The following pages is now inside of our app. The login and Registration is the front door*********




    # ------------------Logout (step 2 of 2)----------------- --
@app.route("/logout")
def logout():
    # This line will get rid of everything stored in session 
    session.clear()
    return redirect("/")

