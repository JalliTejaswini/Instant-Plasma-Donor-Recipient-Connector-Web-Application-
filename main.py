from flask import Flask, make_response, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from db_functions import register_donor, user_loginDb, get_user_profileDb, check_if_email_exists, set_fileDb, login_bbankDb, bbank_view_donorsDb, update_bbank_donor_status, get_donor_blood_requestDb, add_bloodDb, h_loginDb, h_registerDb, get_bloodDb, request_blood, show_blood_reqDb, get_all_hosp_reqDb,update_hosp_reqDb,hsp_req_feedbackDb,get_hsp_feedDb,get_donor_mail_id
import os
import smtplib

UPLOAD_FOLDER = './cert_uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
smtp_email = 'tejaswinijalli888@gmail.com'
smtp_password = 'wqgofvugcosgghqx'

def send_mail(email_id,userId):
    try:
        subject = "Blood Bank"
        body = "You have a new request from Blood Bank"
        msg = f"Subject: {subject}\n\n{body}\nhttp://127.0.0.1:5000/donor-home?userId={userId}."
        conn = smtplib.SMTP("smtp.gmail.com", 587)
        conn.starttls()
        conn.login(smtp_email, smtp_password)
        conn.sendmail(smtp_email, email_id, msg)
        conn.close()
    except Exception as e:
        print("Mail sending failed",e)

# ################## donor route ##################


def get_cert_loc(userId):
    files_list = os.listdir("./cert_uploads/")
    for x in files_list:
        find = f"{userId}_"
        if x.find(find) == 0:
            return x
    return ''


@app.route("/donorLogin", methods=['GET', 'POST'])
@app.route("/donor-login", methods=["GET", 'POST'])
@app.route("/donorRegister", methods=["GET", 'POST'])
def user_login_page():
    if request.method == "POST":
        if request.path == "/donorRegister":
            username = request.form.get("username")
            email_id = request.form.get("emailId")
            password = request.form.get('password')
            confirmPassword = request.form.get("confirmPassword")
            gender = request.form.get("gender")
            dob = request.form.get("dob")
            age = request.form.get('age')
            contact = request.form.get('contact')
            address = request.form.get("address")
            bgroup = request.form.get("bgroup")

            if password != confirmPassword:
                return render_template("donor_login.html", message="password does not match")

            if check_if_email_exists(email_id):
                return render_template("donor_login.html", message="email already exists")

            if not (username and email_id and password and gender and dob and age and contact and address and bgroup):
                return redirect(url_for("user_login_page"))

            register_donor(username, email_id, password, gender,
                           dob, bgroup, age, contact, address)

        elif request.path == '/donor-login':
            emailId = request.form.get("email")
            password = request.form.get("password")
            if not (emailId and password):
                return render_template("donor_login.html", message="invalid user or password")
            user = user_loginDb(emailId, password)
            if user:
                return redirect(url_for('donor_home', userId=user[0][0]))

    return render_template("donor_login.html")


@app.route('/donor-home')
def donor_home():
    args = request.args.to_dict()
    userId = args.get('userId')
    user = get_user_profileDb(userId)
    status = get_donor_blood_requestDb(userId)
    a = get_cert_loc(userId)
    if user is None:
        return redirect(url_for("user_login_page"))
    user = list(user)
    if user[2]:
        user[2] = request.url_root + "cert-file/" + a
    return render_template('donor_home.html', user=user, cert=a, status=status)


@app.route("/upload-cert", methods=['POST'])
def upload_cert():
    userId = request.args.get('userId')
    if 'file' not in request.files:
        return redirect(f"http://127.0.0.1:5000/donor-home?userId={userId}")
    file = request.files['file']
    if file.filename == '':
        return redirect(f"http://127.0.0.1:5000/donor-home?userId={userId}")
    filename = secure_filename(str(file.filename or ""))
    file.save(os.path.join(
        app.config['UPLOAD_FOLDER'], userId + "_" + filename))
    set_fileDb(filename, userId)
    return redirect(f"http://127.0.0.1:5000/donor-home?userId={userId}")


@app.route("/cert-file/<path:filename>")
def get_cert_file(filename):
    return send_file('./cert_uploads/'+filename, mimetype="image/png")


# ################## donor routes ends ##################


# ++++++++++++++++++ blood bank routes starts ++++++++++++++++++

@app.route("/b-banklogin", methods=['GET', 'POST'])
def b_bank_login():
    if request.method == "POST":
        admin_mail = request.form.get("email")
        password = request.form.get("password")
        if not(admin_mail and password):
            return render_template("b_login.html", message="invalid mail or password")
        user = login_bbankDb(admin_mail.strip(), password.strip())
        if user:
            return redirect(url_for("b_home"))
        return redirect(url_for("b_bank_login", s="true"))
    s = request.args.get("s")
    message = ''
    if s:
        message = "Invalid username or password"
    return render_template("b_login.html", message=message)


@app.route("/b-home")
def b_home():
    users = bbank_view_donorsDb()
    hosp_req = get_all_hosp_reqDb() # [(2, 'B+', 2, None, 'pending', 1)]
    return render_template("b_home.html", users=users, hosp_req=hosp_req)


@app.route("/req-donor", methods=["POST"])
@app.route("/donor-reply", methods=["POST"])
@app.route("/reply_hsp_req", methods=["POST"])
def req_donor():

    userId = request.args.get("userId")
    status = request.args.get("status")
    update_bbank_donor_status(status, userId)
    if request.path == '/req-donor':
        emailId = get_donor_mail_id(userId)
        if emailId:
            send_mail(emailId, userId) 
        return redirect(url_for('b_home'))
    elif request.path == "/reply_hsp_req":
        s = request.args.get('s')
        r_id = request.args.get("r_id")
        quan = request.args.get("quan")
        if s and r_id:
            if s == "approve":
                update_hosp_reqDb(r_id,"completed",int(quan))
            elif s == "reject":
                update_hosp_reqDb(r_id, "rejected")
    if request.path == "/donor-reply":
        return redirect(url_for("donor_home", userId=userId))
    return redirect(url_for("b_home"))


@app.route("/add-blood", methods=["POST"])
def add_blood():
    quan = request.form.get("quantity")
    userId = request.args.get('userId')
    bgroup = request.args.get("bgroup").upper()
    blood_map = {"1": "A+",  "2": "B+", "3": "O+",  "4": "AB+",
                 "5": "A-",  "6": "B-",  "7": "O-", "8": "AB-"}
    if bgroup.isdigit():
        bgroup = blood_map[bgroup]
    else:
        bgroup = "unknown"

    update_bbank_donor_status("completed", userId)
    add_bloodDb(bgroup, quan)
    return redirect(url_for("b_home"))

@app.route("/b_feedback")
def b_feedback():
    r_id = request.args.get("r_id")
    data = get_hsp_feedDb(r_id)
    return render_template("b_feedback.html", feedback=data)
    

# ++++++++++++++++++ blood bank routes ends ++++++++++++++++++


# ++++++++++++++++++ hospital routes starts ++++++++++++++++++


@app.route("/h-login", methods=['GET', "POST"])
def h_login():
    if request.method == "POST":
        h_name = request.form.get("h_name")
        pwd = request.form.get("password")
        post_type = request.args.get("type")

        if post_type == "register":
            contact = request.form.get("contact")
            address = request.form.get("address")
            if not (h_name and pwd and contact and address):
                return render_template("h_login.html", message="Fill all the fields")
            h_registerDb(h_name, pwd, contact, address)
            return redirect(url_for("h_login"))
        else:
            if not (h_name and pwd):
                return render_template("h_login.html", message="Invalid hospital name or password")
            h = h_loginDb(h_name, pwd)
            if h:
                return redirect(url_for("h_home", userId=h[0]))
            return render_template("h_login.html", message="Invalid hospital name or password")

    return render_template("h_login.html", message="")


@app.route("/h-home")
def h_home():
    userId = request.args.get('userId')
    users = (1,)
    all_groups = get_bloodDb(userId)
    blood_req = show_blood_reqDb(userId)
    return render_template("h_home.html", all_groups=all_groups, users=users, h_id=userId, blood_req=blood_req)


@app.route("/req-quan", methods=['POST'])
def request_quan():
    blood_map = {"1": "A+",  "2": "B+", "3": "O+",  "4": "AB+",
                 "5": "A-",  "6": "B-",  "7": "O-", "8": "AB-"}
    quan = request.form.get("quantity")
    bgroup = request.args.get("bgroup")
    h_id = request.args.get('h_id')
    bgroup = blood_map[bgroup]
    if h_id and bgroup and quan:
        request_blood(quan=quan, bgroup=bgroup, h_id=h_id)
    return redirect(url_for("h_home", userId=h_id))

@app.route("/h-feedback", methods=["GET", "POST"])
def feedback_view():
    r_id = request.args.get("r_id")
    u_id = request.args.get('u_id')
    if not (r_id and u_id):
        resp = make_response('<h1>Page Not Found</h1>')
        resp.status_code  = 404
        return resp
    if request.method == "POST":
        feed = request.form.get("feedback")
        if not feed:
            return redirect(url_for("feedback_view", r_id=r_id, u_id=u_id))
        hsp_req_feedbackDb(feed,r_id=r_id, u_id=u_id)
        return redirect(url_for("h_home",userId=u_id))
    
    return render_template("h_feedback.html")
    


# ++++++++++++++++++ hospital routes end ++++++++++++++++++

if __name__ == "__main__":
    app.run(debug=True)
