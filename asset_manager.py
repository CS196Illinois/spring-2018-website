import gspread
from oauth2client.service_account import ServiceAccountCredentials as Credentials

import yaml
import csv
import os
import time
import shutil
import httplib2
import requests
from apiclient import discovery

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CLIENT_SECRET = 'client_secret.json'


def authenticate_gdrive():
    credentials = Credentials.from_json_keyfile_name(CLIENT_SECRET, SCOPE)
    return credentials


class Spreadsheet():

    def __init__(self, filename, credentials, cached=False, max_age=None):
        # use creds to create a client to interact with the Google Drive API
        self.client = gspread.authorize(credentials)
 
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        self.sheet = self.client.open(filename).sheet1
        self.data = None

        # set up caching metadata
        self.cached = cached
        if cached:
            self.max_age = max_age
            self.last_updated = -1

    def get_data(self):
        if not self.cached:
            self.client.login()
            self.data = self.sheet.get_all_records()
        elif time.time() - self.last_updated > self.max_age:
            self.client.login()
            self.data = self.sheet.get_all_records()
            self.last_updated = time.time()

        return self.data


class AssetFolder():

    #def __init__(self, drive, path, drive_folder_id, credentials, cached=False, max_age=None):
    def __init__(self, path, drive_folder_id, credentials, cached=False, max_age=None):
        #self.drive = drive
        self.path = path
        self.drive_folder_id = drive_folder_id
        self.manifest = []

        self.credentials = credentials
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)

        # set up directory and drive
        try:
            os.mkdir(path)
        except FileExistsError: # old assets not cleaned up
            shutil.rmtree(path)
            os.mkdir(path)

        # set up caching metadata
        self.cached = cached
        if cached:
            self.max_age = max_age
            self.last_updated = time.time()


    def __download_file(self, file_id, file_name): 
        results = requests.get("https://www.googleapis.com/drive/v3/files/%s?alt=media" % file_id,
                               headers={'Authorization': 'Bearer %s' % self.credentials.get_access_token().access_token})
        if results.status_code != 200: return -1
        with open(file_name, 'wb') as f:
            for chunk in results.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        return 0


    def update(self):
        results = self.service.files().list(
            q="'%s' in parents" % self.drive_folder_id,
            fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))
                # only add to manifest if successfully loaded
                if not self.__download_file(item['id'], os.path.join(self.path, item['name'])):
                    self.manifest.append(item['name'])


    def remove(self):
        shutil.rmtree(self.path)
        self.manifest = []
