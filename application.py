import json
import os
import pyodbc
from flask import Flask, render_template, request, abort, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Krassy+Secret_19'


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
        return render_template('login.html')

      elif request.method == 'POST':
          try:
            login_name = request.form['LoginName']
            Password = request.form['Password']
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:krassy.database.windows.net;PORT=1433;DATABASE=krassy_db;UID=krassykirov;PWD=Mitra194455$')
            cursor = conn.cursor()
            username = cursor.execute("select LoginName from Users where LoginName='%s'"% login_name).fetchval()
            password = cursor.execute("select Password from Users where LoginName='%s'"% login_name).fetchval()
            if username == login_name and password == Password:
                return render_template(
                    'login.html',
                     message="You Are Logged In"
                )
            else:
                flash("You Are NOT Logged In")
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



@app.route('/azuresql', methods=['POST', 'GET'])
def azuresql():
    if request.method == 'GET':
        try:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:krassy.database.windows.net;PORT=1433;DATABASE=krassy_db;UID=krassykirov;PWD=Mitra194455$')
            cursor = conn.cursor()
            cursor.execute("select * from [dbo].[employee]")
            az_users = cursor.fetchall()
            return render_template(
                'azuresql.html',
                title='Azure SQL Testing',
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
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:krassy.database.windows.net;PORT=1433;DATABASE=krassy_db;UID=krassykirov;PWD=Mitra194455$')
            cursor = conn.cursor()
            az_users = list(cursor.execute("select staff_number from [dbo].[employee]"))
            for x in az_users:
                if int(staff_number) in x:
                    flash("ID {} already exist, please use another ID".format(staff_number))
                    return render_template(
                        'azuresql.html',
                        az_users = cursor.execute("select * from [dbo].[employee]")
                   )
            sql = ("INSERT INTO dbo.employee ""VALUES(?,?,?,?,?)")
            val = (staff_number, fname, lname, gender, birth_date)
            cursor.execute(sql, val)
            conn.commit()
            az_users = cursor.execute("select * from [dbo].[employee]")
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



if __name__ == '__main__':
    app.run()
