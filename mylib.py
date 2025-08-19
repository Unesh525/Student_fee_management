import pymysql


def check_photo(email):
    conn  = pymysql.connect(host="localhost",user="root",port=3306,passwd='',db="student",autocommit=True)
    cur = conn.cursor()
    sql = "SELECT * FROM photos WHERE email = '"+email+"'"
    cur.execute(sql)
    n = cur.rowcount
    photo = "no"
    if n==1:
        row=cur.fetchone()
        photo=row[1]
    return photo

def sutudent_check_photo(reg_no):
    conn = pymysql.connect(host="localhost",user="root",port=3306,passwd='',db="student",autocommit=True)
    cur = conn.cursor()
    sql = "select * from student_photo where reg_no = '"+reg_no+"'"
    cur.execute(sql)
    n = cur.rowcount
    photo="no"
    if n==1:
        row=cur.fetchone()
        photo=row[1]
        print(photo)
    return photo



def course_paid(course_id,reg_no):
    p=0
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd='', db="student", autocommit=True)
    cur = conn.cursor()

    sql = "select * from fees where reg_no='"+str(reg_no)+"' and course_id='"+str(course_id)+"'"

    cur.execute(sql)
    n=cur.rowcount
    if n>0:
        data = cur.fetchall()
        for d in data:
            p=p+d[4]

    return p