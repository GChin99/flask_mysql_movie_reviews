from flask_app import app
from flask import Flask, render_template, redirect, request, session, flash
from flask_app.models.user import User 
from flask_app.models.review import Review 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


# -----------------------Read one (step 2 of 3)-------------------------------
@app.route("/dashboard")
def dashboard():
    # ***Login validation****:  For any route inside the app, we can write an if statment (if "key" not in session:)to mkae sure the user has either logged in or registered 
    #if user tried to bypass logging in or resistration, we can redirect them to the main page
    if "user_id" not in session:
        return redirect("/") 
    # The id for the data dictionary is no longer coming from a parameter in the route, Id is now coming from session. 
    data = {
        "id": session["user_id"]
    }
    return render_template("dashboard.html", logged_in_user = User.get_by_id(data), movie_reviews = Review.get_all())

@app.route("/reviews/new")
def new_review_form():
        # ***Login validation****:  For any route inside the app, we can write an if statment (if "key" not in session:)to mkae sure the user has either logged in or registered 
    #if user tried to bypass logging in or resistration, we can redirect them to the main page
    if "user_id" not in session:
        return redirect("/") 
    # The id for the data dictionary is no longer coming from a parameter in the route, Id is now coming from session. 
    data = {
        "id": session["user_id"]
    }
    user = User.get_by_id(data)
    return render_template("create_reivew.html", logged_in_user = user)

@app.route("/reviews/create", methods=["POST"])
def create_review():
    # if not Review.validate_review(request.form):
    #     return redirect("/reviews/new")
    Review.create_review(request.form)
    return redirect("/dashboard")

@app.route("/reviews/<int:id>")
def show_review(id):
    review_data = {
        "id": id
    }
    data = {
        "id": session["user_id"]
    }
    return render_template("show_review.html", review = Review.get_one(review_data),logged_in_user = User.get_by_id(data))

@app.route("/reviews/<int:id>/edit")
def show_edit_form(id):
    review_data = {
        "id": id
    }
    data = {
        "id": session["user_id"]
    }
    return render_template("edit_review.html", review = Review.get_one(review_data),logged_in_user = User.get_by_id(data))

@app.route("/reviews/<int:id>/update", methods =["POST"])
def update_review(id):
    Review.update(request.form)
    return redirect("/dashboard")

@app.route("/reviews/<int:id>/delete", methods =["POST"])
def delete(id):
    review_data = {
        "id": id
    }
    review = Review.get_one(review_data)
    if(review.user_id != session["user_id"]):
        flash(f"Unauthorized access to edit review with id {id}")
        return redirect("/dashboard")
    Review.delete(request.form)
    return redirect("/dashboard")

@app.route("/reviews/<int:id>/favorite", methods =["POST"])
def favorite_review(id):
    print(request.form)
    Review.favorite(request.form)
    return redirect("/dashboard")

@app.route("/reviews/<int:id>/unfavorite", methods =["POST"])
def unfavorite_review(id):
    print(request.form)
    Review.unfavorite(request.form)
    return redirect("/dashboard")