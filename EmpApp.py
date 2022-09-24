from operator import iadd
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

@app.route("/getdata", methods=['GET'])
def getData():
    emp_id = request.form['emp_id']

    #get user data
    search_sql = "Select * from employee where emp_id LIKE %(emp_id)s"
    
    cursor = db_conn.cursor()

    if emp_id == "":
        return "Please enter a valid employee ID:"

    try:
        #get user data
        cursor.execute(search_sql, (emp_id))
        row = cursor.fetchone()
        v_empID = row[0]
        v_fname = row[1]
        v_lname = row[2]
        v_PriSkill = row [3]
        v_location = row [4]

        # db_conn.commit()
        # emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        #s3 = boto3.resource('s3')

        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.png"

        # Get image url
        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, emp_image_file_name_in_s3)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('emp_det_out.html', id = v_empID, fname = v_fname, lname = v_lname, pri_skill = v_PriSkill, location = v_location, image_url = url)

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

@app.route("/delData", methods=['GET'])
def delEmp():
    emp_id = request.form['emp_id']

    #get user data
    search_sql = "Select * from employee where emp_id LIKE %(emp_id)s"
    
    delete_sql = "Delete from employee where emp_id LIKE %(emp_id)s"

    cursor = db_conn.cursor()
    cursor1 = db_conn.cursor()

    if emp_id == "":
        return "Please enter a valid employee ID:"

    try:
        #get user data
        cursor.execute(search_sql, (emp_id))
        cursor1.execute(delete_sql, (emp_id))
        row = cursor.fetchone()

        for result in cursor:
            print(result)
            db_conn.commit()


        # db_conn.commit()
        # emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        #s3 = boto3.resource('s3')

        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.png"

        # Get image url
        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, emp_image_file_name_in_s3)

    except Exception as e:
        db_conn.commit()
        return str(e)

    finally:
        cursor.close()
        cursor1.close()

    print("all modification done...")
    return render_template('fire_emp_out.html', emp_id = emp_id)

