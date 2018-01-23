from flask import Flask, render_template, request, abort
import logging
import os
import sched
import yaml
from datetime import datetime, timedelta
from asset_manager import Spreadsheet, AssetFolder, authenticate_gdrive

app = Flask(__name__)

# load configuration
with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)

# authenticate user
if config['live_update']:
    credentials = authenticate_gdrive()

    assets_base_dir = os.path.join(os.getcwd(), 'static/assets')
    staff_datasheet = Spreadsheet(config['staff_datasheet'], credentials, True, 60*60)
    lecture_datasheet = Spreadsheet(config['lecture_datasheet'], credentials, True, 60*60)

#
# API Endpoints
#

@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.json or "ref" not in request.json:
        return abort(400)
    elif request.json["ref"] == "refs/heads/master":
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

        if staff["officer"]:
            border = "officer-bg"
            logging.error("%s is officer" % staff["name"])
        else:
            border = "staff-bg"
            logging.error("%s is staff" % staff["name"])

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
                    </div>
                </a>
            </div>
        """ % (lecture['slides'], lecture['lecture_id'], lecture['title']))
    lecture_formatted = "\n".join(lecture_arr)

    return render_template("index.html", staff_formatted=staff_formatted,
                           lecture_formatted=lecture_formatted)

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, threaded=True)
