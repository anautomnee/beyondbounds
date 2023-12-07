import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp


from datetime import date

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

@app.route("/")
@login_required
def index():
    return render_template("index.html")


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
        con = sqlite3.connect("bb.db")
        db = con.cursor()
        res = db.execute("SELECT hash FROM users WHERE username = ?", [request.form.get("username")])
        rows = res.fetchone()

        # Ensure username exists and password is correct
        count = 0
        for row in rows:
            count = count + 1
        
        
        #Ensure password is correct

        if count != 1 or not check_password_hash(rows[0], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        res = db.execute("SELECT id FROM users WHERE username = ?", [request.form.get("username")])
        rows = res.fetchone() 
        session["user_id"] = rows[0]

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
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)

        # Ensure passwords match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords do not match", 400)

        # Ensure username is unique
        con = sqlite3.connect("bb.db")
        db = con.cursor()
        username = request.form.get("username")
        unique = db.execute(
            "SELECT COUNT(username) FROM users WHERE username = ?",
            [username]
        )
        if unique.fetchone() > (0, ):
            return apology("username already exists", 400)
        
        hash = generate_password_hash(
                request.form.get("password"), method="scrypt", salt_length=16
        )
        


        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", [username, hash])
        con.commit()

        # Query database for id
        id = db.execute(
            "SELECT id FROM users WHERE username = ?", [username]
        )
        id = id.fetchone()
        
        # Remember which user has logged in
        session["user_id"] = id

        con.close()

        return redirect("/")

    else:
        return render_template("register.html")