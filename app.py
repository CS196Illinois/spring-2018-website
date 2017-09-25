from flask import Flask, render_template, request
import logging
import os
import sched
from datetime import datetime, timedelta
from models import db, Session, User, Signin

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///')

#
# API Endpoints
#

@app.route("/opensession")
def opensession():
    session = Session.query.filter_by(alive=True).first()
    if session is not None: return "another live session exists"
    s = Session(
        date = datetime.now(),
        alive = True
    )
    db.session.add(s)
    db.session.commit()
    return "successfully opened session"

@app.route("/signin", methods=["POST", "GET"])
def signin():
    msg = ""
    session = Session.query.filter_by(alive=True).first()
    if session is None: 
        msg="There is no lecture at this time."
        return render_template("signin.html", msg=msg)
    if request.method == "POST":
        while True:
            if "netid" not in request.form:
                msg = "Please enter a valid NetID."
                break
            u = User.query.filter_by(netid=request.form["netid"].encode('ascii','ignore')).first()
            if u is None:
                msg = "Please enter a valid NetID."
                break
            signin = Signin.query.filter_by(userid=u.id).filter_by(sessionid=session.id).first()
            if signin is not None:
                msg = "Already signed in for this session."
                break 
            s = Signin(
                userid = u.id,
                sessionid = session.id
            )
            db.session.add(s)
            db.session.commit()
            msg = "Successfully signed in."
            break
    return render_template("signin.html", msg=msg)

@app.route("/closesession")
def closesession():
    s = Session.query.filter_by(alive=True).first()
    if s is not None:
        s.alive = False
        db.session.commit()
        return "successfully closed session"
    return "no live session"

@app.route("/backup")
def backup():
    retval = backup_data()
    return "successfully backed up"

@app.route("/")
def home():
    session = Session.query.filter_by(alive=True).first()
    msg = ""
    if session is not None:
        msg = "<input type=\"button\" value=\"Sign in to Lecture\" onclick=\"window.location.href='/signin'\">"
    return render_template("index.html", msg=msg)

@app.route("/<content>")
def home_w_content(content):
    session = Session.query.filter_by(alive=True).first()
    msg = ""
    if session is not None:
        msg = "<input type=\"button\" value=\"Sign in to Lecture\" onclick=\"window.location.href='/signin'\">"
    return render_template("index.html", msg=msg)

#
# import data from student roster
# uses file backup.csv by default
#

def import_data():
    with open("backup.csv", "r") as backup:
        # load stats
        stats = backup.readline().replace("\n","").split(",")
        sessions = int(stats[0])
        users = int(stats[1])
        # load sessions
        session_ctr = 0
        while session_ctr < sessions:
            session_line = backup.readline().encode('ascii', 'ignore')
            s = Session(
                date = datetime.strptime(session_line, "%Y-%m-%dT%H:%M:%S.%f\n"),
                alive = False
            )
            db.session.add(s)
            session_ctr += 1
        # load users
        user_ctr = 0
        while user_ctr < users:
            user_line = backup.readline().encode('ascii', 'ignore').replace("\n","").replace("\r","").split(",")
            u = User(
                netid = user_line[0]
            )
            db.session.add(u)
            # load signins
            for idx in range(1, len(user_line)):
                s = Signin(
                    userid = u.id,
                    sessionid = int(user_line[idx])
                )
                db.session.add(s)
            user_ctr += 1
        db.session.commit()
        logging.warning("sessions:%d users:%d" % (Session.query.count(), User.query.count()))

#
# backup data to backup.csv
#

def backup_data():
    with open("backup.csv", "w") as backup:
        # write stats
        sessions = Session.query.count()
        users = User.query.count()
        backup.write("%d,%d\n" % (sessions, users))
        # write sessions
        for session in Session.query.all():
            backup.write("%s\n" % session.date.isoformat())
        # write users
        for user in User.query.all():
            backup.write("%s" % user.netid)
            for signin in user.signins:
                backup.write(",%d" % signin.sessionid)
            backup.write("\n") 

if __name__ == "__main__":
    db.app = app
    db.init_app(app)
    db.create_all(app=app)
    import_data()
    app.run("0.0.0.0", port=80, threaded=True)
