import os, calendar, time
import sqlite3, re

from flask import Flask, render_template, request, g, current_app, send_from_directory

app = Flask(__name__)

DATABASE = '/home/ubuntu/flaskapp/mydb/mydb.db'
DIRECTORY_NAME = '/home/ubuntu/flaskapp/static'

@app.route('/',methods=['POST','GET'])
def starting():
    if request.method == "POST":
        user_Name = request.form['username']
        password = request.form['password']
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            cur = db.cursor()
            cur.execute('select * from tablename where user_Name =?', (user_Name,))
            row = cur.fetchone()
            if(row == None):
                return render_template('Welcome.html', error1='false')
            else:
                cur.execute('select * from tablename where user_Name =? and password =?', (user_Name, password,))
                row = cur.fetchone()
                if (row == None):
                    return render_template('Welcome.html', error3='false')
                else:
                    wc= row[6]
                    if(wc == None):
                        wc = ""
                    fn = row[5]
                    if(fn == None):
                        fn = ""
                    return render_template('display.html',userfirstname=row[0],userlastname=row[1],email=row[4],Filename=fn,wordcount=wc, username = row[2])
            db.close()
        return render_template('Welcome.html')

    return render_template('Welcome.html')

@app.route('/usercreation', methods=['POST','GET'])
def getvalue():

    if request.method == 'POST':
        user_first_name = request.form['firstname']
        user_last_name = request.form['lastname']
        emailid = request.form['email']
        password = request.form['pwd']
        username = request.form['username']
        fileName=""
        wordcount=0
        db = getattr(g, '_database', None)
        if db is None:
                db = g._database = sqlite3.connect(DATABASE)
                cur = db.cursor()
                cur.execute('select * from tablename where user_Name =?', (username,))
                row = cur.fetchone()
                if(row == None ):
                    cur.execute('select * from tablename where email =?', (emailid,))
                    row = cur.fetchone()
                    if(row == None):
                        cur.execute("insert into tablename (first_Name, last_Name, user_Name,password,email) values (?,?,?,?,?)",(user_first_name,user_last_name,username,password,emailid))
                        db.commit()
                        return render_template('display.html',userfirstname=user_first_name,userlastname=user_last_name,email=emailid, username=username, Filename=fileName, wordcount=wordcount)
                    else:
                        return render_template('usercreation.html', error2='true')
                else:
                    return render_template('usercreation.html', error1 = 'true')
                db.close()
        return render_template('usercreation.html')
    return render_template('usercreation.html')

@app.route('/files/<file_name>')
def get_file(file_name):
	directory = os.path.join(current_app.root_path, DIRECTORY_NAME)
	return send_from_directory(directory, file_name, as_attachment=True)

@app.route('/update', methods=['POST','GET'])
def update_file():
    file = request.files['file']
    username = request.values.get("username")

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cur = db.cursor()
        cur.execute('select * from tablename where user_Name =?', (username,))
        row = cur.fetchone()
        file_ext = file.filename
        value1 = calendar.timegm(time.gmtime())
        fileName = username + str(value1) + ".txt"
        tg_Dir = DIRECTORY_NAME + "/" + fileName
        if (row == None):
            return render_template('Welcome.html', error1='false')
        else:
            user_first_name = row[0]
            user_last_name = row[1]
            emailid = row[4]
            file.save(tg_Dir)
            cur.execute('update tablename set Filename =? where user_Name =?', (fileName,username,))
            db.commit()
            if file_ext.endswith('.txt'):
                file1 = open(tg_Dir, "rt")
                data = file1.read()
                words = data.split()
                wordCount = len(words)
                cur.execute('update tablename set wordCount =? where user_Name =?', (wordCount,username,))
                db.commit()
            return render_template('display.html',userfirstname=user_first_name,userlastname=user_last_name,email=emailid,Filename= fileName, wordcount= wordCount )
    return render_template('usercreation.html')


if __name__ == '__main__':
  app.run(debug=True)