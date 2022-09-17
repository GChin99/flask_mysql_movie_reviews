from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models.user import User
import re   # the regex module
# create a regular expression object that we'll use later (validation)   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
PASSWORD_REGEX =re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z\d]+$")
# At least one upper case English letter, (?=.*[A-Z])
# At least one lower case English letter, (?=.*[a-z])
# At least one digit, (?=.*[0-9])


class Review:

    db = "movie_critic"

    def __init__(self, data):
        self.id = data["id"]
        self.title = data["title"]
        self.rating = data["rating"]
        self.date_watched = data["date_watched"]
        self.content = data["content"]
        self.user_id = data["user_id"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user = None
        # below attribute is for many to many query
        self.users_who_favorited = [] #used in show_review to show who favorited the review
        self.user_id_who_favorited = [] #used on dashboard to favorite/unfavorite button


# get all the reviews with the associted user information (one to many)
    # @classmethod
    # def get_all(cls):
    #     # query = "SELECT * FROM reviews JOIN users ON reviews.user_id = users.id;"
    #     results = connectToMySQL(cls.db).query_db(query) #data isn't needed to run this query 
    #     print(results)
    #     #we want to create an empty list that we will appened the reviews with the users instance attached to it
    #     reviews = []
    #     for row in results:
    #         #create the review object
    #         review = cls(row)
    #         #create associated user object, need data dictionary for user
    #         user_data = {
    #             "id": row["users.id"],
    #             "first_name": row["first_name"],
    #             "last_name": row["last_name"],
    #             "email": row["email"],
    #             "password": row["password"],
    #             "created_at": row["users.created_at"],
    #             "updated_at": row["users.updated_at"]
    #         }
    #         user = User(user_data)
    #         review.user = user
    #         reviews.append(review)
    #     return reviews

# # get all the reviews with the associted user information and users who liked the review(Many to many query)
    @classmethod
    def get_all(cls):
        # '''   ''' a pair of three apostrophes is a multi line quotes
        # Select line will get all the reviews with the associted user information. Uses an alias to change users to creators (creators of the review) (links users table with reviews table)
        # 1st LEFT JOIN shows which user_id liked which review_id (user_id 1 like review_id 1) (links reviews table with favorited table)
        # 2nd LEFT JOIN will give us the information for the user_id (user_id 1 is Happy Yeti ) We use an alias to change users to users_who_favorited (users who favoriated a review) (links users table with favorited_reviews table)
        query = '''
            SELECT * FROM reviews JOIN users AS creators ON reviews.user_id = creators.id
            LEFT JOIN favorited_reviews ON reviews.id = favorited_reviews.review_id
            LEFT JOIN users AS users_who_favorited ON favorited_reviews.user_id = users_who_favorited.id; '''
        results = connectToMySQL(cls.db).query_db(query) #data isn't needed to run this query 
        print(results)
        #we want to create an empty list that we will appened the reviews with the users instance attached to it
        reviews = []
        for row in results:
            # set boolean to check if its a new review (if its a new review it jumps down to if new_review)
            # if its not a new reivew, the row will have some dupaciate information that we do not need
            # We only want 1 instances of a review, but we want all the users who liked the review
            new_review = True
            # We need the user data for the user who favorited a review
            user_who_favorited_data = {
                # users_who_favorited came from the JOIN statment in the query (JOIN users AS users_who_favorited)
                "id": row["users_who_favorited.id"], #we have to add users_who_favorited. to all attributes because the user_data below took the orginal attribute
                "first_name": row["users_who_favorited.first_name"],
                "last_name": row["users_who_favorited.last_name"],
                "email": row["users_who_favorited.email"],
                "password": row["password"],
                "created_at": row["users_who_favorited.created_at"],
                "updated_at": row["users_who_favorited.updated_at"]
            }

            # We need to check to see if there are any reviews, if there isnt, then we can process this as a new review
            number_of_reivews = len(reviews)
            # if number of reviews is 0 then we know it a new review and we can process it as a new review (if new_review)
            if number_of_reivews > 0:
                # if a review is present, we want to grab the last review that was process
                last_review = reviews[number_of_reivews-1]
                # we want to check the id of the last review and compaire it to the current row (was this review favorited by the current user)
                if last_review.id == row["id"]:
                    # If its the same review we need to add the user  to the current list of users_who favorited the review
                    last_review.user_id_who_favorited.append(row["users_who_favorited.id"])
                    last_review.users_who_favorited.append(User(user_who_favorited_data)) #appened user object to the attribute user_who_favorited
                    # if appeneded a user to users_who_favorited a reveiw, then we know this is not a new review so new_review = False
                    new_review = False

            # new reveiw is the same as a one to many get all method above (get all the reviews with the associted user information)
            if new_review:
                #create the review object
                review = cls(row)
                #create associated user object, need data dictionary for user
                # This is the user data for who created the review 
                user_data = {
                    # need to put creators in front of id, created_at, and updated_at because they share the same attributes as reviews
                    # since reviews is on the left hand side of the JOIN it gets the attribute first
                    "id": row["creators.id"], #we have to change it from users.id to creators.id because we used alias in our query statment
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_at": row["creators.created_at"],
                    "updated_at": row["creators.updated_at"]
                }
                user = User(user_data)
                review.user = user
                #check to see if anyone favorited the review.  If there is we appened it to our empty list attributes 
                if row["users_who_favorited.id"]: #if this has no value, skip over the next 2 lines. If it does have a value, we need to append that information
                    review.user_id_who_favorited.append(row["users_who_favorited.id"])
                    review.users_who_favorited.append(User(user_who_favorited_data))
                reviews.append(review) #we are appended a new reviews with the user who created the reveiw 
        return reviews
    
# get one reviews with the associted user information(one to many query)
    # @classmethod
    # def get_one(cls, data):
    #     query = "SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE reviews.id = %(id)s;"
    #     results = connectToMySQL(cls.db).query_db(query, data) #data isn't needed to run this query 
    #     print(results)
    #     #create the review object, 
    #     row = results[0]
    #     review =cls(row)
    #         #create associated user object, need data dictionary for user
    #     user_data = {
    #         "id": row["users.id"],
    #         "first_name": row["first_name"],
    #         "last_name": row["last_name"],
    #         "email": row["email"],
    #         "password": row["password"],
    #         "created_at": row["users.created_at"],
    #         "updated_at": row["users.updated_at"]
    #     }
    #     user = User(user_data)
    #     review.user = user
    #     # return the single review object that has the associted user object attached to the user attribute (self.user = None)
    #     return review
    

# get one reviews with the associted user information and users who liked the review(Many to many query)
    @classmethod
    def get_one(cls, data):
        # '''   ''' a pair of three apostrophes is a multi line quotes
        # Select line will get all the reviews with the associted user information. Uses an alias to change users to creators (creators of the review) (links users table with reviews table)
        # 1st LEFT JOIN shows which user_id liked which review_id (user_id 1 like review_id 1) (links reviews table with favorited table)
        # 2nd LEFT JOIN will give us the information for the user_id (user_id 1 is Happy Yeti ) We use an alias to change users to users_who_favorited (users who favoriated a review) (links users table with favorited_reviews table)
        query = '''
            SELECT * FROM reviews JOIN users AS creators ON reviews.user_id = creators.id
            LEFT JOIN favorited_reviews ON reviews.id = favorited_reviews.review_id
            LEFT JOIN users AS users_who_favorited ON favorited_reviews.user_id = users_who_favorited.id
            where reviews.id = %(id)s;'''
        results = connectToMySQL(cls.db).query_db(query, data) #data isn't needed to run this query 
        print(results)
        if len(results) <1:
            return False

        new_review = True
        for row in results:
            #if this is the first row being processed
            if new_review:
                review =cls(row)
                #create associated user object, need data dictionary for user
                user_data = {
                    "id": row["creators.id"], #we have to change it from users.id to creators.id because we used alias in our query statment
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_at": row["creators.created_at"],
                    "updated_at": row["creators.updated_at"]
                }
                creator = User(user_data)
                review.creator = creator
                new_review = False

            if row["users_who_favorited.id"]:
                user_who_favorited_data = {
                    # users_who_favorited came from the JOIN statment in the query (JOIN users AS users_who_favorited)
                    "id": row["users_who_favorited.id"], #we have to add users_who_favorited. to all attributes because the user_data below took the orginal attribute
                    "first_name": row["users_who_favorited.first_name"],
                    "last_name": row["users_who_favorited.last_name"],
                    "email": row["users_who_favorited.email"],
                    "password": row["password"],
                    "created_at": row["users_who_favorited.created_at"],
                    "updated_at": row["users_who_favorited.updated_at"]
                }
                user_who_favorited = User(user_who_favorited_data)
                review.users_who_favorited.append(User(user_who_favorited_data))
                review.user_id_who_favorited.append(row["users_who_favorited.id"])
        # return the single review object that has the associted user object attached to the user attribute (self.user = None)
        return review

    @classmethod
    def create_review(cls, data):
        #insert queries will return the id number of the row inserted
        query = "INSERT INTO reviews (title, rating, date_watched, content, user_id) VALUES (%(title)s, %(rating)s, %(date_watched)s, %(content)s, %(user_id)s);"
        results = connectToMySQL(cls.db).query_db(query, data)
        # print(results)
        # return results

    @classmethod
    def update(cls, data):
        query = "UPDATE reviews SET title = %(title)s, rating = %(rating)s, date_watched = %(date_watched)s, content= %(content)s WHERE id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        # print(results)
        # return results

    @classmethod
    def delete (cls, data):
        query = "DELETE FROM reviews WHERE id = %(id)s"
        results = connectToMySQL(cls.db).query_db(query, data)
        # print(results)
        # return results

    @classmethod
    def favorite (cls, data):
        query = "INSERT INTO favorited_reviews (user_id, review_id) VALUES (%(user_id)s, %(id)s);"
        results = connectToMySQL(cls.db).query_db(query, data)
        print(results)
        return results

    @classmethod
    def unfavorite (cls, data):
        query = "DELETE FROM favorited_reviews WHERE user_id = %(user_id)s AND review_id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        print(results)
        return results


    @staticmethod
    def validate_review(review):
        is_valid = True
        if len(review["title"]) <1:
            flash("Title is too short!") 
            is_valid = False
        if len(review["rating"]) <1:
            flash("Need to rate movie") 
            is_valid = False
        # if int(review['rating']) <0 or int(review['rating']) >5:
        #     flash("Rating needs to be in between 0-5, error")
        #     is_valid = False
        # validate a radio button, If raido was not clicked, the key would not register 
        # if "radio_button_key" not in review:
            # flash("you need to select radio_button")
        return is_valid