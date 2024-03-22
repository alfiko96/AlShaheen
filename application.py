import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///alshaheen.db")


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/profile")
@login_required
def profile():
    # look up the profile for current user
      identity = db.execute(
        "SELECT first_name, last_name, email FROM users WHERE id = :user_id", user_id=session["user_id"])
      fname = identity[0]["first_name"]
      lname = identity[0]["last_name"]
      email = identity[0]["email"]
      return render_template("profile.html", fname=fname, lname=lname, email=email)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("fname"):
            return apology("must provide name", 400)

        elif not request.form.get("lname"):
            return apology("must provide name", 400)

        elif not request.form.get("email"):
            return apology("must provide email address", 400)

        # update current user's details
        db.execute("UPDATE users SET first_name=:fname, last_name=:lname, email=:email WHERE id = :user_id",
        fname = request.form.get("fname"),
        lname = request.form.get("lname"),
        email = request.form.get("email"),
        user_id=session["user_id"])

        flash("Updated!")

        # Redirect user to home page
        return redirect("/profile")

    else:
        return render_template("update.html")

@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

       if not request.form.get("participant"):
            return apology("must provide a value", 400)

       if not request.form.get("category"):
            return apology("must provide a value", 400)

       p = request.form.get("participant")
       category = str.lower(request.form.get("category"))
       user = db.execute("SELECT id, first_name, last_name FROM users where id=:user_id", user_id=session["user_id"])
       fname = user[0]["first_name"]
       lname = user[0]["last_name"]
       user_id = user[0]["id"]

       # Check for existing participant
       exists_participant= db.execute("SELECT user_id FROM :category WHERE user_id=:user_id", category=category, user_id=user_id)
       if exists_participant:
            return apology("Member can only register once", 400)

       db.execute("INSERT INTO :category (user_id, first_name, last_name) VALUES (:user_id,:fname,:lname)",
               category=category, user_id=user_id, fname=fname, lname=lname)

       db.execute("UPDATE list SET participants = participants + :p where category=:category", p=p, category=category.capitalize())

       return redirect("/tournament")

    else:
        return render_template("join.html")

@app.route("/unjoin", methods=["GET", "POST"])
@login_required
def unjoin():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

       if not request.form.get("participant"):
            return apology("must provide a value", 400)

       if not request.form.get("category"):
            return apology("must provide a value", 400)

       p = request.form.get("participant")
       category = str.lower(request.form.get("category"))
       user = db.execute("SELECT id, first_name, last_name FROM users where id=:user_id", user_id=session["user_id"])
       user_id = user[0]["id"]

       exist = db.execute("SELECT * from :category WHERE user_id=:user_id", category=category, user_id=user_id)
       if not exist:
           return apology("Participant doesn't exist.", 400)

       db.execute("DELETE FROM :category WHERE user_id=:user_id", category=category, user_id=user_id)

       db.execute("UPDATE list SET participants = participants - :p where category=:category", p=p, category=category.capitalize())

       return redirect("/tournament")

    else:
        return render_template("unjoin.html")


@app.route("/unbook", methods=["GET", "POST"])
@login_required
def unbook():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("category"):
            return apology("must provide category", 400)

        elif not request.form.get("date"):
            return apology("must provide date", 400)

        elif not request.form.get("begin"):
            return apology("must provide time", 400)

        elif not request.form.get("end"):
            return apology("must provide time", 400)

        category = request.form.get("category")
        date = request.form.get("date")
        f = request.form.get("begin")
        to = request.form.get("end")

        exist = db.execute("SELECT * FROM book WHERE user_id=:user_id AND category=:category AND begin=:b AND booking_date=:date",
                   user_id=session["user_id"], category=category, b=f, date=date)
        if not exist:
            return apology("Booking doesn't exist.", 400)

        db.execute("DELETE FROM book WHERE user_id=:user_id AND category=:category AND begin=:b AND booking_date=:date",
                   user_id=session["user_id"], category=category, b=f, date=date)

        flash("Booking has been cancelled!")

        return redirect("/")

    else:
        return render_template("unbook.html")

@app.route("/tournament")
@login_required
def tournament():

    acts = db.execute("SELECT * FROM list")
    return render_template("tournament.html", acts=acts)

@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("category"):
            return apology("must provide category", 400)

        elif not request.form.get("date"):
            return apology("must provide date", 400)

        elif not request.form.get("begin"):
            return apology("must provide time", 400)

        elif not request.form.get("end"):
            return apology("must provide time", 400)

        category = request.form.get("category")
        date = request.form.get("date")
        f = request.form.get("begin")
        to = request.form.get("end")
        begin = datetime.strptime(f,'%H:%M')
        end = datetime.strptime(to,'%H:%M')
        user = db.execute("SELECT id, first_name, last_name FROM users where id=:user_id", user_id=session["user_id"])
        fname = user[0]["first_name"]
        lname = user[0]["last_name"]
        user_id = user[0]["id"]

        difference= end - begin
        if (difference.total_seconds()/3600) >= 2:
            return apology("Member can only book one hour at a time.", 400)
        # check for existing booking
        exist = db.execute("SELECT * FROM book WHERE category=:category AND booking_date=:date AND begin=:b",
                           category=category, date=date, b=f)
        if exist:
            return apology("This slot has been taken. Please book at another time.", 400)
        # members can only book 2 hours in a day
        limit = db.execute("SELECT user_id, SUM(end-begin) as total_sum FROM book where user_id=:user_id AND booking_date=:date",
                user_id=user_id, date=date)
        total = limit[0]["total_sum"]
        if total is None:
            total = 0
        if (total + (difference.total_seconds()/3600)) > 2:
            return apology("Member can only book for approximately 2 hours.", 400)
        # insert new entry of booking
        db.execute("INSERT INTO book (user_id, first_name, last_name, category, booking_date, begin, end) VALUES (:user_id,:fname,:lname,:category,:date,:f,:to)",
                   user_id=user_id, fname=fname, lname=lname, category=category, date=date, f=f, to=to)

        flash("Booking has been confirmed!")

        return redirect("/")

    else:
        return render_template("book.html")


@app.route("/history")
@login_required
def history():
    # display the history of bookings made by the user
    history = db.execute("SELECT category, booking_date, begin, end FROM book where user_id=:user_id", user_id=session["user_id"])
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure the same password was submitted
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        elif not request.form.get("fname"):
            return apology("must provide name", 400)

        elif not request.form.get("lname"):
            return apology("must provide name", 400)

        elif not request.form.get("email"):
            return apology("must provide email address", 400)

        # Check for existing username
        exists_username= db.execute("SELECT username FROM users where username = :username", username = request.form.get("username"))
        if exists_username:
            return apology("username taken", 400)

        # Enter username and hashed password into database
        hashed=generate_password_hash(request.form.get("password"))
        new_user = db.execute("INSERT INTO users (username, hash, first_name, last_name, email) VALUES (:username,:hashed,:firstname,:lastname,:email)",
                          username=request.form.get("username"), hashed=hashed, firstname=request.form.get("fname"),
                          lastname=request.form.get("lname"), email=request.form.get("email"))

        # Remember which user has logged in
        session["user_id"] = new_user

        # Successfully registered!!!
        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure the same password was submitted
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Check for existing username
        exists_username= db.execute("SELECT username FROM users where username = :username", username = request.form.get("username"))
        if not exists_username:
            return apology("Username does not exist.", 400)

        # Change password
        hashed=generate_password_hash(request.form.get("password"))
        db.execute("UPDATE users SET hash =:hashed WHERE username=:username", hashed=hashed, username=request.form.get("username"))

        # Password has been changed!!!
        flash("Password has been changed!")

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgotpassword.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
