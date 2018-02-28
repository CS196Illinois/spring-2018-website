from flask import Flask, render_template, request, abort, jsonify
import logging
import os
import sched
import yaml
from collections import deque
from datetime import datetime, timedelta
from asset_manager import Spreadsheet, AssetFolder, authenticate_gdrive
from feed_utils import FeedManager

# load configuration
with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)

# authenticate user
if config['live_update']:
    credentials = authenticate_gdrive()

    assets_base_dir = os.path.join(os.getcwd(), 'static/assets')
    staff_datasheet = Spreadsheet(config['staff_datasheet'], credentials, True, 60*60)
    lecture_datasheet = Spreadsheet(config['lecture_datasheet'], credentials, True, 60*60)

app = Flask(__name__)
feed_manager = FeedManager(config['feed_size'])


#
# API Endpoints
#

@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.json or "ref" not in request.json:
        return abort(400)
    elif request.json["ref"] == "refs/heads/master":
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            raise RuntimeError
        func()
    else:
        logging.error("non-master branch updated; no reload")
    return "success"

@app.route("/feed", methods=["GET", "POST"])
def feed():
    if request.method == "POST":
        if "message" not in request.values:
            return abort(400)

        feed_manager.post(request.values.get("message"), request.remote_addr)
        return jsonify({"success": True}), 201
    else:
        feed = feed_manager.get_feed()
        return jsonify({"data": feed, "size": len(feed)})

@app.route("/")
def home():
    return web_endpoint()

@app.route("/<content>")
def home_w_content(content):
    return web_endpoint()

def web_endpoint():
    if config['live_update']:
        staff_data = staff_datasheet.get_data()
    else:
        staff_data = [] # for local development only
    staff_arr = []
    for index, staff in enumerate(staff_data):
        start_row = ""
        end_row = ""
        if index % 4 == 0:
            start_row = """<div class="row">"""
        elif index % 4 == 3:
            end_row = """</div>"""

        border = "officer-bg" if staff["officer"] else "staff-bg"

        staff_arr.append("""
            %s
            <div class="col-sm-3"> 
                <div class="%s">
                    <img src = "%s"/>
                    <h4>%s</h4>
                    <p>%s</p>
                </div>  
            </div>
            %s
        """ % (start_row, border, staff['profile'], staff['name'], staff['desc'], end_row))
    staff_formatted = "\n".join(staff_arr)

    # format lecture data
    if config['live_update']:
        lecture_data = lecture_datasheet.get_data()
    else:
        lecture_data = [] # for local development only
    lecture_arr = []
    for lecture in lecture_data:
        lecture_arr.append("""
            <div class="col-sm-2">
                <a href="%s">
                    <div class="infoLecture">
                        <h3>Lecture %s</h3>
                        <p>%s</p>
                        <a href="%s">Video</a>
                        <a href="%s">Demo</a>
                    </div>
                </a>
            </div>
        """ % (lecture['slides'], lecture['lecture_id'], lecture['title'],
               lecture['video'], lecture['demo']))
    lecture_formatted = "\n".join(lecture_arr)

    return render_template("index.html", staff_formatted=staff_formatted,
                           lecture_formatted=lecture_formatted)

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, threaded=True)
