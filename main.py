from flask import Flask,request, session, redirect, url_for, render_template
from mylib import check_photo,course_paid,sutudent_check_photo
from pathlib import Path

import os
import time
import pymysql
from werkzeug.utils import secure_filename



app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.secret_key = "super secret key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about_us')
def about_us():
    return render_template('AboutUs.html')

@app.route('/contact_us')
def contact_us():
    return render_template('ContactUs.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
        cur = conn.cursor()

        email = request.form['T1']
        password = request.form['T2']

        sql = "select * from login where email='"+email+"' and password='"+password+"'"

        cur.execute(sql)
        n = cur.rowcount
        if n==1:
            data=cur.fetchone()
            usertype=data[2]

            #creating session
            session['usertype']=usertype
            session['email']=email
            if usertype=='student':
                session['reg_no']=email
                print(session['reg_no'])
            if usertype == "admin":
                return redirect(url_for('admin_home'))
            elif usertype=="accountant":
                return redirect(url_for('accountant_home'))
            elif usertype=="student":
                return redirect(url_for('student_dash'))
            else:
                return render_template('login.html',msg="Email And Password Incorrect")
        else:
            return render_template("login.html",msg="Email And Password Incorrect")
    else:
        return render_template('login.html')

@app.route('/test_admin_login')
def test_admin_login():
    session['email'] = 'admin@example.com'
    session['usertype'] = 'admin'
    return "Admin logged in"
@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('usertype',None)
        session.pop('email',None)
        return redirect('login')
    else:
        return redirect('login')
@app.route('/change_password',methods=['GET','POST'])
def change_password():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="accountant" or usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                old_password = request.form['T1']
                new_password = request.form['T2']

                sql = "UPDATE login set password=' "+new_password+"' where email='"+email+"' and password='"+old_password+"'"

                cur.execute(sql)
                n = cur.rowcount
                if n==1:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('ChangePassword.html',msg="Password Changed",k=k)
                else:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('ChangePassword.html',msg="Old Password Incorrect",k=k)
            else:
                if usertype=="admin":
                    k="k"
                else:
                    k="l"
                return render_template("ChangePassword.html",k=k)
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))




@app.route('/admin_reg',methods=['GET','POST'])
def admin_reg():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'POST':
                try:
                    conn = pymysql.connect(host='localhost',user="root",db='student',passwd='',port=3306,autocommit=True)
                    cur1 = conn.cursor()
                    cur2 = conn.cursor()


                    Name= request.form['T1']
                    Email = request.form['T2']
                    Contact = request.form['T3']
                    Password = request.form['T4']
                    address = request.form['T5']
                    dob = request.form['T6']
                    gender = request.form['T7']

                    ut = "admin"

                    sql1 = "INSERT INTO admin VALUES('"+Name+"','"+Email+"','"+Contact+"','"+address+"','"+dob+"','"+gender+"')"
                    sql2 = "INSERT INTO login VALUES('"+Email+"','"+Password+"','"+ut+"')"

                    cur1.execute(sql1)
                    cur2.execute(sql2)

                    n1 = cur1.rowcount
                    n2 = cur2.rowcount
                    if n1==1 and n2==1:
                        msg = "Registered Successfully"
                    else:
                        msg = "Registered Failed"
                    return render_template('AdminReg.html',msg=msg)
                except pymysql.err.IntegrityError:
                    return render_template('AdminReg.html',msg="User Already Exist")
            else:
                return render_template('AdminReg.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


@app.route('/auth_error')
def auth_error():
    return render_template("AuthError.html")

@app.route('/admin_home')
def admin_home():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()
            cur1 = conn.cursor()
            cur2 = conn.cursor()


            sql = "select * from admin where email='"+email+"'"
            sql1 = "SELECT photo FROM photos WHERE email=%s"
            sql2 = "select * from  students"

            cur.execute(sql)
            cur2.execute(sql2)
            cur1.execute(sql1, (email,))
            row = cur1.fetchone()
            photo = row[0] if row else None
            n=cur.rowcount
            if n==1:
                data=cur.fetchall()
                data1=cur2.fetchall()
                return render_template("AdminHome.html",data=data,data1=data1,photo=photo,n=n)
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/show_admin')
def show_admin():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()

            sql = "select * from admin"

            cur.execute(sql)
            n=cur.rowcount
            if n>0:
                data=cur.fetchall()
                return render_template("ShowAdmin.html",data=data)
            else:
                return render_template("ShowAdmin.html",msg="Data Not Found")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/accountant_reg',methods=['GET','POST'])
def accountant_reg():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'POST':
                try:
                    conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                    cur1 = conn.cursor()
                    cur2 = conn.cursor()

                    em_id = request.form['T1']
                    name = request.form['T2']
                    contact = request.form['T3']
                    address = request.form['T4']
                    gender = request.form['T5']
                    email = request.form['T6']
                    password = request.form['T7']
                    usertype =  "accountant"

                    sql1 = "INSERT INTO accountant VALUES('"+em_id+"','"+name+"','"+contact+"','"+address+"','"+gender+"','"+email+"')"
                    sql2 = "INSERT INTO login VALUES('"+email+"','"+password+"','"+usertype+"')"

                    cur1.execute(sql1)
                    cur2.execute(sql2)

                    n1 = cur1.rowcount
                    n2 = cur2.rowcount
                    if n1==1 and n2==1:
                        return render_template('AccountantReg.html',msg="Registered Successfully")
                    else:
                        return render_template('AccountantReg.html',msg="Registered Failed")
                except pymysql.err.IntegrityError:
                    return render_template('AccountantReg.html',msg="User Already Exist")
            else:
                return render_template('AccountantReg.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/manage_accountant')
def manage_accountant():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost',user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()

            sql = "select * from accountant"
            cur.execute(sql)
            n=cur.rowcount
            if n>0:
                data=cur.fetchall()
                return render_template("ManageAccountant.html",data=data)
            else:
                return render_template("ManageAccountant.html",msg="Data Not Found")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_accountant',methods=['GET','POST'])
def edit_accountant():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()

            em = request.form['T1']
            sql = "select * from accountant where email='"+em+"'"

            cur.execute(sql)
            n=cur.rowcount
            if n==1:
                data=cur.fetchall()
                return render_template("EditAccountant.html",data=data)
            else:
                return render_template("ManageAccountant.html")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))



@app.route('/edit1_accountant',methods=['GET','POST'])
def edit1_accountant():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                em_id = request.form['T1']
                name = request.form['T2']
                contact = request.form['T3']
                address = request.form['T4']
                em = request.form['T6']

                sql = "UPDATE accountant set emp_id='"+em_id+"', name='"+name+"', contact='"+contact+"',address='"+address+"' where email='"+em+"'"

                cur.execute(sql)
                n1 = cur.rowcount
                if n1==1:
                    return render_template('EditAccountant.html',msg="Saved Successfully")
                else:
                    return render_template('EditAccountant.html',msg="Edit Failed")
            else:
                return render_template('ManageAccountant.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/delete_accountant',methods=['GET','POST'])
def delete_accountant():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,
                                       autocommit=True)
                cur = conn.cursor()

                em = request.form['T1']
                sql = "select * from accountant where email='" + em + "'"

                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    data = cur.fetchall()
                    return render_template("DeleteAccountant.html", data=data)
                else:
                    return render_template("ManageAccountant.html")
            else:
                return render_template("ManageAccountant.html")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/delete1_accountant',methods=['GET','POST'])
def delete1_accountant():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,
                                   autocommit=True)
            cur = conn.cursor()

            em=request.form['T6']
            sql = "delete from accountant where email='"+em+"'"

            cur.execute(sql)
            n = cur.rowcount
            if n==1:
                return render_template('DeleteAccountant.html',msg="Deleted Successfully")
            else:
                return render_template('DeleteAccountant.html',msg="Delete Failed")
        else:
            return render_template('ManageAccountant.html')
    else:
        return redirect(url_for('login'))


@app.route('/accountant_home')
def accountant_home():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="accountant":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()
            cur1 = conn.cursor()
            cur3 = conn.cursor()

            sql = "select * from accountant where email='"+email+"'"
            sql1 = "SELECT photo FROM photos WHERE email=%s"
            sql3 = "select * from students"

            cur3.execute(sql3)
            cur.execute(sql)
            cur1.execute(sql1, (email,))
            row = cur1.fetchone()
            photo = row[0] if row else None
            n=cur.rowcount
            n2=cur3.rowcount
            print(n2)
            if n==1:
                data=cur.fetchall()
                data1=cur3.fetchall()
                return render_template("AccountantHome.html",data=data,data1=data1,photo=photo,n=n)
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


@app.route('/edit_students',methods=['GET','POST'])
def edit_students():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="accountant":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
                cur = conn.cursor()
                reg_no = request.form['T1']
                sql = "select * from students where reg_no='"+reg_no+"'"

                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data=cur.fetchall()
                    return render_template('EditStudents.html',data=data,j="k")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return redirect(url_for('auth_error'))
        elif usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()
                reg_no = request.form['T1']
                sql = "select * from students where reg_no='" + reg_no + "'"

                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    data = cur.fetchall()
                    return render_template('EditStudents.html', data=data,j="l")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/edit1_students',methods=['GET','POST'])
def edit1_students():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="accountant":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()


                reg_no = request.form['T1']
                s_name = request.form['T2']
                f_name = request.form['T3']
                m_name = request.form['T4']
                gender = request.form['T5']
                dob = request.form['T6']
                category = request.form['T7']
                domicile = request.form['T8']
                address = request.form['T9']
                contactno = request.form['T10']
                em = request.form['T11']
                institute = request.form['T12']



                sql = "UPDATE students set em='" + em + "', s_name='" + s_name + "', f_name='" + f_name + "',m_name='" + m_name + "', gender='" + gender + "', dob='" + dob + "', category='" + category + "', domicile='" + domicile + "' , address='" + address + "', contactno='" + contactno + "', institute='" + institute + "' where reg_no='" + reg_no + "'"

                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('EditStudents.html', msg="Saved Successfully", j=k)
                else:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('EditStudents.html', msg="Edit Failed", j=k)
            else:
                return redirect(url_for('autherror'))
        elif usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                reg_no = request.form['T1']
                s_name = request.form['T2']
                f_name = request.form['T3']
                m_name = request.form['T4']
                gender = request.form['T5']
                dob = request.form['T6']
                category = request.form['T7']
                domicile = request.form['T8']
                address = request.form['T9']
                contactno = request.form['T10']
                em = request.form['T11']
                institute = request.form['T12']


                sql = "UPDATE students set em='"+em+"', s_name='"+s_name+"', f_name='"+f_name+"',m_name='"+m_name+"', gender='"+gender+"', dob='"+dob+"', category='"+category+"', domicile='"+domicile+"' , address='"+address+"', contactno='"+contactno+"', institute='"+institute+"' where reg_no='"+reg_no+"'"

                cur.execute(sql)
                n = cur.rowcount
                if n==1:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('EditStudents.html',msg="Saved Successfully",j=k)
                else:
                    if usertype == "admin":
                        k = "k"
                    else:
                        k = "l"
                    return render_template('EditStudents.html',msg="Edit Failed",j=k)
            else:
                return render_template('EditStudents.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/delete_students',methods=['GET','POST'])
def delete_students():
    if 'email' in session:
        usertype=session['usertype']
        email=session['email']
        if usertype=="admin":
            if request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                reg_no = request.form['T1']
                sql = "select * from students where reg_no='" + reg_no + "'"

                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    data = cur.fetchall()
                    return render_template('DeleteStudents.html', data=data)
                else:
                    return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/delete1_students',methods=['POST','GET'])
def delete1_students():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
            cur = conn.cursor()

            reg_no = request.form['T1']
            sql = "DELETE from students where reg_no='"+reg_no+"'"
            cur.execute(sql)
            n=cur.rowcount
            if n==1:
                return render_template('DeleteStudents.html',msg="Delete Successfully")
            else:
                return render_template('DeleteStudents.html',msg="Delete Failed")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/edit_admin_profile',methods=['POST','GET'])
def edit_admin_profile():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'GET':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
                cur = conn.cursor()

                sql = "select * from admin where email='"+email+"'"
                cur.execute(sql)
                n = cur.rowcount
                if n==1:
                    data = cur.fetchall()
                    return render_template('EditAdminProfile.html',data=data)
                else:
                    return redirect(url_for('auth_error'))
            elif request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                name = request.form['T1']
                contact = request.form['T3']
                address = request.form['T5']
                dob = request.form['T6']
                gender = request.form['T7']
                sql = "update admin set name='"+name+"', contact='"+contact+"', address='"+address+"',dob='"+dob+"',gender='"+gender+"' where email='" + email + "'"
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    return render_template('EditAdminProfile.html', msg="Saved Successfully")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return render_template('EditAdminProfile.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/photo')
def photo():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            return render_template('PhotoUpload.html',j="k")
        elif usertype=="accountant":
            return render_template('PhotoUpload.html',j="j")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/student_photo',methods=['POST','GET'])
def student_photo():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="admin":
            if request.method == 'POST':
                reg_no = request.form['T15']
                return render_template('StudentPhotoUpload.html',j="k",reg_no=reg_no)
            else:
                return redirect(url_for('auth_error'))
        elif usertype=="accountant":
            if request.method == 'POST':
                reg_no = request.form['T15']
                return render_template('StudentPhotoUpload.html', j="j", reg_no=reg_no)
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/student_photo1', methods=['GET', 'POST'])
def student_photo1():
    if 'email' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == "admin":
            if request.method == 'POST':
                file = request.files.get('F1')
                if file and file.filename != '':
                    file_ext = os.path.splitext(file.filename)[1][1:]
                    filename = secure_filename(str(int(time.time())) + '.' + file_ext)
                    try:
                        conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                        cur = conn.cursor()
                        reg_no = request.form['T1']
                        print(reg_no)
                        print(file)
                        sql = "INSERT INTO student_photo (reg_no, photo) VALUES (%s, %s)"
                        cur.execute(sql, (reg_no, filename))

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        return render_template('StudentPhotoUpload.html',j="k",msg="Photo Upload Success")

                    except pymysql.err.IntegrityError:
                        return render_template('StudentPhotoUpload.html',msg="Photo Upload ",j="k" )
                    except Exception as e:
                        return render_template('StudentPhotoUpload.html',msg="Photo Upload Failed",j="k")
                    finally:
                        cur.close()
                        conn.close()
                else:
                    return render_template('StudentPhoto.html')
            else:
                return render_template('StudentPhotoUpload.html')
        elif usertype=="accountant":
            if request.method == 'POST':
                file = request.files.get('F1')

                if file and file.filename != '':
                    file_ext = os.path.splitext(file.filename)[1][1:]
                    filename = secure_filename(str(int(time.time())) + '.' + file_ext)

                    try:
                        conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                        cur = conn.cursor()

                        reg_no = request.form['T1']
                        sql = "INSERT INTO student_photo (reg_no, photo) VALUES (%s, %s)"
                        cur.execute(sql, (reg_no, filename))

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        return render_template('StudentPhotoUpload.html',j="j",msg="Photo Upload Success")

                    except pymysql.err.IntegrityError:
                        return render_template('StudentPhotoUpload.html',j="j", msg="Photo Upload Failed")
                    except Exception as e:
                        return render_template('StudentPhotoUpload.html',j="j", msg="Photo Upload Failed")
                    finally:
                        cur.close()
                        conn.close()
                else:
                    return render_template('PhotoUpload.html')
            else:
                return redirect(url_for("auth_error"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for('login'))




@app.route('/student_change_photo1',methods=['POST','GET'])
def student_change_photo1():
    if 'email' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
            if request.method == "POST":
                reg_no = request.form['T15']
                print(reg_no)
                photo = sutudent_check_photo(reg_no)
                print(photo)
                conn = pymysql.connect(host='localhost', user="root", password='', port=3306, db='student', autocommit=True)
                cur = conn.cursor()
                sql = "DELETE FROM student_photo WHERE reg_no=%s"
                cur.execute(sql, (reg_no,))
                n = cur.rowcount
                if n == 1:
                    os.remove("./static/uploads/" + photo)
                    return render_template("StudentPhotoUpload.html",j="k",reg_no=reg_no)
                else:
                    return render_template("StudentPhotoUpload.html",j="k")
            else:
                return render_template("StudentPhotoUpload.html")
        elif usertype == 'accountant':
            reg_no = request.form['T15']
            print(reg_no)
            photo = sutudent_check_photo(reg_no)
            print(photo)
            conn = pymysql.connect(host='localhost', user="root", password='', port=3306, db='student', autocommit=True)
            cur = conn.cursor()
            sql = "DELETE FROM student_photo WHERE reg_no=%s"
            cur.execute(sql, (reg_no,))
            n = cur.rowcount
            if n == 1:
                os.remove("./static/uploads/" + photo)
                return render_template("StudentPhotoUpload.html", j="j", reg_no=reg_no)
            else:
                return render_template("StudentPhotoUpload.html", j="j")
        else:
            return redirect(url_for("autherror"))
    else:
        return redirect(url_for("autherror"))


@app.route('/photo1', methods=['GET', 'POST'])
def photo1():
    if 'email' in session:
        usertype = session['usertype']
        email = session['email']

        if usertype == "admin":
            if request.method == 'POST':
                file = request.files.get('F1')

                if file and file.filename != '':
                    file_ext = os.path.splitext(file.filename)[1][1:]
                    filename = secure_filename(str(int(time.time())) + '.' + file_ext)

                    try:
                        conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                        cur = conn.cursor()

                        sql = "INSERT INTO photos (email, photo) VALUES (%s, %s)"
                        cur.execute(sql, (email, filename))

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        return redirect(url_for('admin_home'))

                    except pymysql.err.IntegrityError:
                        return render_template('PhotoUpload.html', )
                    except Exception as e:
                        return render_template('PhotoUpload.html')
                    finally:
                        cur.close()
                        conn.close()
                else:
                    return render_template('PhotoUpload.html')
            else:
                return render_template('PhotoUpload.html')
        elif usertype=="accountant":
            if request.method == 'POST':
                file = request.files.get('F1')

                if file and file.filename != '':
                    file_ext = os.path.splitext(file.filename)[1][1:]
                    filename = secure_filename(str(int(time.time())) + '.' + file_ext)

                    try:
                        conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                        cur = conn.cursor()

                        sql = "INSERT INTO photos (email, photo) VALUES (%s, %s)"
                        cur.execute(sql, (email, filename))

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        return redirect(url_for('accountant_home'))

                    except pymysql.err.IntegrityError:
                        return render_template('PhotoUpload.html', )
                    except Exception as e:
                         return render_template('PhotoUpload.html')
                    finally:
                        cur.close()
                        conn.close()
                else:
                    return render_template('PhotoUpload.html')
            else:
                return redirect(url_for("auth_error"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for('login'))

@app.route('/change_photo')
def change_photo():
    if 'email' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
                photo = check_photo(email)
                conn = pymysql.connect(host='localhost', user="root", password='', port=3306, db='student', autocommit=True)
                cur = conn.cursor()
                sql = "DELETE FROM photos WHERE email=%s"
                cur.execute(sql, (email,))
                n = cur.rowcount
                if n == 1:
                    os.remove("./static/uploads/" + photo)
                    return render_template("PhotoUpload.html",j="k")
                else:
                    return render_template("PhotoUpload.html")
        elif usertype == 'accountant':
                photo = check_photo(email)
                conn = pymysql.connect(host='localhost', user="root", password='', port=3306, db='student',
                                       autocommit=True)
                cur = conn.cursor()
                sql = "DELETE FROM photos WHERE email=%s"
                cur.execute(sql, (email,))
                n = cur.rowcount
                if n == 1:
                    os.remove("./static/uploads/" + photo)
                    return render_template("PhotoUpload.html",j="j")
                else:
                    return render_template("PhotoUpload.html")
        else:
            return redirect(url_for("autherror"))
    else:
        return redirect(url_for("autherror"))


@app.route('/edit_accountant_profile',methods=['POST','GET'])
def edit_accountant_profile():
    if 'email' in session:
        email=session['email']
        usertype=session['usertype']
        if usertype=="accountant":
            if request.method == 'GET':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306, autocommit=True)
                cur = conn.cursor()

                sql = "select * from accountant where email='"+email+"'"
                cur.execute(sql)
                n = cur.rowcount
                if n==1:
                    data = cur.fetchall()
                    return render_template('EditAccountantProfile.html',data=data)
                else:
                    return redirect(url_for('auth_error'))
            elif request.method == 'POST':
                conn = pymysql.connect(host='localhost', user="root", db='student', passwd='', port=3306,autocommit=True)
                cur = conn.cursor()

                em_id = request.form['T1']
                name = request.form['T2']
                contact = request.form['T3']
                address = request.form['T4']
                gender = request.form['T5']

                sql = "update accountant set emp_id='"+em_id+"', name='"+name+"', contact='"+contact+"', address='"+address+"',gender='"+gender+"' where email='" + email + "'"
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    return render_template('EditAccountantProfile.html', msg="Saved Successfully")
                else:
                    return render_template('EditAccountantProfile.html',msg="Edit Failed")
            else:
                return render_template('EditAccountantProfile.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/student_dash',methods=['POST','GET'])
def student_dash():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        reg_no = session['email']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost',user="root",db="student",port=3306,password='',autocommit=True)
                cur = conn.cursor()
                reg_no = request.form['T1']
                sql = "select * from students where reg_no='"+reg_no+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data = cur.fetchall()
                    cur1 = conn.cursor()
                    s2 = "select * from course where reg_no='"+reg_no+"'"
                    cur1.execute(s2)
                    n1=cur1.rowcount
                    photo = sutudent_check_photo(reg_no)
                    if n1>0:
                        data1=cur1.fetchall()
                        courses=[]
                        for d in data1:
                            paid = course_paid(d[0],d[4])
                            due=d[2]-paid
                            aa=[d[0],d[1],d[2],d[3],d[4],paid,due]
                            courses.append(aa)
                        cur5 = conn.cursor()
                        sql5 = "select * from fees where reg_no='"+reg_no+"'"
                        cur5.execute(sql5)
                        data5 = cur5.fetchall()
                        total_fee = 0
                        for d in data1:
                            total_fee = total_fee + d[2]
                        print(total_fee)
                        total_deposit = 0
                        for i in data5:
                            total_deposit = total_deposit + i[4]
                        print(total_deposit)
                        total_due =  total_fee - total_deposit
                        print(total_due)
                        photo=sutudent_check_photo(reg_no)
                        return render_template('StudentDashboard.html',total_fee=total_fee,total_deposit=total_deposit,total_due=total_due,data=data,data1=courses,data5=data5,j="k",photo=photo)
                    else:
                        return render_template('StudentDashboard.html',data=data,j="k",photo=photo)
                else:
                    return redirect(url_for("auth_error"))
            else:
                return render_template("AdminHome.html")
        elif usertype == "accountant":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost',user="root",db="student",port=3306,password='',autocommit=True)
                cur = conn.cursor()
                reg_no = request.form['T1']
                sql = "select * from students where reg_no='"+reg_no+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data = cur.fetchall()
                    cur1 = conn.cursor()
                    s2 = "select * from course where reg_no='"+reg_no+"'"
                    s2 = "select * from course where reg_no='"+reg_no+"'"
                    cur1.execute(s2)
                    n1=cur1.rowcount
                    photo = sutudent_check_photo(reg_no)
                    if n1 > 0:
                        data1 = cur1.fetchall()
                        courses = []
                        for d in data1:
                            paid = course_paid(d[0], d[4])
                            due = d[2] - paid
                            aa = [d[0], d[1], d[2], d[3], d[4], paid, due]
                            courses.append(aa)
                        cur5 = conn.cursor()
                        sql5 = "select * from fees where reg_no='" + reg_no + "'"
                        cur5.execute(sql5)
                        data5 = cur5.fetchall()
                        total_fee = 0
                        for d in data1:
                            total_fee = total_fee + d[2]
                        print(total_fee)
                        total_deposit = 0
                        for i in data5:
                            total_deposit = total_deposit + i[4]
                        print(total_deposit)
                        total_due = total_fee - total_deposit
                        print(total_due)
                        photo = sutudent_check_photo(reg_no)
                        return render_template('StudentDashboard.html', total_fee=total_fee,total_deposit=total_deposit,total_due=total_due,data=data, data1=courses, data5=data5, j="j",photo=photo)
                    else:
                        return render_template('StudentDashboard.html', data=data, j="j", photo=photo)
                else:
                    return redirect(url_for("auth_error"))
            else:
                return render_template("AccountantHome.html")
        elif usertype=="student":
                conn = pymysql.connect(host='localhost',user="root",db="student",port=3306,password='',autocommit=True)
                cur = conn.cursor()
                sql = "select * from students where reg_no='"+reg_no+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data = cur.fetchall()
                    cur1 = conn.cursor()
                    s2 = "select * from course where reg_no='"+reg_no+"'"
                    s2 = "select * from course where reg_no='"+reg_no+"'"
                    cur1.execute(s2)
                    n1=cur1.rowcount
                    photo = sutudent_check_photo(reg_no)
                    if n1 > 0:
                        data1 = cur1.fetchall()
                        courses = []
                        for d in data1:
                            paid = course_paid(d[0], d[4])
                            due = d[2] - paid
                            aa = [d[0], d[1], d[2], d[3], d[4], paid, due]
                            courses.append(aa)
                        cur5 = conn.cursor()
                        sql5 = "select * from fees where reg_no='" + reg_no + "'"
                        cur5.execute(sql5)
                        data5 = cur5.fetchall()
                        total_fee=0
                        for d in data1:
                            total_fee=total_fee+d[2]
                        print(total_fee)
                        total_deposit=0
                        for i in data5:
                            total_deposit=total_deposit+i[4]
                        print(total_deposit)
                        total_due = total_fee - total_deposit
                        print(total_due)
                        photo = sutudent_check_photo(reg_no)
                        return render_template('StudentDashboard.html', total_fee=total_fee,total_deposit=total_deposit,total_due=total_due,data=data, data1=courses, data5=data5, j="u",photo=photo,reg_no=reg_no)
                    else:
                        return render_template('StudentDashboard.html', data=data, j="u",reg_no=reg_no, photo=photo)
                else:
                    return redirect(url_for("auth_error"))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))



@app.route('/students_reg', methods=['GET','POST'])
def students_reg():
    if 'email' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == "accountant":
            if request.method == 'GET':
                return render_template('StudentsReg.html')
            elif request.method == 'POST':
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()
                cur2 = conn.cursor()
                reg_no = request.form['T1']
                s_name = request.form['T2']
                f_name = request.form['T3']
                m_name = request.form['T4']
                gender = request.form['T5']
                dob = request.form['T6']
                category = request.form['T7']
                domicile = request.form['T8']
                address = request.form['T9']
                contactno = request.form['T10']
                em = request.form['T11']
                institute = request.form['T12']
                password = request.form['T13']
                ut = "student"
                sql = "insert into students values('"+reg_no+"','"+s_name+"','"+f_name+"','"+m_name+"','"+gender+"','"+dob+"','"+category+"','"+domicile+"','"+address+"','"+contactno+"','"+em+"','"+institute+"')"
                sql2 = "INSERT INTO login VALUES('" + reg_no + "','" + password + "','" + ut + "')"
                cur.execute(sql)

                cur2.execute(sql2)
                n2=cur2.rowcount

                n=cur.rowcount
                if n==1 and n2==1:
                    return render_template('StudentsReg.html',msg="Student Register Successfully")
                else:
                    return render_template('StudentsReg.html',msg="Student Register Failed")
            else:
                return render_template('StudentsReg.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


@app.route('/add_course',methods=['POST','GET'])
def add_course():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                reg_no=request.form['T1']
                return render_template("Addcourse.html",reg_no=reg_no,j="k")
            else:
                return render_template("StudentDashboard.html")
        elif usertype=="accountant":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                reg_no=request.form['T1']
                return render_template("Addcourse.html",reg_no=reg_no,j="j")
            else:
                return render_template("StudentDashboard.html")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/add_course1',methods=['POST','GET'])
def add_course1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                student_course_id=0
                reg_no = request.form['reg_no']
                course_name = request.form['corse_name']
                fee = request.form['fee']
                start_date  = request.form['start_date']

                sql = "insert into course values('"+str(student_course_id)+"','"+course_name+"','"+fee+"','"+start_date+"','"+reg_no+"')"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    return render_template('Addcourse.html',msg="Course Register Successfull ",j="k")
                else:
                    return render_template('Addcourse.html',msg="Course Register Failed",j="k")
            else:
                return redirect(url_for('auth_error'))
        elif usertype == "accountant":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                student_course_id = 0
                reg_no = request.form['reg_no']
                course_name = request.form['corse_name']
                fee = request.form['fee']
                start_date = request.form['start_date']

                sql = "insert into course values('" + str(student_course_id) + "','" + course_name + "','" + fee + "','" + start_date + "','" + reg_no + "')"
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    return render_template('Addcourse.html', msg="Course Register Succeq",j="j")
                else:
                    return render_template('Addcourse.html', msg="Course Register Failed",j="j")
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


@app.route('/deposit_amt',methods=['POST','GET'])
def deposit_amt():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()

            course_id = request.form['T1']
            sql = "select * from course where st_course_id='"+course_id+"'"
            cur.execute(sql)
            data=cur.fetchone()
            reg_no=data[4]
            course_name=data[1]
            return render_template("DepositAmt.html",course_id=course_id,reg_no=reg_no,course_name=course_name,d="d",j="k")
        if usertype=="accountant":
            conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()

            course_id = request.form['T1']
            sql = "select * from course where st_course_id='"+course_id+"'"
            cur.execute(sql)
            data=cur.fetchone()
            reg_no=data[4]
            course_name=data[1]
            return render_template("DepositAmt.html",course_id=course_id,reg_no=reg_no,course_name=course_name,d="d",j="j")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/deposit_amt1',methods=['POST','GET'])
def deposit_amt1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()
            t_no = 0
            course_id = request.form['T1']
            reg_no = request.form['T2']
            course_name =  request.form['T3']
            amount = request.form['T4']
            deposit_date = request.form['T5']
            remark = request.form['T6']

            sql = "insert into fees values('"+str(t_no)+"','"+str(course_id)+"','"+str(reg_no)+"','"+course_name+"','"+str(amount)+"','"+deposit_date+"','"+remark+"')"
            cur.execute(sql)
            n=cur.rowcount
            if n==1:
                return render_template("DepositAmt.html",msg="Deposit Amount Successfully",j="k")
            else:
                return render_template('DepositAmt.html',msg="Deposit Amount Failed",j="k")
        elif usertype=="accountant":
            conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()
            t_no = 0
            course_id = request.form['T1']
            reg_no = request.form['T2']
            course_name = request.form['T3']
            amount = request.form['T4']
            deposit_date = request.form['T5']
            remark = request.form['T6']

            sql = "insert into fees values('" + str(t_no) + "','" + str(course_id) + "','" + str(reg_no) + "','" + course_name + "','" + str(amount) + "','" + deposit_date + "','" + remark + "')"
            cur.execute(sql)
            n = cur.rowcount
            if n == 1:
                return render_template("DepositAmt.html", msg="Deposit Amount Successfully",j="j")
            else:
                return render_template('DepositAmt.html', msg="Deposit Amount Failed",j="j")
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_course',methods=['POST','GET'])
def edit_course():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            conn =  pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()

            course_id = request.form['T1']
            sql = "select * from course where st_course_id='"+course_id+"'"
            cur.execute(sql)
            n=cur.rowcount
            if n==1:
                data=cur.fetchall()
                return render_template('EditCourse.html',data=data)
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_course1',methods=['POST','GET'])
def edit_course1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                st_course_id = request.form['T1']
                reg_no = request.form['reg_no']
                course_name = request.form['corse_name']
                fee = request.form['fee']
                start_date = request.form['start_date']

                sql = "update course set course_name='"+course_name+"',fee='"+fee+"',start_date='"+start_date+"' where st_course_id='"+st_course_id+"'"

                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    return render_template('EditCourse.html',msg="Edit Successfully")
                else:
                    return render_template('EditCourse.html',msg="Edit Failed")
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_course',methods=['POST','GET'])
def delete_course():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            conn =  pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
            cur = conn.cursor()

            course_id = request.form['T1']
            sql = "select * from course where st_course_id='"+course_id+"'"
            cur.execute(sql)
            n=cur.rowcount
            if n==1:
                data=cur.fetchall()
                return render_template('DeleteCourse.html',data=data)
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_course1',methods=['POST','GET'])
def delete_course1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                st_course_id = request.form['T1']
                sql = "delete from course where st_course_id='"+st_course_id+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    return render_template('DeleteCourse.html',msg="Delete Course Successfully")
                else:
                    return render_template('DeleteCourse.html',msg="Delete Course Failed")
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_transaction',methods=['POST','GET'])
def edit_transaction():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype == "admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                t_id = request.form['T1']
                sql = "select * from fees where t_no='"+t_id+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data=cur.fetchall()
                    return render_template('EditTransaction.html',data=data,d="d")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))
@app.route('/edit_transaction1',methods=['POST','GET'])
def edit_transaction1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                t_no = request.form['T1']
                course_id = request.form['T2']
                reg_no = request.form['T3']
                course_name = request.form['T4']
                amount = request.form['T5']
                deposit_date = request.form['T6']
                remark = request.form['T7']

                sql = "update fees set course_id='"+course_id+"', course_name='"+course_name+"',amount='"+amount+"',deposit_date='"+deposit_date+"',remark='"+remark+"' where t_no='"+t_no+"'"
                cur.execute(sql)
                n= cur.rowcount
                if n==1:
                    return render_template('EditTransaction.html',msg="Edit Successfully")
                else:
                    return render_template('EditTransaction.html',msg="Edit Failed")
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_transaction',methods=['POST','GET'])
def delete_transaction():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype == "admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                t_id = request.form['T1']
                sql = "select * from fees where t_no='"+t_id+"'"
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    data=cur.fetchall()
                    return render_template('DeleteTransaction.html',data=data,d="d")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_transaction1',methods=['POST','GET'])
def delete_transaction1():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="admin":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()

                t_no = request.form['T1']

                sql = "delete from fees where t_no='"+t_no+"'"
                cur.execute(sql)
                n= cur.rowcount
                if n==1:
                    return render_template('EditTransaction.html',msg="Delete Successfully")
                else:
                    return render_template('EditTransaction.html',msg="Delete Failed")
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


@app.route('/receipt',methods=['POST','GET'])
def receipt():
    if 'email' in session:
        email = session['email']
        usertype = session['usertype']
        if usertype=="accountant":
            if request.method == "POST":
                conn = pymysql.connect(host='localhost', user='root', passwd='', db='student', autocommit=True)
                cur = conn.cursor()
                cur1 = conn.cursor()
                cur2 = conn.cursor()

                t_no = request.form['T1']

                sql = "select * from fees where t_no='"+t_no+"'"
                cur.execute(sql)
                n=cur.rowcount
                data1 = cur.fetchone()
                reg_no = str(data1[1])
                print(reg_no)
                sql1 = "select * from students where reg_no='" + reg_no + "'"
                cur1.execute(sql1)
                data2 = cur1.fetchall()
                print(data2)
                print(n)
                if n==1:
                    print(data1)
                    return render_template('Receipt.html',data=data1,data2=data2,j="j")
                else:
                    return redirect(url_for('auth_error'))
            else:
                return redirect(url_for('auth_error'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('login'))


if __name__=='__main__':
    app.run(debug=True)


