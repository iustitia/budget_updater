#import requests

# venv
#  source ~/workspace/venv/googleapi/bin/activate
"""
k = 'secret-secret-secret'

client_id = 'secret-secret.apps.googleusercontent.com'

client_secret= 'secret'

# TODO: authenticate

# url = 'https://sheets.googleapis.com/v4/spreadsheets/secret-secret/values/Sheet1!A1:D5'
url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/Sheet1!A1:D5'

id_test_open = 'secret'
id_moj_budget = 'secret-secret'

url_query.format(id2, key)

resp = requests.get(url)
"""

import httplib2

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

CLIENT_SECRET = 'client_secret.json'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets'
STORAGE = Storage('credentials.storage')

# https://medium.com/@ashokyogi5/a-beginners-guide-to-google-oauth-and-google-apis-450f36389184

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
# Fetch credentials from storage
    credentials = STORAGE.get()
# If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

credentials = authorize_credentials()


def get_google_sheet(spreadsheet_id, sheet_name, cell_range):
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    if sheet_name:
        cell_range = '%s!%s' % (sheet_name, cell_range)
    print(cell_range)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=cell_range).execute()
    print(result['range'])
    values = result.get('values', [])
    return values

def update_cell(spreadsheet_id, sheet_name, cell_range, value):
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    if sheet_name:
        cell_range = '%s!%s' % (sheet_name, cell_range)
    print(cell_range)
    body = {"values": [value]}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=cell_range, valueInputOption='USER_ENTERED',
    body=body).execute()
    print(result.get('range'))
    values = result.get('values', [])
    return values    

id_test_open = 'secret'
id_moj_budget = 'secret'
values = get_google_sheet(id_test_open, 'AnotherSheet', 'A1:E5')

print(values)

budget_values = get_google_sheet(id_moj_budget, 'Luty', 'O74:Q75')
print(budget_values)

updates = update_cell(id_test_open, None, 'E1:H7', ['9', '9', '9'])
print(updates)

updates = update_cell(id_moj_budget, 'Lipiec', 'I184:I184', ['59,98'])
print(updates)
