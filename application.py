import json, pyodbc,os, requests,datetime
from flask import Flask, render_template, request, abort, flash, make_response, session, url_for,redirect
import urllib,adal,uuid,time
from jose import jws
from auth import requires_auth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key' + str(os.urandom(12))
CLIENT_ID = '6be1ec05-2113-4f92-a179-84eb90d05d00'
CLIENT_SECRET = "[7WgmM=Q78Qr?I2nK[R@qDQhe-:sja1x"
REDIRECT_URI = 'https://krassy3.azurewebsites.net/login/authorized'
AUTHORITY_URL = 'https://login.microsoftonline.com/common'
AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
RESOURCE = 'https://graph.microsoft.com/'
API_VERSION = 'beta'
SCOPES = ['User.Read']  # Add other scopes/permissions as needed.
keys_url = 'https://login.microsoftonline.com/krassy.onmicrosoft.com/discovery/keys'
keys_raw = requests.get(keys_url).text
keys = json.loads(keys_raw)
SESSION = requests.Session()

@app.route('/')
def home():
    return render_template(
        'index.html',
        title='Krassy Flask Test App'
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    auth_state = str(uuid.uuid4())
    SESSION.auth_state = auth_state
    prompt_behavior = 'select_account'  # prompt_behavior = 'login'
    params = urllib.parse.urlencode({'response_type': 'code id_token',
                                     'client_id': CLIENT_ID,
                                     'redirect_uri': REDIRECT_URI,
                                     'state': auth_state,
                                     'nonce': str(uuid.uuid4()),
                                     'scope': 'openid email',
                                     'prompt': prompt_behavior,
                                     'response_mode': 'form_post'})

    return redirect(AUTHORITY_URL + '/oauth2/v2.0/authorize?' + params)

@app.route('/login/authorized', methods=['GET', 'POST'])
def authorized():
    # Handler for the application's Redirect Uri. Gets the authorization code from the flask response form dictionary.
    try:
        code = request.form.get('code')
        id_token = request.form.get('id_token')
        session['id_token'] = id_token

        auth_state = request.form.get('state')
        if auth_state != SESSION.auth_state:
            print('state returned to redirect URL does not match!')
            SESSION.auth_state = None
            session.clear()
            return redirect(url_for('/'))

        auth_context = adal.AuthenticationContext(AUTHORITY_URL, api_version=None)

        token_response = auth_context.acquire_token_with_authorization_code(
            code, REDIRECT_URI, RESOURCE, CLIENT_ID, CLIENT_SECRET)

        session['access_token'] = token_response['accessToken']
        session['id_token_decoded'] = json.loads(jws.verify(id_token, keys, algorithms=['RS256']))
        SESSION.headers.update({'Authorization': f"Bearer {token_response['accessToken']}",
                                'User-Agent': 'adal-sample',
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'SdkVersion': 'sample-python-adal',
                                'return-client-request-id': 'true'})

        # print('id_token: {0},"\n", token_response: {1}'.format(id_token,token_response))

        expires_in = datetime.datetime.now() + datetime.timedelta(seconds=token_response.get('expires_in', 3599))
        session["token_expires_in"] = expires_in
        return redirect('/graphcall')
    except Exception as error:
            return (render_template(
                'error.html',
                error= error
            ))

@app.route('/graphcall')
def graphcall():
        """Confirm user authentication by calling Graph and displaying some data."""
        #session contains the id_token+access_token
        if 'id_token' not in session or 'access_token' not in session:
            SESSION.auth_state = None
            session.clear()
            return redirect(url_for('/'))

        endpoint = RESOURCE + API_VERSION + '/me'
        http_headers = {'client-request-id': str(uuid.uuid4())}
        graphdata = SESSION.get(endpoint, headers=http_headers, stream=False).json()
        print(session['id_token_decoded']['email'])
        return render_template('graphcall.html',
                                     graphdata=graphdata,
                                     endpoint=endpoint,
                                     sample='ADAL',
                                     id_token_decoded=session['id_token_decoded'],
                                     id_token=session['id_token'],
                                     access_token=session['access_token'])

@app.route('/key_vault')
def key_vault():
    try:
        msi_endpoint = os.environ["MSI_ENDPOINT"]
        msi_secret = os.environ["MSI_SECRET"]
        token_auth_uri = f"{msi_endpoint}?resource=https://vault.azure.net&api-version=2017-09-01"
        head_msi = {'Secret': msi_secret}
        resp = requests.get(token_auth_uri, headers=head_msi)
        access_token = resp.json()['access_token']
        endpoint = "https://uaekeyvault.vault.azure.net/secrets/mysecret?api-version=2016-10-01"
        headers = {"Authorization": 'Bearer {}'.format(access_token)}
        response = requests.get(endpoint, headers=headers).json()
        return render_template(
            'keyvault.html',
             message =  flash("Secret Value is: {}".format(response.get('value')))
          )
    except Exception as error:
        return render_template(
            'keyvault.html'
            # error = f'error {error}',
        )


@app.route('/azuresql', methods=['POST', 'GET'])
@requires_auth
def azuresql():
    if request.method == 'GET':
        try:
            conn = pyodbc.connect(os.environ['azure_sql'])
            cursor = conn.cursor()
            cursor.execute("SELECT * from employee")
            az_users = cursor.fetchall()
            return render_template(
                'azuresql.html',
                az_users=az_users
            )
        except Exception as error:
             return render_template(
                'azuresql.html',
                 error="Something went wrong {}".format(error),
             )

    elif request.method == 'POST':
         try:
            staff_number = request.form['staff_number']
            fname = request.form['fname']
            lname = request.form['lname']
            gender = request.form['gender']
            birth_date = request.form['birth_date']
            conn = pyodbc.connect(os.environ['azure_sql'])
            cursor = conn.cursor()
            az_users = list(cursor.execute("SELECT staff_number from employee"))
            for x in az_users:
                if int(staff_number) in x:
                    flash(f"ID {staff_number} already exist, please use another ID")
                    return render_template(
                        'azuresql.html',
                        az_users = cursor.execute("select * from employee")
                   )
            sql = ("INSERT INTO employee ""VALUES(?,?,?,?,?)")
            val = (staff_number, fname, lname, gender, birth_date)
            cursor.execute(sql, val)
            conn.commit()
            az_users = cursor.execute("select * from employee")
            return render_template(
                        'azuresql.html',
                        title='SQL Connection Testing',
                        az_users=az_users,
                        message = "Successfully Added"
                    )

         except Exception as error:
             return render_template(
                 'azuresql.html',
                 error=f"Something went wrong {error}"
         )


@app.route('/func')
def azfunc():
    return render_template(
        'function.html',
        title='Azure Function',
    )

@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
    )

@app.route('/404', methods=['GET', 'POST'])
def error404():
    return (render_template(
        'error.html',
        error='404 Not Found was triggered from the server..testing error messages..'
    )),404

@app.route('/500', methods=['GET', 'POST'])
def error500():
     return (render_template(
        'error.html',
        error='500 Internal Server Error was triggered from the server..testing error messages..'
    )),500

@app.route('/echo', methods=['GET', 'POST'])
def api_echo():
    if request.method == 'GET':
        hd = request.headers
        return render_template('headers.html',hd=hd)

    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'text/plain':
            return "Text Message: " + request.data

        elif request.headers['Content-Type'] == 'application/json':
            return "JSON Message: " + json.dumps(request.json)

        elif request.headers['Content-Type'] == 'application/octet-stream':
            return "Binary message written!"

@app.route('/logout')
def logout():
    """signs out the current user from the session."""
    session['access_token'] = None
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)