import os

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = 'https://krassy.net/login/authorized'  #'https://krassy3.azurewebsites.net/login/authorized'
AUTHORITY_URL = 'https://login.microsoftonline.com/common'
AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
RESOURCE = 'https://graph.microsoft.com/'
API_VERSION = 'beta'
SCOPES = ['User.Read']  # Add other scopes/permissions as needed.
