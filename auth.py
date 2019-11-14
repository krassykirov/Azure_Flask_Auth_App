import adal, requests
from application import app


@app.route('/auth')
def get_token():

    url = 'https://login.microsoftonline.com/krassy.onmicrosoft.com/oauth2/v2.0/token'

    data = {
        'grant_type': 'client_credentials',
        'client_id': "6be1ec05-2113-4f92-a179-84eb90d05d00",
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': "n2mQ02=2_oWkqagb-OpGR/B_OI:?2eE/",
    }

    r = requests.post(url, data=data)
    token = r.json().get('access_token')

    headers = {
        'Content-Type' : 'application\json',
        'Authorization': 'Bearer {}'.format(token)
    }

    user_endpoint = 'https://graph.microsoft.com/v1.0/users'
    r = requests.get(user_endpoint, headers=headers)
    result = r.json()
    return result