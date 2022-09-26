from crypt import methods
from flask import Flask, jsonify,render_template,request,redirect,session,url_for
from flask_mysqldb import MySQL
import yaml
import mysql.connector
import re
from mysql.connector import Error


app=Flask(__name__)

app.secret_key = '123'

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] =db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB'] =db['mysql_db']

mysql=MySQL(app)

@app.route('/') 
def index():
    return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        loginDetails=request.form
        loginUser=loginDetails['loginUser']
        loginPassword=loginDetails['loginPassword']
        cur=mysql.connection.cursor()
        passwordQuery=cur.execute("SELECT * FROM login WHERE user_name=%s and user_password=%s",(loginUser,loginPassword))
        account=cur.fetchone()
        if account != None:
            session['loggedin'] = True
            session['id'] = account[0]
            session['password'] = account[2]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return redirect(url_for('slot',loginUser=loginUser))
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html',msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/login')

@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method=='POST':
        registerDetails=request.form
        registerUser=registerDetails['registerName']
        newPassword=registerDetails['newPassword']
        confirmPassword=registerDetails['confirmPassword']
        cur=mysql.connection.cursor()
        alreadyreg=cur.execute("SELECT * FROM login WHERE user_name=%s",(registerUser,))
        account=cur.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not registerUser or not newPassword or not confirmPassword:
            msg = 'Please fill out the form !'
        else:
            cur.execute('INSERT INTO login(user_name,user_password) VALUES ( % s, % s)', (registerUser, newPassword))
            mysql.connection.commit()
            msg = 'You have successfully registered ! Login to continue' 
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

        
    return render_template('register.html',msg=msg)

@app.route('/slot',methods=['GET','POST'])
def slot():
    msg=''
    # Get data from the form
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['userName']
        address=userDetails['address']
        phoneNo=userDetails['phoneNo']
        slotName=userDetails['slotName']
        cur=mysql.connection.cursor()
        slotQuery="SELECT slot_entries FROM slot where slot_name = %s"
        cur.execute(slotQuery,(slotName,))
        slotNames=cur.fetchone()
        slotCount=slotNames[0]       

        # Checking if maximum entry limit is reached
        if slotCount>=20:
            cur.execute("select slot_id from slot where slot_name=%s",(slotName,))
            slotEntries=cur.fetchone()
            slotId=slotEntries[0]
            for i in range(slotId,5):
                cur.execute("select slot_entries from slot where slot_id=%s",(i,))
                entries=cur.fetchone()
                if entries[0]<20:
                    cur.execute("SELECT slot_name FROM slot WHERE slot_id=%s",(i,))
                    availableSlotName=cur.fetchone()
                    availableSlot=availableSlotName[0]
                    cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,availableSlot))
                    entry=entries[0]+1
                    cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(entry,availableSlot))
                    mysql.connection.commit()
                    cur.close
                    msg= 'Selected slot was not available so alloted to '+availableSlot
                    alotted=True
                    return render_template('slot.html',msg=msg)
                else:
                    continue
            alotted=False
            if alotted!=True:
                for i in range(1,slotId):
                    cur.execute("select slot_entries from slot where slot_id=%s",(i,))
                    entries=cur.fetchone()
                    if entries[0]<20:
                        cur.execute("SELECT slot_name FROM slot WHERE slot_id=%s",(i,))
                        availableSlotName=cur.fetchone()
                        availableSlot=availableSlotName[0]
                        cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,availableSlot))
                        entry=entries[0]+1
                        cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(entry,availableSlot))
                        mysql.connection.commit()
                        cur.close
                        msg= 'Selected slot was not available so alloted to '+availableSlot
                        return render_template('slot.html',msg=msg)
                    else:
                        continue
                msg= 'No available slots'
            return render_template('slot.html',msg=msg)
        else:
            cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,slotName))
            slotCount=slotCount+1
            cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(slotCount,slotName))
            mysql.connection.commit()
            cur.close()
            msg= 'Alloted to slot ' + slotName
    return render_template('slot.html',msg=msg)

@app.route('/status')
def status():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("SELECT * FROM slot")
    if resultValue>0:
        slotDetails=cur.fetchall()
        return render_template('status.html',slotDetails=slotDetails)

if __name__==("__main__"):
    app.run(debug=True)