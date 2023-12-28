import datetime
import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, abort
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

#Calendar
events = [
    {
        'todo' : 'Test',
        'date' : '2023-12-17'
    }
]

# Groups table
try:
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "CREATE TABLE groups ( group_id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT NOT NULL)"
    )
except sqlite3.OperationalError:
    pass

# Groups_id table
try:
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "CREATE TABLE group_to_user (group_id INTEGER NOT NULL, user_id INTEGER NOT NULL)"
    )
except sqlite3.OperationalError:
    pass

# Events table
try:
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "CREATE TABLE events ( event_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, group_id INTEGER NOT NULL, start TEXT NOT NULL, end TEXT NOT NULL)"
    )
except sqlite3.OperationalError:
    pass

# Meetings table
try:
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "CREATE TABLE meetings ( meeting_id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER NOT NULL, start TEXT NOT NULL)"
    )
except sqlite3.OperationalError:
    pass

# Acceptions table
try:
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "CREATE TABLE acceptions ( acception_id INTEGER PRIMARY KEY AUTOINCREMENT, meeting_id INTEGER NOT NULL, user_id INTEGER NOT NULL, status INTEGER NOT NULL)"
    )
except sqlite3.OperationalError:
    pass

def get_groups(user_id):

    con = sqlite3.connect("bb.db")
    db = con.cursor()
    res = db.execute(
        "SELECT groups.group_name, groups.group_id FROM groups JOIN group_to_user ON groups.group_id = group_to_user.group_id WHERE user_id = ?", 
        [user_id]
    )
    groups = res.fetchall()

    # Conversion of list of tuple to list of strings
    groups = [{"name": name, "id": id} for (name,id) in groups]
    return groups

def statusToAdj(status):
    if status == None:
        return 'none'
    if status == 0 or status == (0, ):
        return 'none'
    if status == 1 or status == (1, ):
        return 'accepted'
    if status == 2 or status == (2, ):
        return 'declined'
    return 'N/A'

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        group_name = request.form.get("group_name")
        if group_name == '':
            return apology("must provide name", 403)
        
        con = sqlite3.connect("bb.db")
        db = con.cursor()
        db.execute(
            "INSERT INTO groups (group_name) VALUES (?)", [group_name]
        )
        con.commit()
        group_id = db.lastrowid

        db.execute(
            "INSERT INTO group_to_user (group_id, user_id) VALUES (?,?)", [group_id, session["user_id"]]
        )
        con.commit()
        groups = get_groups(session["user_id"])


        #Count the groups
        group_number = len(groups)

        #Get the meetings for the person
        con = sqlite3.connect("bb.db")
        db = con.cursor()
        db.execute(
            "SELECT meetings.start, groups.group_name FROM meetings JOIN acceptions ON meetings.meeting_id = acceptions.meeting_id JOIN groups ON meetings.group_id = groups.group_id WHERE acceptions.status = 1 AND acceptions.user_id = ? ORDER BY meetings.start DESC LIMIT 4", [session["user_id"]]
        )
        meetings = db.fetchall()

        meetings = [{"start": start, "name": name} for (start,name) in db.fetchall()]

        return render_template("index.html", groups=groups, group_number=group_number, meetings=meetings)

    else:
        groups = get_groups(session["user_id"])

        #Count the groups
        group_number = len(groups)

        #Get the meetings for the person
        con = sqlite3.connect("bb.db")
        db = con.cursor()
        db.execute(
            "SELECT meetings.start, groups.group_name FROM meetings JOIN acceptions ON meetings.meeting_id = acceptions.meeting_id JOIN groups ON meetings.group_id = groups.group_id WHERE acceptions.status = 1 AND acceptions.user_id = ? ORDER BY meetings.start DESC LIMIT 4", [session["user_id"]]
        )

        meetings = [{"start": start, "name": name} for (start,name) in db.fetchall()]
        
        return render_template("index.html", groups=groups, group_number=group_number, meetings=meetings)


@app.route("/group/<group_id>")
@login_required
def group(group_id):
    """Show main info for a group"""
    # Get group name

    # Check if user_id associated with group_id
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "SELECT COUNT(group_id) FROM group_to_user WHERE group_id = ? AND user_id = ?", [group_id, session["user_id"]]
    )
    group_access = db.fetchone()
    if group_access == (1,):
        # Get group name for title and members for body
        db.execute(
            "SELECT group_name FROM groups WHERE group_id = ?", [group_id]
        )
        group_name = db.fetchone()
        # Conversion of list of tuple to list of strings
        group_name = list(group_name)[0]

        # Get members for body
        db.execute(
            "SELECT users.username FROM users JOIN group_to_user ON users.id = group_to_user.user_id WHERE group_to_user.group_id = ?", [group_id]
        )
        members = db.fetchall()
        # Conversion of list of tuple to list of strings
        members = [i for (i,) in members]

        # Get all groups for user
        groups = get_groups(session["user_id"])

        #Get meetings for this group
        db.execute(
            "SELECT meetings.start, meetings.meeting_id FROM meetings WHERE meetings.group_id = ?", [group_id]
        )
        # Conversion of list of tuple to list of strings
        meetings = [{"start": start, "id": id} for (start,id) in db.fetchall()]
        for meeting in meetings:
            db.execute(
                "SELECT status FROM acceptions WHERE meeting_id = ? AND user_id = ?", [meeting["id"], session["user_id"]]
            )
            status = db.fetchone()

            meeting["status"] = statusToAdj(status)
            db.execute(
                "SELECT u.username, a.status FROM group_to_user as gu JOIN users as u ON gu.user_id=u.id LEFT JOIN acceptions as a ON a.user_id = gu.user_id WHERE gu.group_id = ? and gu.user_id != ? AND ( a.meeting_id = ? OR a.meeting_id is null )",
                [group_id, session["user_id"], meeting["id"]]
            )
            meeting["members"] = [{"username": username, "status": statusToAdj(status) } for (username, status) in db.fetchall()]
        meetings_number = len(meetings)

        return render_template("group.html", groups=groups, group_id=group_id, group_name=group_name, members=members, meetings=meetings, meetings_number=meetings_number)
    else:
        return apology("no access to this group", 400)

@app.route("/api/addmember", methods=["POST"])
def addmember():
    # TODO check if user already in group
    member_username = request.form.get("member_username")
    # Check if this username exists
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "SELECT id FROM users WHERE username = ?", [member_username]
    )
    res = db.fetchone()
    if res is not None:
        member_id, = res
        group_id = request.form.get("group_id")
        # Get user id from username 
        db.execute(
            "INSERT INTO group_to_user(group_id, user_id) VALUES(?,?);", [group_id, member_id]
        )
        con.commit()
        return redirect(f'/group/{group_id}')
    else:
        return apology("user doesn't exist", 400)

@app.route("/api/addmeeting", methods=["POST"])
def addmeeting():
    group_id = request.form.get("group_id")
    new_meeting = request.form.get("meeting_time")
    # Check if this meeting exists
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    db.execute(
        "SELECT COUNT(*) FROM meetings WHERE start = ? AND group_id = ?", [new_meeting, group_id]
    )
    meetings_count = db.fetchone()
    if meetings_count == (0,):
        db.execute(
            "INSERT INTO meetings(group_id, start) VALUES(?,?)", [group_id, new_meeting]
        )
        con.commit()
        db.execute(
            "SELECT meeting_id FROM meetings WHERE group_id = ? AND start = ?", [group_id, new_meeting]
        )
        meeting_id, = db.fetchone()

        db.execute(
            "INSERT INTO acceptions(meeting_id, user_id, status) VALUES(?,?,0)", [meeting_id, session["user_id"]]
        )
        con.commit()

        return redirect(f'/group/{group_id}')
    else:
        abort(400)

@app.route("/api/updatemeeting", methods=["POST"])
def acceptmeeting():
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    status = request.form.get("status")
    meeting_id = request.form.get("meeting_id")
    group_id = request.form.get("group_id")
    try:
        db.execute(
            "SELECT COUNT(*) FROM acceptions WHERE meeting_id = ? AND user_id = ?", [meeting_id, session["user_id"]]
        )
        if (1,) == db.fetchone():
            db.execute(
                "UPDATE acceptions SET status = ? WHERE meeting_id = ? AND user_id = ?", [status, meeting_id, session["user_id"]]
            )
        else:
            db.execute(
                "INSERT INTO acceptions(meeting_id, user_id, status) VALUES(?,?,?)", [meeting_id, session["user_id"], status]
            )
        con.commit()
        return redirect(f'/group/{group_id}')
    except Exception as e:
        abort(400)

@app.route("/api/newevent", methods=["POST"])
def newevent():
    con = sqlite3.connect("bb.db")
    db = con.cursor()
    start = request.form.get("start")
    end = request.form.get("end")
    group_id = request.form.get("group_id")
    try:
        db.execute(
            "INSERT INTO events (start, end, user_id, group_id) VALUES(?,?,?,?)", [start, end, session["user_id"], group_id]
        )
        con.commit()
        return str(db.lastrowid), 201
    except Exception as e:
        abort(400)

@app.route("/api/getevents", methods=["GET"])
@login_required
def getevent():
    user_id = session["user_id"]

    group_id = request.args.get("group_id", type=int)
    if group_id is None:
        abort(400)

    events = []

    con = sqlite3.connect("bb.db")
    db = con.cursor()
    # people in group - SELECT user_id FROM groups WHERE group_id = 
    db.execute(
        "SELECT e.event_id, e.start, e.end, e.user_id, u.username FROM events as e JOIN users as u ON e.user_id = u.id WHERE e.group_id = ?", [group_id]
    )

    for (event_id, start, end, event_user_id, event_username) in db.fetchall():
        event = {
            "id": event_id,
            "start": start,
            "end": end,
            "editable": False,
            "color": "#FD8F52",
        }
        if event_user_id != user_id:
            event["display"] = "background"
            event["title"] = event_username
            event["color"] = "#FD8F52"
        events.append(event)
    
    return events


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
        if rows is not None:
            for row in rows:
                count = count + 1
            
        
        
        #Ensure password is correct

        if count != 1 or not check_password_hash(rows[0], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        res = db.execute("SELECT id FROM users WHERE username = ?", [request.form.get("username")])
        rows = res.fetchone() 
        session["user_id"], = rows

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
        session["user_id"], = id

        con.close()

        return redirect("/")

    else:
        return render_template("register.html")