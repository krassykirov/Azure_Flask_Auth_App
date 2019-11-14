import json
import os
import pyodbc
import requests
from flask import Flask, render_template, request, abort, flash, make_response
import adal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Krassy Flask Test App'
    )

@app.route('/login', methods=['GET','POST'])
def login():
      if request.method == 'GET':
            name = request.cookies.get('LoginName')
            if name is not None:
                return render_template(
                    'login.html',
                    error = 'Welcome {}'.format(name.split('@')[0])
                )
            else:
                return render_template('login.html' )

      elif request.method == 'POST':
          try:
            login_name = request.form['LoginName']
            Password = request.form['Password']
            conn = pyodbc.connect(os.environ['azure_sql'])
            cursor = conn.cursor()
            username = cursor.execute("select LoginName from Users where LoginName='%s'"% login_name).fetchval()
            password = cursor.execute("select Password from Users where LoginName='%s'"% login_name).fetchval()
            if username == login_name and password == Password:
                resp = make_response(render_template('login.html',message="Welcome {}!".format(login_name)))
                resp.set_cookie('LoginName', login_name)
                return resp
            else:
                return render_template(
                    'login.html',
                     message="You Are NOT Logged In"
                )

          except Exception as error:
                return render_template(
                    'login.html',
                    error="Something went wrong {}".format(error),
                    message=error
                )

@app.route('/secret')
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
            'login.html',
           error= response
        )
    except Exception as error:
        return render_template(
            'error.html'
        )


@app.route('/azuresql', methods=['POST', 'GET'])
def azuresql():
    if request.method == 'GET':
        try:
            conn = pyodbc.connect(os.environ['SQLAZURECONNSTR_azure_sql'])
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * from employee")
                az_users = cursor.fetchall()
                return render_template(
                    'azuresql.html',
                    az_users=az_users,
                    error = "azure_sql {}".format(os.environ['azure_sql']),
                    message = "azure_sql1 {}".format(os.environ['azure_sql1'])
                )
            else:
                conn = pyodbc.connect(os.environ['azure_sql'])
                cursor = conn.cursor()
                cursor.execute("SELECT * from employee")
                az_users = cursor.fetchall()
                return render_template(
                    'azuresql.html',
                    az_users=az_users,
                    error="azure_sql {}".format(os.environ['azure_sql']),
                    message="azure_sql1 {}".format(os.environ['azure_sql1'])
                )

        except Exception as error:
             return render_template(
                'azuresql.html',
                 error="Something went wrong {}".format(error),
                 message = "azure_sql {}".format(os.environ['azure_sql'])
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
                    flash("ID {} already exist, please use another ID".format(staff_number))
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
                 error="Something went wrong {}".format(error),
                 message="Entered Exception Block"
             )


@app.route('/echo', methods=['GET', 'POST'])
def api_echo():
    if request.method == 'GET':
        hd = request.headers
        a = []
        for h in hd.items():
            a.append('{} <br/>'.format(h))

        return "ECHO: GET\n' {}".format(a)

    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'text/plain':
            return "Text Message: " + request.data

        elif request.headers['Content-Type'] == 'application/json':
            return "JSON Message: " + json.dumps(request.json)

        elif request.headers['Content-Type'] == 'application/octet-stream':
            return "Binary message written!"


@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
    )


@app.route('/testing')
def testing():
    return render_template(
        'testing.html',
        title='Testing..',
    )

@app.route('/img')
def img():
    return render_template(
        'test2.html',
        title='Testing',
    )

@app.route('/404', methods=['GET', 'POST'])
def error404():
    return abort(404, "404!")


@app.route('/500', methods=['GET', 'POST'])
def error500():
    return abort(500, "500!")

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

    user = {
        "accountEnabled": True,
        "displayName": "created_from_python",
        "mailNickname": "created_from_python",
        "userPrincipalName": "created_from_python@krassy.onmicrosoft.com",
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False,
            "password": "P@ssword"
        }
    }
    user_endpoint = 'https://graph.microsoft.com/v1.0/users'
    result = requests.post(user_endpoint,data = json.dumps(user),headers=headers)
    return result.content

if __name__ == '__main__':
    app.run()
