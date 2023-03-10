from flask import render_template, Flask, request, session, redirect, url_for, jsonify, make_response, abort, flash
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from flask import current_app as app
from application.database import db
from application.models0 import Users, Bloodbank, DonationRequests, Badges, Badges_Users_Association, BloodstatW
from datetime import datetime
import os
import plotly.graph_objs as go
import base64
from base64 import b64encode
from sqlalchemy.exc import IntegrityError

app.jinja_env.filters['b64encode'] = b64encode

#-------------------------------BLOODBANK routes--------------------------------------------------------------------------


@app.route("/bblogin", methods = ["GET","POST"])
def bbloginpage():
	global pinc
	if (request.method=="GET"):
		return render_template("fpageBB.htm")
	elif (request.method=="POST"):
		bname = request.form["bname"]
		pinc = request.form["bank_pincode"]
		bank = db.session.query(Bloodbank).filter(Bloodbank.bank_name == bname, Bloodbank.bank_pincode == pinc).first()
		if (bank):
			session["bname"] = bname
			session["pinc"] = pinc

			return redirect(url_for("bname"))
		else:
			return redirect(url_for("bbloginpage"))
	else:
		if "bname" in session:
			return redirect(url_for("bname"))
		return ("Error Check")

@app.route("/bblogout", methods = ["GET","POST"])
def bblogout():
	session.pop("bname", None)
	return render_template("index.htm")

@app.route("/bname", methods = ["GET","POST"])
def bname():
	if "bname" in session:
		bname = session["bname"]
		pinc = session["pinc"]
		b_id = db.session.query(Bloodbank.bank_id).filter(Bloodbank.bank_name == bname, Bloodbank.bank_pincode == pinc).first()
		chart = blood_status_chart(b_id[0])
		return render_template("1pageBB.htm", d_name = bname, chart = chart)



@app.route("/approve-request/<int:Req_id>", methods=["POST"])
def approve_request(Req_id):
    myquery = db.session.query(DonationRequests).filter_by(Req_id = Req_id).first()
    (myquery.Req_status,myquery.Response_date) = ('approved',datetime.today())
    db.session.commit()
    return {'message': 'Request approved successfully!'}

@app.route("/cancel-request/<int:Req_id>", methods=["POST"])
def cancel_request(Req_id):
	myquery = db.session.query(DonationRequests).filter_by(Req_id = Req_id).first()
	if myquery:
		donor_username = db.session.query(DonationRequests.Received_from).filter(DonationRequests.Req_id == Req_id).first()
		donation_count_row = db.session.query(Users.donation_count).filter(Users.username == donor_username[0]).first()		#this returns a row object in form of a tuple
		donation_count = donation_count_row[0]											#this assigns the zeroth index of the tuple to the donation count
		donation_count += 1
		db.session.query(Users).filter(Users.username == donor_username[0]).update({"donation_count": donation_count})		#update the record in the table
		badge_check = db.session.query(Badges.badge_id,Badges.badge_count_required).filter(Badges.badge_count_required==donation_count).first()
		if (badge_check):
			award_badge_to_user(badge_check[0], donor_username[0])
			db.session.commit()
		db.session.delete(myquery)
		db.session.commit()
		return {'message': 'Request Cancelled successfully!'}
	
	else:
        	return {'message': 'Error: Request does not exist!'}

@app.route("/reject-request/<int:Req_id>", methods=["POST"])
def reject_request(Req_id):
	myquery = db.session.query(DonationRequests).filter_by(Req_id = Req_id).first()
	if myquery:
		db.session.delete(myquery)
		db.session.commit()
		return {'message': 'Request Cancelled successfully!'}
	
	else:
        	return {'message': 'Error: Request does not exist!'}

@app.route("/listofrequests", methods=["POST"])
def listofrequests():
     bname = session["bname"]
     pinc = session["pinc"]
     b_id = db.session.query(Bloodbank.bank_id).filter(Bloodbank.bank_name == bname, Bloodbank.bank_pincode == pinc).first()
     #query database for requests
     totreceived_req = (db.session.query(DonationRequests.Req_id,DonationRequests.Received_from, Users.blood_group, DonationRequests.Req_status, DonationRequests.Received_date).join(Users, DonationRequests.Received_from == Users.username).filter(DonationRequests.Received_by == b_id[0]).all())

     # Build an HTML string to represent the list of blood banks

     html = "<table><thead><tr><th>Name</th><th>Blood Group</th><th>Date Received</th><th>Request Status</th><th>Approve/Cancel Request</th></tr></thead><tbody>"

     for request in totreceived_req:
        html += f"<tr><td>{request.Received_from}</td><td>{request.blood_group}</td><td>{request.Received_date}</td><td>{request.Req_status}</td><td><button onclick=\"approveRequest('{request.Req_id}');\">Approve</button><button onclick=\"cancelRequest('{request.Req_id}');\">Cancel</button><button onclick=\"rejectRequest('{request.Req_id}');\">Reject</button></td></tr>"
     html += "</tbody></table>"
     # Return the HTML string as a JSON object
     return jsonify({'html': html})

@app.route('/update', methods=['POST'])
def update_blood_status():
	blood_status = (db.session.query(BloodstatW).join(Bloodbank, BloodstatW.bank_id == Bloodbank.bank_id).filter(Bloodbank.bank_name == session["bname"], Bloodbank.bank_pincode == session["pinc"] ).first())
	
	if blood_status is None:
		blood_status = BloodstatW(bank_id=1)
		db.session.add(blood_status)

	A_pos = request.form.get('A_pos')
	if A_pos is not None:
		blood_status.A_pos = A_pos

	AB_pos = request.form.get('AB_pos')
	if AB_pos is not None:
		blood_status.AB_pos = AB_pos

	B_pos = request.form.get('B_pos')
	if B_pos is not None:
		blood_status.B_pos = B_pos

	O_pos = request.form.get('O_pos')
	if O_pos is not None:
		blood_status.O_pos = O_pos

	A_neg = request.form.get('A_neg')
	if A_neg is not None:
		blood_status.A_neg = A_neg

	AB_neg = request.form.get('AB_neg')
	if AB_neg is not None:
		blood_status.AB_neg = AB_neg

	B_neg = request.form.get('B_neg')
	if B_neg is not None:
		blood_status.B_neg = B_neg

	O_neg = request.form.get('O_neg')
	if O_neg is not None:
		blood_status.O_neg = O_neg

	db.session.commit()

	return jsonify({'message': 'Blood status updated.'})
	#return {'message': 'Blood Status updated successfully!'}


#---------------------------------------------------------------------------------------


#--------------------------------Crude functions-----------------------------------------------

def blood_status_chart(bank_id):
	blood_stock = db.session.query(BloodstatW.A_pos,BloodstatW.AB_pos,BloodstatW.B_pos,BloodstatW.O_pos,BloodstatW.A_pos,BloodstatW.AB_neg,BloodstatW.B_neg,BloodstatW.O_neg,Bloodbank.bank_name).join(Bloodbank, BloodstatW.bank_id == Bloodbank.bank_id).filter(Bloodbank.bank_id == bank_id).first()
	blood_types = ['A+', 'AB+', 'B+', 'O+', 'A-', 'AB-', 'B-', 'O-']
	values =[]
	for a in range (0,8,1):
		values.append(blood_stock[a])
	fig = go.Figure(data=[go.Bar(x=blood_types, y=values, marker=dict(color='orange'))])
	fig.update_layout(title='Blood Stock for Bank Name: {}'.format(blood_stock.bank_name), xaxis_title='Blood Types', yaxis_title='Quantity in Litres')
	fig.add_hrect(y0=0, y1=10, line_width=0, fillcolor="red", opacity=0.25)
	chart_html = fig.to_html(full_html=False)
	return chart_html

def get_badge_image(badge_id):
    badge = Badge.query.get(badge_id)
    if badge:
        image_data = base64.b64encode(badge.badge_image).decode('utf-8')
        return f"data:image/jpeg;base64,{image_data}"
    return None

def generate_pdf(request_recipient, bank_name, bank_address, Response_date):
    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)

    # Draw things on the PDF. Here's where the PDF generation happens.

    # Adding logo image
    logo_path = r"C:\Users\DELL\Desktop\bledblood\static\images\logo_1_0.jpg"

    logo_width, logo_height = 180, 180
    logo_x = (letter[0] - logo_width) / 2  # center horizontally
    logo_y = 500  # place below the border
    p.drawImage(logo_path, x=logo_x, y=logo_y, width=logo_width, height=logo_height)
    

    # Set font and center alignment
    p.setFont('Helvetica-Bold', 16)
    p.drawCentredString(300, 685, 'Appointment Slip')

    # Add borders
    p.setStrokeColor(colors.red)
    p.setLineWidth(1)
    p.rect(50, 50, 500, 700, stroke=1, fill=0)

    # Add name, bloodbank name, bloodbank address and date
    p.setFont('Helvetica', 10)
    p.drawString(150, 450, f'Username: {request_recipient}')
    p.drawString(150, 425, f'Bank Name: {bank_name}')
    p.drawString(150, 400, f'Bank Address: {bank_address}')
    p.drawString(150, 375, f'Response Date: {Response_date}')

    p.setFillColorRGB(0.88,0.08,0.27)
    p.setFont('Helvetica', 8)
    p.drawString(120, 350, f'Caution: Kindly Carry your Recent Medical reports with a Governmnet Identity Card. They would be verified')
    
    p.setFillColorRGB(0.88,0.08,0.27)
    p.setFont('Helvetica', 8)
    p.drawString(80, 330, f'Donors are requested to refrain from smoking or consuming any type of addictive materials within 2hrs before and after donation.')



    newpic_path = r"C:\Users\DELL\Desktop\bledblood\static\images\doc_withblddon0.jpg"
    newpic_width, newpic_height = 200, 200
    newpic_x = (letter[0] - newpic_width) / 2  # center horizontally
    newpic_y = 120  # place below the border
    p.drawImage(newpic_path, x=newpic_x, y=newpic_y, width=newpic_width, height=newpic_height)

    # Add more content as needed.

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # File buffer rewind
    buffer.seek(0)

    return buffer


def award_badge_to_user(badge_id, username):
	user = Users.query.filter_by(username=username).first()
	badge = Badges.query.get(badge_id)

	if not username:
		abort(404, description="User not found")

	if not badge_id:
		abort(404, description="Badge not found")

	association = Badges_Users_Association.query.filter_by(user_username=user.username, badge_id=badge.badge_id).first()

	if association:
        	abort(400, description="Badge already awarded to user")

	association = Badges_Users_Association(user_username=user.username, badge_id=badge.badge_id, badge_earned_date=datetime.now())
	db.session.add(association)
	db.session.commit()


#------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user/appointment_slip/<string:request_recipient>/<string:bank_name>/<string:bank_address>/<string:Response_date>", methods=["POST"])
def downloadslipfunc(request_recipient, bank_name, bank_address, Response_date):
    try:
        pdf = generate_pdf(request_recipient, bank_name, bank_address, Response_date)
        response = make_response(pdf.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=appointment.pdf'
        return response, 200
    except Exception as e:
        return {"message": str(e)}, 500

@app.route("/pincode-lookup", methods=["POST"])
def pincode_lookup():
    # Get the zip code entered by the user
    pincode = request.form["pincode"]

    # Query the database for blood banks with the matching pin code
    banks = db.session.query(Bloodbank.bank_id,Bloodbank.bank_name,Bloodbank.bank_pincode).filter(Bloodbank.bank_pincode == pincode).all()

    # Build an HTML string to represent the list of blood banks

    html = "<table><thead><tr><th>Blood Bank ID</th><th>Blood Bank Name</th><th>Pincode</th><th>Send Donation Request</th></tr></thead><tbody>"
    sender = session["username"]
    
    for bank in banks:
        html += f"<tr><td>{bank.bank_id}</td><td>{bank.bank_name}</td><td>{bank.bank_pincode}</td><td><button onclick=\"addRequest('{sender}', '{bank.bank_id}');\">Add Request</button></td></tr>"
    html += "</tbody></table>"
    # Return the HTML string as a JSON object
    return jsonify({'html': html})

@app.route("/add-request/<string:Received_from>/<int:Received_by>", methods=["POST"])
def add_request(Received_from, Received_by):
    Received_date = datetime.today()
    request = DonationRequests(Received_date =Received_date,Received_from=Received_from, Received_by=Received_by)
    db.session.add(request)
    db.session.commit()
    return {'message': 'Request sent successfully!'}

@app.route("/approvedlistofrequests", methods=["POST"])
def approvedlistofrequests():
    request_recipient = session["username"]
    #query database for requests
    totreceived_req = (db.session.query(DonationRequests.Req_id,Bloodbank.bank_name, Bloodbank.bank_address, DonationRequests.Received_by, DonationRequests.Req_status, DonationRequests.Response_date).join(Bloodbank, DonationRequests.Received_by == Bloodbank.bank_id).filter(DonationRequests.Received_from == request_recipient, DonationRequests.Req_status == 'approved' ).all())

    # Build an HTML string to represent the list of blood banks

    html_result = "<table><thead><tr><th>Blood Bank Name</th><th>Request Status</th><th>Date Approved</th><th>Download Appointment Slip</th></tr></thead><tbody>"

    for request in totreceived_req:
       	html_result += f"<tr><td>{request.bank_name}</td><td>{request.Req_status}</td><td>{request.Response_date}</td><td><button onclick=\"downloadslipfunc('{request_recipient}','{request.bank_name}', '{request.bank_address}','{request.Response_date}')\">Download</button></td></tr>"
    html_result += "</tbody></table>"
    # Return the HTML string as a JSON object
    return jsonify({'html': html_result})

@app.route("/", methods = ["GET","POST"])
def defaultpage():
  	return render_template("index.htm")

@app.route("/selectpage", methods = ["GET","POST"])
def selectpage():
	return render_template("selectpage.htm")

@app.route("/userselectpage", methods = ["GET","POST"])
def user_selectpage():
	return render_template("User_selectpage.htm")

@app.route("/registerpage", methods = ["GET","POST"])
def registerpage():
	return render_template("registerpage.htm")

@app.route("/login", methods = ["GET","POST"])
def loginpage():
	if (request.method=="GET"):
		return render_template("fpage.htm")
	elif (request.method=="POST"):
		username = request.form["username"]
		psswd = request.form["pswd"]
		user = db.session.query(Users).filter(Users.username == username, Users.pswd == psswd).first()

		if (user):
			session["username"] = username
			return redirect(url_for("username"))
		else:
			return render_template("fpage.htm")
			
	else:
		if "username" in session:
			return redirect(url_for("username"))
		return ("Error Check")


@app.route("/user", methods = ["GET","POST"])
def username():
	if "username" in session:
		username = session["username"]
		first_name = db.session.query(Users.fname).filter(Users.username==username).first()
		return render_template("1page.htm", display_username = first_name[0])

@app.route("/user/summary", methods = ["GET","POST"])
def summary():
	return render_template("summary.htm")

@app.route("/user/achievements", methods = ["GET","POST"])
def achievements():
	donor_name = session["username"]
	user = Users.query.filter_by(username=donor_name).first()
	if user is None:
        	return 'User not found'
	badges = Badges.query.join(Badges_Users_Association).filter(Badges_Users_Association.user_username==donor_name).all()
	for badge in badges:
		badge.badge_image = base64.b64encode(badge.badge_image).decode('utf-8')

	return render_template("achievements.htm", badges = badges)



@app.route("/user/logout", methods = ["GET","POST"])
def logout():
	session.pop("username", None)
	return redirect(url_for("defaultpage"))

@app.route('/register', methods=["POST"])
def registration():
	username = request.form['username']
	password = request.form['pswd']
	blood_group = request.form['bld_grp']
	fname = request.form['first_name']
	lname = request.form['last_name']
	age = request.form['age']
	pincode = request.form['pincode']
	comorbidities = request.form['Comorbidities']
	if (comorbidities == "Yes"):
		comorbidities = 1
	else:
		comorbidities = 0
	gender = request.form['Gender']
	email = request.form['email']

	if db.session.query(Users).filter(Users.username == username).first() is not None:
		flash('Username already exists.')
		return redirect(url_for('registerpage'))
	elif db.session.query(Users).filter(Users.email == email).first() is not None:
		flash('Email already exists.')
		return redirect(url_for('registerpage'))
	
	user = Users(username=username, pswd=password,blood_group = blood_group, fname=fname, lname=lname,  age=age, pincode = pincode, comorbidities = comorbidities, Gender=gender, email=email)
	try:
		# code that may cause a database error
		db.session.add(user)
		db.session.commit()
		flash('Registration successful!')
		return redirect(url_for('loginpage'))

	except IntegrityError as e:
		# handle the database error
		db.session.rollback()
		flash('Error registering user: {}'.format(str(e)))
		return redirect(url_for('registerpage'))

	except Exception as e:
		# handle any other errors
		db.session.rollback()
		flash('Error registering user: {}'.format(str(e)))
		return redirect(url_for('registerpage'))