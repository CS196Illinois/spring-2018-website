# spring-2018-website

## Server
To run with Gunicorn in a production environment, do `./runserver.sh`
To run with the Flask development engine (eg. for testing), do `python app.py`
In order to have the server listen on port 80, must be run as sudo

## Credentials
To use this service you will need to have access to the course Google Drive
and set up a service account as shown in the *gspread* documentation [here](http://gspread.readthedocs.io/en/latest/oauth2.html)

The Google Drive API also needs to be enabled for this, and course files will
need to be shared with the email in the credentials file.

## Local Development
It is possible to deploy the server for local development by opening `config.yaml` and setting
the option `live_update` to `false`. This disables fetching data from Google Drive.

## Layout
Main folder:
 - `runserver.sh`: shell script to launch server with Gunicorn
 - `main.py`: Python file to launch the server with Github webhook
 - `app.py`: Python file with the server-side code
 - `requirements.txt`: List of Python module dependencies
 - `config.yaml`: Configuration options 
 - `asset_manager.py`: Module to manage files and spreadsheets on Drive
 - `client_secret.json`: Authentication credentials for Drive

`static` folder:
 - `css/*`: CSS files for the site
 - `fonts/*`: font files for the site
 - `js/*`: front-end Javascript files for the site
 - `sass/*`: SASS style sheets for the site

`templates` folder:
 - `favicon.ico`: icon to display in browser header bar
 - `index.html`: HTML for site home page
