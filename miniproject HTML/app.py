from flask import Flask, request, render_template,jsonify,session,redirect,url_for, flash
import re
from datetime import datetime


# Get the current date and time
now = datetime.now()

# Print the current date and time
print("Current date and time:", now)

import bcrypt

import mysql.connector

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abhi0008",
    database="tadabill2"
)

conn = mydb.cursor()

app = Flask(__name__)

app.secret_key = 'just_for_fun_and_testing_123'


# Regular expression to match a valid Indian mobile number
indian_mobile_regex = re.compile(r'^[789]\d{9}$')

# Regular expression to match a valid PAN number
pan_regex = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')



@app.route('/', methods=['GET'])
def login():
    return render_template('login-page.html')


@app.route('/checkUser', methods=['POST'])
def login1():
    data = request.json
    #print(data)
    username = data.get('username')
    password = data.get('password')

    conn.execute('SELECT * FROM login_page WHERE user_name = %s and password = %s', (username, password))
    user = conn.fetchone()
    #print(user)

    if user:
        session['user_name'] = user[1]  # Assuming the first column is the user_name
        session['password'] = user[2]  # Store additional details if needed

        return jsonify({'success': True, 'message': 'Login successful!'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect username or password!'})


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup1():
    data = request.json
    password = data.get('password')
    username = data.get('user_name')
    department = data.get('department_name')

    conn.execute('SELECT * FROM login_page WHERE department_name = %s and user_name=%s and password=%s',
                 (department, username, password))
    user_check = conn.fetchone()
    if user_check:
        return jsonify({'success': False, 'message': 'Username already exists!'})

    conn.execute(
        'INSERT INTO login_page (department_name,user_name, password)'
        ' VALUES (%s, %s, %s)',
        (department, username, password)
    )

    mydb.commit()
    return jsonify({'success': True, 'message': 'Signup successful!'})


@app.route('/personalDetails', methods=['POST'])
def person():
    if request.method == 'POST':
        name = request.form['name']
        pan_no = request.form['pan_no']
        phone_no = request.form['phone_no']
        designation = request.form['designation']
        college_name = request.form['college_name']
        acc_no = request.form['acc_no']
        ifsc = request.form['ifsc']
        address=request.form['address']
        bank_name=request.form['bank_name']

        if not pan_regex.match(pan_no):
            print("Hi")
            flash('Invalid PAN number format. It should be in the format: ABCDE1234F')
            return redirect(url_for('personal_details'))

            # Validate mobile number
        if not indian_mobile_regex.match(phone_no):
            print("Hello")
            flash('Invalid mobile number format. It should start with 7, 8, or 9 and be 10 digits long.', 'danger')
            return render_template('personalDetails.html')

        sql = """INSERT INTO personnel_info
        (pan_no, name, college_name, designation, mobile_no, account_no, ifsc_code,address,bank_name) 
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)"""
        values = (pan_no, name, college_name, designation, phone_no, acc_no, ifsc,address,bank_name)


        conn.execute(sql, values)
        mydb.commit()





    return render_template('personalDetails.html')


@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))


@app.route('/personalDetails')
def personal_details():
    return render_template('personalDetails.html')


@app.route('/tada', methods=['GET'])
def tada():
    # Render the TADA page for GET requests
    conn.execute("SELECT pan_no FROM personnel_info")  # Query to get the pan values
    pan_values = [row[0] for row in conn.fetchall()]  # Extract the pan values
    return render_template('tada.html',pan_values=pan_values)

@app.route('/tada', methods=['POST'])
def tada_post():
    # Retrieve the PAN number from the form
    pan_no = request.form.get('pan_no')
    if not pan_no:
        return redirect('/personalDetails')  # Redirect to the personal details page if PAN number is not found

    # Handle TADA form submission: insert data into the travel_details table
    departure = request.form.get('departure')
    departure_date = request.form.get('departure_date') or None
    departure_time = request.form.get('departure_time') or None
    arrival = request.form.get('arrival')
    arr_date = request.form.get('arr_date') or None
    arr_time = request.form.get('arr_time') or None
    mode = request.form.get('mode')
    fare_amount = request.form.get('fare_amount') or None
    travel_con = request.form.get('travel_con')
    local_con = request.form.get('local_con')
    types = request.form.get('types') or None
    no_of_fares = request.form.get('no_of_fares')

    # Debug: Print the request form to see what data is being received
    print(request.form)

    if departure_date and arr_date:
        departure_dt = datetime.strptime(departure_date, '%Y-%m-%d')
        arrival_dt = datetime.strptime(arr_date, '%Y-%m-%d')

        # Check if the arrival date is before the departure date
        if arrival_dt < departure_dt:
            flash('Error: Arrival date cannot be before departure date!', 'danger')
            return redirect(url_for('personal_details'))

    # Insert into the database
    sql = """INSERT INTO travel_details
        (pan_no, departure, departure_date, departure_time, arrival, arrival_date, arrival_time, mode_of_journey,
        fare_amount, travel_convenience, local_convenience, class, no_of_fares)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (
        pan_no, departure, departure_date, departure_time, arrival, arr_date, arr_time, mode, fare_amount, travel_con,
        local_con, types, no_of_fares
    )

    try:
        conn.execute(sql, values)
        mydb.commit()
        message = "Details saved successfully!"
    except mysql.connector.Error as err:
        print("Error: ", err)
        mydb.rollback()
        message = "There was an error saving your details. Please try again."

    # Render the same page with a success or error message
    return render_template('tada.html', pan_no=pan_no)

@app.route('/print_paper_evaluation',methods=['GET'])
def print_paper_evaluation():
    no_of_batches = request.args.get('no_of_batches')
    semester=request.args.get('semester')
    pan_no=request.args.get('pan_no')
    date=request.args.get('date')
    subject=request.args.get('subject')
    subject_code = request.args.get('subject_code')
    conn.execute("SELECT amount FROM remuneration WHERE work_done='paper_evaluation' ")  # Query to get the pan values
    amount = conn.fetchone()[0]
    amount = int(amount)
    total=amount
    total *= int(no_of_batches)
    query = "SELECT * from personnel_info where pan_no= %s"

    conn.execute(query, (pan_no,))

    personnel_row = conn.fetchone()

    name = personnel_row[1]  # First column (name)
    designation = personnel_row[3]  # Second column (designation)
    college_name = personnel_row[2]  # Third column (email)
    account_no = personnel_row[5]
    bank_name = personnel_row[8]
    ifsc_code = personnel_row[6]
    address = personnel_row[7]

    # Extract the pan values


    return render_template('print_paper_evaluation.html',amount=amount,subject_code=subject_code,total=total,
                           pan_no=pan_no,
                           date=date,name=name,designation=designation,college_name=college_name,
                           semester=semester,bank_name=bank_name,ifsc_code=ifsc_code, account_no=account_no,no_of_batches=no_of_batches,subject=subject,address=address)


@app.route('/paperEvaluation', methods=['GET'])
def paper_eval():
    # Render the paper evaluation page for GET requests
    conn.execute("SELECT pan_no FROM personnel_info")  # Query to get the pan values
    pan_values = [row[0] for row in conn.fetchall()]  # Extract the pan values
    return render_template('paperEvaluation.html',pan_values=pan_values)


@app.route('/paperEvaluation', methods=['POST'])
def paper_eval_post():
    # Handle paper evaluation form submission: insert data into the see_paper table
    pan_no = request.form['pan_no']
    subject = request.form['subject']
    subject_code = request.form['subject_code']
    date=request.form['date']
    date = None if date == '' else date

    no_of_batches = request.form['no_of_packets']
    no_of_batches = None if no_of_batches == '' else no_of_batches
    semester=request.form['semester']

    try:
        sql = """INSERT INTO see_paper
            (see_pan_no, no_of_packets, subject_code, date, semester)
            VALUES (%s, %s, %s, %s, %s)"""
        values = (pan_no, no_of_batches, subject_code, date, semester)

        conn.execute(sql, values)
        mydb.commit()
    except Exception as e:
        print(f"Error inserting into see_paper: {e}")
        return "An error occurred", 500

    # Render the paper evaluation page after submission
    return redirect(url_for('print_paper_evaluation', no_of_batches=no_of_batches,pan_no=pan_no,date=date,subject=subject,
                            semester=semester,subject_code=subject_code))


@app.route('/paperSetting', methods=['GET'])
def paper_setting_get():
    # Render the paper setting page for GET requests
    conn.execute("SELECT pan_no FROM personnel_info")  # Query to get the pan values
    pan_values = [row[0] for row in conn.fetchall()]  # Extract the pan values
    return render_template('paperSetting.html',pan_values=pan_values)


@app.route('/print_paper_setting',methods=['GET'])
def print_paper_setting():
    subject=request.args.get('subject')
    sub_code = request.args.get('sub_code')
    setter_pan_no=request.args.get('setter_pan_no')
    date=request.args.get('date')
    semester=request.args.get('semester')
    no_of_packets=request.args.get('no_of_packets')
    conn.execute("SELECT amount FROM remuneration WHERE work_done='paper_setting' ")  # Query to get the pan values
    amount = conn.fetchone()[0] # Extract the pan values

    query = "SELECT * from personnel_info where pan_no= %s"

    conn.execute(query,(setter_pan_no,))

    personnel_row = conn.fetchone()

    # Access specific columns from the row
    name = personnel_row[1]  # First column (name)
    designation = personnel_row[3]  # Second column (designation)
    college_name = personnel_row[2]  # Third column (email)
    account_no=personnel_row[5]
    bank_name=personnel_row[8]
    ifsc_code=personnel_row[6]
    address=personnel_row[7]

    total=1
    total=int(amount)*int(no_of_packets)


    return render_template('print_paper_setting.html',amount=amount,sub_code=sub_code,setter_pan_no=setter_pan_no,
                           date=date,name=name,designation=designation,college_name=college_name,
                           semester=semester,bank_name=bank_name,ifsc_code=ifsc_code, account_no=account_no,no_of_packets=no_of_packets,
                           total=total,subject=subject,address=address)



@app.route('/paperSetting', methods=['POST'])
def paper_setting_post():
    # Handle paper setting form submission: insert data into the paper_setting table
    setter_pan_no = request.form['pan_no']
    sub_code = request.form['subject_code']
    exam_duration = request.form['duration']
    exam_duration = None if exam_duration == '' else exam_duration
    date = request.form['date']
    semester=request.form['semester']
    subject=request.form['subject']
    no_of_packets=request.form['no_of_packets']

    if not setter_pan_no or not sub_code or not exam_duration or not date:
        flash("All fields are required. Please fill in all fields.", "error")
        return redirect(url_for('paper_setting_get'))  # Redirect back to the form with a message

        # If all fields are filled, proceed with database insertion
    exam_duration = None if exam_duration == '' else exam_duration

    sql = """INSERT INTO paper_setting
        (setter_pan_no, sub_code, exam_duration,date,semester,subject)
        VALUES (%s, %s, %s,%s,%s,%s)"""
    values = (setter_pan_no, sub_code, exam_duration,date,semester,subject)



    conn.execute(sql, values)
    mydb.commit()



    # Render the paper setting page after submission
    return redirect(url_for('print_paper_setting', sub_code=sub_code,setter_pan_no=setter_pan_no,date=date,semester=semester,
                            subject=subject,no_of_packets=no_of_packets))


@app.route('/print_practical_exam',methods=['GET'])
def print_practical_exam():
    subject = request.args.get('subject')
    sub_code = request.args.get('subject_code')
    no_of_batches = request.args.get('no_of_batches')
    extra_students=request.args.get('extra_students')
    semester=request.args.get('semester')

    examiner_pan_no=request.args.get('examiner_pan_no')
    date=request.args.get('date')
    conn.execute("SELECT amount FROM remuneration WHERE work_done='practical_exam' ")  # Query to get the pan values
    amount = conn.fetchone()[0] # Extract the pan values
    conn.execute("SELECT per_extra FROM remuneration WHERE work_done='practical_exam'")
    per_extra=conn.fetchone()[0]
    query = "SELECT * from personnel_info where pan_no= %s"

    conn.execute(query, (examiner_pan_no,))

    personnel_row = conn.fetchone()

    # Access specific columns from the row
    name = personnel_row[1]  # First column (name)
    designation = personnel_row[3]  # Second column (designation)
    college_name = personnel_row[2]  # Third column (email)
    account_no = personnel_row[5]
    bank_name = personnel_row[8]
    ifsc_code = personnel_row[6]
    address = personnel_row[7]
    amount=int(amount)
    total=amount*int(no_of_batches) +int(extra_students)*int(per_extra)

    return render_template('print_practical_exam.html',amount=amount,no_of_batches=no_of_batches,extra_students=extra_students,
                           examiner_pan_no=examiner_pan_no,date=date,semester=semester,name=name,designation=designation,college_name=college_name,
                           account_no=account_no,bank_name=bank_name,ifsc_code=ifsc_code,address=address,per_extra=per_extra,total=total,subject=subject,
                           sub_code=sub_code)


@app.route('/practicalExaminations', methods=['GET'])
def lab_exam_get():
    conn.execute("SELECT pan_no FROM personnel_info")  # Query to get the pan values
    pan_values = [row[0] for row in conn.fetchall()]  # Extract the pan values
    return render_template('practicalExaminations.html',pan_values=pan_values)


@app.route('/practicalExaminations', methods=['POST'])
def lab_examination_post():
    # Handle practical examinations form submission: insert data into the lab_examination table
    examiner_pan_no = request.form['pan_no']
    no_of_batches = request.form['no_of_batches']
    extra_students = request.form['extra_students']
    extra_students = None if extra_students == '' else extra_students
    subject_code = request.form['subject_code']
    subject=request.form['subject']
    date=request.form['date']
    semester=request.form['semester']

    if not examiner_pan_no or not subject_code or not no_of_batches or not date or not extra_students:
        flash("All fields are required. Please fill in all fields.", "error")
        return redirect(url_for('print_practical_exam'))  # Redirect back to the form with a message

        # If all fields are filled, proceed with database insertion


    sql = """INSERT INTO lab_examination
        (examiner_pan_no, no_of_batches, extra_students, subject_code,date,semester,subject)
        VALUES (%s, %s, %s, %s,%s,%s,%s)"""
    values = (examiner_pan_no, no_of_batches, extra_students, subject_code,date,semester,subject)

    conn.execute(sql, values)
    mydb.commit()

    # Render the practical examinations page after submission
    return redirect(url_for('print_practical_exam', no_of_batches=no_of_batches, extra_students=extra_students,examiner_pan_no=examiner_pan_no,date=date,semester=semester,subject_code=subject_code,
                            subject=subject))


@app.route('/home', methods=['GET'])
def home1():
    conn.execute("SELECT pan_no FROM personnel_info")  # Query to get the pan values
    pan_values = [row[0] for row in conn.fetchall()]  # Extract the pan values
    return render_template('home.html',pan_values=pan_values)


@app.route('/print', methods=['GET'])
def get_data():

    conn1 = mydb.cursor(dictionary=True)
    conn1.execute("SELECT departure, arrival, departure_time, arrival_time, arrival_date, departure_date, "
                  "mode_of_journey, class, no_of_fares, fare_amount, travel_convenience, local_convenience "
                  "FROM travel_details "
                  "GROUP BY departure, arrival, departure_time, arrival_time, arrival_date, departure_date, "
                  "mode_of_journey, class, no_of_fares, fare_amount, travel_convenience, local_convenience")
    result = conn1.fetchall()

    gap_days = []

    for i in range(len(result) - 1):
        current_arrival = result[i]['arrival_date']
        next_departure = result[i + 1]['departure_date']

        if current_arrival and next_departure:
            difference = (next_departure - current_arrival).days
            gap_days.append(int(difference+1))
            print(f"Gap between entry {i} arrival and entry {i + 1} departure: {difference} days")
        else:
            print(f"Missing date in entry {i} or entry {i + 1}")

    print(gap_days)

    da = []
    even_days = []
    odd_days = []
    for j in range(len(gap_days)):
        if j % 2 == 0:
            even_days.append(gap_days[j])
            da.append(gap_days[j] * 100)
        else:
            odd_days.append(gap_days[j])
    odd_days.append(0)

    for z in range(len(odd_days)):

        if odd_days[z]<3:
            da[z]+=((odd_days[z]-1)*100)

    enumerated_data = list(enumerate(result))
    aligned_odd_days = odd_days + [None] * (len(result) - len(odd_days))
    aligned_even_days = even_days + [None] * (len(result) - len(even_days))
    aligned_da = da + [None] * (len(result) - len(da))

    print(f'aligned days={aligned_even_days}')
    print(f'aligned da={aligned_da}')

    # Ensure local_convenience is a valid number before converting
    amount = []
    for i in range(len(result)):
        local_convenience_value = result[i]['local_convenience']
        if local_convenience_value.isdigit():
            amount.append(int(local_convenience_value))
        else:
            amount.append(0)  # Default to 0 if not a valid number


    ta_admissible=[]
    for x in range(len(odd_days)):
        if odd_days[x]<3:
            ta_admissible.append(1)
        else:
            ta_admissible.append(2)

    fare_ammo = []
    for y in range(len(result)):
        fare_amount = result[y]['fare_amount']
        if fare_amount is None:
            fare_ammo.append(0)  # If fare_amount is None, append 0
        else:
            fare_ammo.append(int(fare_amount))  # Convert fare_amount to an integer and append it

    claim = []
    total=[]
    for k in range(len(ta_admissible)):
        total.append(ta_admissible[k] * int(fare_ammo[k*2]))
        claim.append((ta_admissible[k] * int(fare_ammo[k*2])) + da[k] + amount[2 * k] + amount[(2 * k) + 1])

    total_amount = sum(claim)
    return render_template('print.html', travel_data=enumerated_data, da=da, even_days=even_days,
                           odd_days=odd_days, aligned_even_days=aligned_even_days, aligned_odd_days=aligned_odd_days,
                           aligned_da=aligned_da, claim=claim,total_amount=total_amount,total=total)


if  __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)


