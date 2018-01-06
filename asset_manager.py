from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import FileNotDownloadableError 

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import yaml
import csv
import os
import time
import shutil


class Spreadsheet():

    def __init__(self, filename):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        self.client = gspread.authorize(creds)
 
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        self.sheet = self.client.open(filename).sheet1

    def extract(self):
        # Extract and print all of the values
        sheet_data = self.sheet.get_all_records()
        return sheet_data


class AssetFolder():

    def __init__(self, drive, path, drive_folder_id, cached=False, max_age=None):
        self.drive = drive
        self.path = path
        self.drive_folder_id = drive_folder_id
        self.manifest = []

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

    def update(self):
        folder_list_file = self.drive.ListFile({'q': "'%s' in parents and trashed=false" % self.drive_folder_id}).GetList()
        for asset in folder_list_file:
            try:
                asset.GetContentFile(self.path+'/'+asset['title'])
                self.manifest.append(asset['title'])
            except FileNotDownloadableError:
                pass

        # update caching metadata
        if self.cached:
            self.last_updated = time.time()

    def remove(self):
        shutil.rmtree(self.path)
        self.manifest = []
