from crypt import methods
from flask import Flask, jsonify,render_template,request,redirect,session
from flask_mysqldb import MySQL
import yaml
import mysql.connector
import re
from mysql.connector import Error


def connect():
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='test1',
                                       user='root',
                                       password='Alen@199)')
        if conn.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    connect()

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
        print(loginPassword)
        cur=mysql.connection.cursor()
        passwordQuery=cur.execute("SELECT * FROM login WHERE user_name=%s and user_password=%s",(loginUser,loginPassword))
        print(passwordQuery)
        # userPassword=cur.fetchone()
        account=cur.fetchone()
        print(account)
        print(account[0])
        # if loginPassword==userPassword[0]:
        #     msg = 'Logged in successfully !'
        #     # return 'success'
        #     return redirect('/slot')
        # else:
        #     msg = 'Incorrect username / password !'
        if account:
            session['loggedin'] = True
            print(account[0])
            session['id'] = account[0]
            session['username'] = account[2]
            msg = 'Logged in successfully !'
            return render_template('slot.html', msg = msg,loginUser=loginUser)
        elif not loginUser or not loginPassword :
            msg = 'Please fill out the form !'
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
        print(alreadyreg)
        account=cur.fetchone()
        # if alreadyreg>=1:
        #     msg='User already exists!'
        # else:
        #     if newPassword==confirmPassword:
        #         cur.execute("INSERT INTO login(user_name,user_password) values(%s,%s)",(registerUser,confirmPassword))
        #         mysql.connection.commit()
        #         # return redirect('/slot')
        #         msg='Registered Successfully! Login to continue'
            
        #     else:
        #         msg="Passwords doesn't match"
        if account:
            msg = 'Account already exists !'
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        #     msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', registerUser):
            msg = 'Username must contain only characters and numbers !'
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
        print(slotName)
        slotNames=cur.fetchone()
        print(slotNames)
        print(slotNames[0])
        slotCount=slotNames[0]       

        # Checking if maximum entry limit is reached
        if slotCount>=20:
            slotId= int(slotName[-1])
            query="SELECT slot_entries from slot"
            cur.execute(query)
            cur.fetchall()
            c=slotId
            # Allocating delivery request to next available slot
            for i in range (0,4):
                if c==4 and slotCount>=20:
                    c=1
                print(c)
                availableSlot='Slot '+ (str(c+1))
                print('---------------------')
                print(availableSlot)
                slotQuery2="SELECT slot_entries FROM slot where slot_name = %s"
                cur.execute(slotQuery2,(availableSlot,))
                slotNames1=cur.fetchone()
                if slotNames1[0]<20:
                    print(slotNames1[0])
                    cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,availableSlot))
                    slotCount=slotCount+1
                    print(slotCount)
                    updatedSlotCount=slotNames1[0]+1
                    print('--------',updatedSlotCount,'-----------')
                    cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(updatedSlotCount,availableSlot))
                    mysql.connection.commit()
                    cur.close()
                    break
                elif c<5:
                    c=c+1
                else:
                    return 'NO AVAILABLE SLOTS'
            return ('Alloted to ' + availableSlot)
        else:
            cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,slotName))
            slotCount=slotCount+1
            print(slotCount)
            cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(slotCount,slotName))
            mysql.connection.commit()
            cur.close()
            return 'Alloted to slot ' + slotName
    return render_template('slot.html')

@app.route('/status')
def status():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("SELECT * FROM slot")
    if resultValue>0:
        slotDetails=cur.fetchall()
        return render_template('status.html',slotDetails=slotDetails)

if __name__==("__main__"):
    app.run(debug=True)