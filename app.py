from flask import Flask, render_template, request, abort
import logging
import os
import sched
import yaml
import sys
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
    news_datasheet = Spreadsheet(config['news_datasheet'], credentials, True, 60*60)
    sponsor_datasheet = Spreadsheet(config['sponsor_datasheet'], credentials, True, 60*60)

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
    # format news data
    if config['live_update']:
        news_data = news_datasheet.get_data()
    else:
        news_data = []
    news_arr = []
    for news in news_data:
        news_arr.append("""
            <div>
                <b>%s</b> : <span>%s</span>
            </div> 
        """ % (news['date'], news['text']))
    news_formatted = "\n".join(news_arr)

    # format sponsor data
    if config['live_update']:
        sponsor_data = sponsor_datasheet.get_data()
    else:
        sponsor_data = []
    sponsor_arr = []
    for sponsor in sponsor_data:
        sponsor_arr.append("""
            <section class="col-sm-3">
                <a href = "%s" style="color:white;text-decoration: none">
                    <img src="%s"/>
                    <h2>%s</h2>
                </a>
            </section>
        """ % (sponsor['link'], sponsor['image'], sponsor['name']))
    sponsor_formatted = "\n".join(sponsor_arr)

    return render_template(
        "home.html",
        news_formatted=news_formatted,
        sponsor_formatted=sponsor_formatted,
    )

@app.route("/resources")
def resources():
    # format lecture data
    if config['live_update']:
        lecture_data = lecture_datasheet.get_data()
    else:
        lecture_data = [] # for local development only
    lecture_arr = []
    for lecture in lecture_data:
        # mark empty resources in red
        color = {}
        for field in ['prelecture', 'slides', 'video', 'demo']:
            color[field] = 'resource_missing' if (lecture[field] == "") else 'resource_present'
        lecture_arr.append("""
            <tr>
                <td><span><b>Lecture %s: </b>%s</span></td>
                <td><a href="%s" class="%s"><i class="fas fa-book"></i></a></td>
                <td><a href="%s" class="%s"><i class="fas fa-chalkboard"></i></a></td>
                <td><a href="%s" class="%s"><i class="fas fa-video"></i></a></td>
                <td><a href="%s" class="%s"><i class="fas fa-code"></i></a></td>
            </tr>
        """ % (lecture['lecture_id'], lecture['title'], lecture['prelecture'],
               color['prelecture'], lecture['slides'], color['slides'],
               lecture['video'], color['video'], lecture['demo'], color['demo']))
    lecture_formatted = "\n".join(lecture_arr)

    return render_template(
        "resources.html",
        lecture_formatted=lecture_formatted,
    )

@app.route("/staff")
def staff():
    # format staff data
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

        border = "instructor-bg" if staff["officer"] else "staff-bg"

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

    return render_template(
        "staff.html",
        staff_formatted=staff_formatted,
    )

@app.route("/projects")
def project():
    return render_template(
        "projects.html",
    )

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, threaded=True)
