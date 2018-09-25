import datetime
import os
from collections import OrderedDict
from pprint import pprint

import httplib2
import oauth2client
import yaml

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, 'google_api', 'key.yaml'), 'r') as y:
    config = yaml.load(y)


class Api:
    CLIENT_SECRET = 'client_secret.json'
    SCOPE = 'https://www.googleapis.com/auth/spreadsheets'
    STORAGE = Storage('credentials.storage')

    id_test_open = config['spreadsheet_id_test']
    id_my_budget = config['spreadsheet_id_my_budget']
    categories = None

    def __init__(self, spreadsheet_id=None):
        self.authorize_credentials()
        if spreadsheet_id is None:
            self.spreadsheet_id = self.id_my_budget
        else:
            self.spreadsheet_id = spreadsheet_id
        self._get_service()

    def authorize_credentials(self):
        # Fetch credentials from storage
        self.credentials = self.STORAGE.get()
        # If the credentials doesn't exist in the storage location then run the flow
        if self.credentials is None or self.credentials.invalid:
            flow = flow_from_clientsecrets(self.CLIENT_SECRET, scope=self.SCOPE)
            http = httplib2.Http()
            self.credentials = run_flow(flow, self.STORAGE, http=http)

    def _get_service(self):
        http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    def get_google_sheet(self, cell_range, sheet_name=None, format_option='FORMATTED_VALUE'):
        if sheet_name:
            cell_range = '%s!%s' % (sheet_name, cell_range)
        # print(cell_range)
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=cell_range, valueRenderOption=format_option).execute()
        # print(result)
        values = result.get('values', [])

        return values

    def _get_cell(self, cell_range, sheet_name=None, format_option='FORMATTED_VALUE'):
        return self.get_google_sheet(cell_range, sheet_name, format_option)

    def update_cell(self, cell_range, value, sheet_name=None):

        if sheet_name:
            cell_range = '%s!%s' % (sheet_name, cell_range)
        body = {"values": [[value]]}
        try:
            result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=cell_range, valueInputOption='USER_ENTERED',
            body=body).execute()

        except oauth2client.client.HttpAccessTokenRefreshError:
            self.authorize_credentials()
            # retry:
            result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=cell_range, valueInputOption='USER_ENTERED',
            body=body).execute()

        values = result.get('values', [])
        return values

    def update_expense(self, cell_range, value, sheet_name=None):
        current_value = self._get_cell(cell_range, sheet_name, format_option='FORMULA')
        if not current_value:
            self.update_cell(cell_range, value, sheet_name)
        else:
            current_value = current_value[0][0]
            if isinstance(current_value, str):
                value = '{}+{}'.format(current_value.strip(), value)
            elif isinstance(current_value, (int, float)):
                value = '={}+{}'.format(current_value, value)
            self.update_cell(cell_range, value, sheet_name)

    def get_categories(self):
        if self.categories:
            return self.categories
        categories_range = 'B1:C254'
        categories_list = self.get_google_sheet(categories_range, 'Sierpień')
        categories_list.insert(0, [])

        categories = OrderedDict()
        for i, el in enumerate(categories_list):
            assert type(el) == list
            if i > 45 and el and el[0] != '.' and len(el[0]) < 25:
                categories[el[0]] = i

        self.categories = categories

        return self.categories

    def update_expense_by_cat(self, category, value, date=None):
        category = self.categories[category]
        if date is None:
            date = 'today'
        sheet_name, day = self.get_sheet_and_column_for_date(date)
        # print(sheet_name, day)
        # print({'day': day, 'category': category})
        cell_range = '{0}{1}:{0}{1}'.format(day, category)
        self.update_cell(cell_range, value, sheet_name)

    def update_expense_by_cat_id(self, category_id, value, date=None):
        if date is None:
            date = 'today'
        sheet_name, day = self.get_sheet_and_column_for_date(date)
        # print(sheet_name, day)
        # print({'day': day, 'category': category_id})
        if type(value) != str:
            value = str(value)
        value = value.replace('.', ',')
        cell_range = '{0}{1}:{0}{1}'.format(day, category_id)
        self.update_expense(cell_range, value, sheet_name)

    def get_sheet_and_column_for_date(self, date):
        month = date.month
        day = date.day

        months = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień',
                  'Październik', 'Listopad', 'Grudzień']
        import string
        day_index = [s for s in string.ascii_uppercase]
        day_index.extend(['{}{}'.format(s, ss) for s in string.ascii_uppercase for ss in string.ascii_uppercase])

        # spr czy dobry dzień
        return months[month], day_index[day+7]
