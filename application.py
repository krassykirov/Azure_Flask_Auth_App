import json
import os
import pyodbc
import requests
from flask import Flask, render_template, request, abort, flash, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key' + str(os.urandom(12))

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
                 message =error
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
        return render_template('headers.html',hd=hd)

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
    return (render_template(
        'error.html',
        error='404 Not Found'
    )),404

@app.route('/500', methods=['GET', 'POST'])
def error500():
     return (render_template(
        'error.html',
        error='500 Server Error'
    )),500


if __name__ == '__main__':
    app.run()
