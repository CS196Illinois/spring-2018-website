from flask import Flask, render_template, request, abort
import logging
import os
import sched
import yaml
from datetime import datetime, timedelta
from asset_manager import Spreadsheet, AssetFolder
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///')

# load configuration
with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)

# authenticate user
gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
drive = GoogleDrive(gauth)

staff_datasheet = Spreadsheet(config['staff_datasheet'])
staff_assets = AssetFolder(drive, '/tmp/assets/staff', config['staff_folder'],
                           True, 60*60*24)
staff_assets.update()

lecture_datasheet = Spreadsheet(config['lecture_datasheet'])

#
# API Endpoints
#

@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.json or "ref" not in request.json:
        return abort(400)
    elif request.json["ref"] == "refs/heads/master":
        backup_data()
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError
        func()
    else:
        logging.error("non-master branch updated; no reload")
    return "success"

@app.route("/")
def home():
    return web_endpoint()

@app.route("/<content>")
def home_w_content(content):
    return web_endpoint()

def web_endpoint():
    staff_data = staff_datasheet.extract()

    # format lecture data
    lecture_data = lecture_datasheet.extract()
    print(lecture_data)
    lecture_arr = []
    for lecture in lecture_data:
        lecture_arr.append("""
            <div class="col-sm-2">
                <a href="%s">
                    <div class="infoLecture">
                        <h3>Lecture %s</h3>
                        <p>%s</p>
                    </div>
                </a>
            </div>
        """ % (lecture['slides'], lecture['lecture_id'], lecture['title']))
    lecture_formatted = "\n".join(lecture_arr)
    staff_formatted = ""

    return render_template("index.html", staff_formatted=staff_formatted,
                           lecture_formatted=lecture_formatted)

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, threaded=True)
