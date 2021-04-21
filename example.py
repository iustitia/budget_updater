import httplib2

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

CLIENT_SECRET = 'client_secret.json'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets.readonly'
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

def get_google_sheet(spreadsheetId):
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    rangeName = 'A1:E5'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, sheet='AnotherSheet').execute()
    values = result.get('values', [])
    return values


id_test_open = 'secret'
values = get_google_sheet(id_test_open)

print(values)
