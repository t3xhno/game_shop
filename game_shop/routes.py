from flask import render_template, request, redirect, session, jsonify
from werkzeug.utils import secure_filename
from game_shop import app
import os
from flask_bcrypt import Bcrypt

from game_shop.models import *
bcrypt = Bcrypt(app)

@app.before_request
def before_request():
    print(request.path)
    if "username" not in session and request.path != "/login":
        return redirect("/login")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            if User.query.filter_by(username=username).first() is None: raise Exception("Invalid credentials")
            
            hashed_password = User.query.filter_by(username=username).first().password_hash

            if not bcrypt.check_password_hash(hashed_password, password): raise Exception("Invalid credentials")

            user = User.query.filter_by(username=username).first()

            session["username"] = user.username
            session["role"] = user.role
            session["_id"] = user._id

            return redirect("/")
        except Exception as e: return render_template("login.html", response=e)
    
    if request.method == "GET":
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return render_template("index.html", users = users)

@app.route("/register", methods=['GET', 'POST'])
def users():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            avatar_img = request.files["avatar_img"]
            role = request.form["role"]

            if User.query.filter_by(username = username).first() is not None:
                return render_template("register.html", response="Username is taken, try another one.")
            
            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

            avatar_path = ""
            if avatar_img.filename is not None and avatar_img.filename != "":
                avatar_path = avatar_img.filename
                avatar_img.save(os.path.join(app.config.root_path, app.config["UPLOAD_FOLDER"], "avatars", secure_filename(avatar_img.filename)))

            db.session.add(User(username, password_hash, email, avatar_path, role))
            db.session.commit()
        except Exception as e: return render_template("register.html", response=e)
        return redirect("/users")
    
    if request.method == "GET":
        return render_template("register.html")

@app.route("/users/<id>", methods=["DELETE", "GET", "POST"])
def handleUser(id):
    if request.method == "GET":
        try:
            if session["_id"] != int(id): raise Exception("Permission denied")
            user = User.query.filter_by(_id = id).first()
            if user is None: raise Exception("User with that id doesn't exist")
            return render_template("edit_user.html", user=user)
        except Exception as e: return render_template("users.html", response=e, users=User.query.all())
    
    if request.method == "POST":
        user = User.query.filter_by(_id=id).first()
        try:
            if session["_id"] != int(id): raise Exception("Permission denied")
            username = request.form["username"]
            email = request.form["email"]
            role = request.form["role"]

            if username != user.username and  User.query.filter_by(username=username).first() is not None: raise Exception("Username is taken")
            if email != user.email and User.query.filter_by(email=email).first() is not None: raise Exception("Email is taken")

            user.username = username
            user.email = email
            user.role = role
            print(user)
            db.session.commit()
            return redirect("/")
        except Exception as e: return render_template("edit_user.html", response=e, user=user)

    if request.method == "DELETE":
        try:
            if session["_id"] != int(id): raise Exception("Permission denied")
            db.session.delete(User.query.filter_by(_id=id).first())
            db.session.commit()
            return redirect("/users")
        except: render_template("index.html", response="User with id doesn't exist")

@app.route("/users")
def users_list():
    try:
        users = User.query.all()
    except:
        users = list()
    return render_template("users.html", users=users)

@app.route("/games")
def games():
    try:
        games = Game.query.all()
    except:
        games = list()
    return render_template("games.html", games=games)

@app.route("/add-game", methods=["POST", "GET", "DELETE"])
def add_game():
    if request.method == "POST":
        try:
            title = request.form["title"]
            desc = request.form["desc"]
            qty = request.form["qty"]
            price = request.form["price"]
            title = request.form["title"]
            cover_img = request.files["cover_img"]

            if Game.query.filter_by(title=title).first() is not None:
                return render_template("add_game.html", response="Title already in database")

            cover_path = ""
            if cover_img.filename is not None and cover_img.filename != "":
                cover_path = cover_img.filename
                cover_img.save(os.path.join(app.config.root_path, app.config["UPLOAD_FOLDER"], "covers", secure_filename(cover_img.filename)))

            db.session.add(Game(title, desc, cover_path, qty, price))
            db.session.commit()
        except Exception as e: return render_template("add_game.html", response=e)
        return redirect("/games")

    if request.method == "GET":
        return render_template("add_game.html")

@app.route("/game/<id>", methods=["POST", "GET", "DELETE"])
def game(id):
    if request.method == "GET":
        try:
            game = Game.query.filter_by(_id=id).first()
            me = User.query.filter_by(_id=session["_id"]).first()
            isOwned = len(list(filter(lambda game: game._id == int(id), me.my_games))) > 0
            return render_template("game.html", game=game, isOwned=isOwned)
        except: return render_template("games.html", response="Game not found!")

@app.route("/buy-game", methods=["POST"])
def buy_game():
    if request.method == "POST":
        try:
            game_id = request.json["game_id"]
            user_id = session["_id"]
            game = Game.query.filter_by(_id=game_id).first()
            user = User.query.filter_by(_id=user_id).first()
            isOwned = len(list(filter(lambda game: game._id == game_id, user.my_games))) > 0
            if isOwned: return jsonify({ "code": 301, "msg": "Game already owned!" })
            game.qty -= 1
            user.my_games.append(game)
            db.session.commit()
        except: return jsonify({ "code": 500, "msg": "Something went wrong..."  })

        return jsonify({
            "code": 200,
            "msg": "Successfully bought the game!",
        })

@app.route("/add-review/<game_id>", methods=["POST"])
def add_review(game_id):
    if request.method == "POST":
        try:
            rating = request.json["rating"]
            review_text = request.json["review_text"]
            user = User.query.filter_by(_id=session["_id"]).first()
            game = Game.query.filter_by(_id=game_id).first()
            newReview = Review(rating=rating, review_text=review_text)
            db.session.add(newReview)
            user.reviews.append(newReview)
            game.reviews.append(newReview)
            db.session.commit()
            return jsonify({
                "code": 200,
                "msg": "Successfully added review!",
            })
        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "msg": "Failed to add review :/",
            })

