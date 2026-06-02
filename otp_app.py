from flask import Flask, request, render_template_string, redirect, session
import json
import os
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "mfa_secret_key"

# New database file
DATA_FILE = "sara.json"

# Your Gmail details
EMAIL_ADDRESS = "ritesh47748@gmail.com"
EMAIL_PASSWORD = "ehbe chvg miyt esgg"


# ----------------------------
# DATABASE FUNCTIONS
# ----------------------------

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ----------------------------
# EMAIL OTP FUNCTION
# ----------------------------

def send_email_otp(receiver_email, otp):

    subject = "Your MFA OTP Code"

    body = f"""
Hello,

Your One-Time Password (OTP) is:

{otp}

Please enter this code to complete your login.

Regards,
MFA Authentication System
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(
        EMAIL_ADDRESS,
        EMAIL_PASSWORD
    )

    server.send_message(msg)
    server.quit()


# ----------------------------
# STYLE
# ----------------------------

style = """
<style>

body{
    margin:0;
    font-family:Arial, sans-serif;
    background:linear-gradient(135deg,#1e3c72,#2a5298);
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
}

.container{
    background:white;
    padding:35px;
    width:420px;
    border-radius:15px;
    text-align:center;
    box-shadow:0px 0px 25px rgba(0,0,0,0.3);
}

input{
    width:90%;
    padding:12px;
    margin:8px;
    border:1px solid #ccc;
    border-radius:6px;
}

button{
    padding:12px 25px;
    border:none;
    background:#2a5298;
    color:white;
    border-radius:6px;
    cursor:pointer;
}

button:hover{
    background:#1e3c72;
}

a{
    text-decoration:none;
    color:#2a5298;
    font-weight:bold;
}

.message{
    margin-top:15px;
}

</style>
"""


# ----------------------------
# PAGES
# ----------------------------

register_page = style + """

<div class="container">

<h2>Create MFA Account</h2>

<form method="POST">

<input type="text"
name="username"
placeholder="Username"
required>

<input type="email"
name="email"
placeholder="Email Address"
required>

<input type="password"
name="password"
placeholder="Password"
required>

<br><br>

<button type="submit">
Register
</button>

</form>

<p class="message">{{message}}</p>

<a href="/">Back to Login</a>

</div>
"""


login_page = style + """

<div class="container">

<h2>MFA Login System</h2>

<form method="POST">

<input type="text"
name="username"
placeholder="Username"
required>

<input type="password"
name="password"
placeholder="Password"
required>

<br><br>

<button type="submit">
Login
</button>

</form>

<p class="message">{{message}}</p>

<a href="/register">
Create Account
</a>

</div>
"""


otp_page = style + """

<div class="container">

<h2>Email Verification</h2>

<p>
A One-Time Password has been sent to your email.
</p>

<form method="POST">

<input type="text"
name="otp"
placeholder="Enter OTP"
required>

<br><br>

<button type="submit">
Verify OTP
</button>

</form>

<p class="message">{{message}}</p>

</div>
"""


success_page = style + """

<div class="container">

<h1>✅ Login Successful</h1>

<h3>Welcome {{username}}</h3>

<p>
Multi-Factor Authentication completed successfully.
</p>

<a href="/">
Logout
</a>

</div>
"""


# ----------------------------
# REGISTER
# ----------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if username in users:

            message = "User already exists ❌"

        else:

            users[username] = {
                "email": email,
                "password": password
            }

            save_users(users)

            message = "Account created successfully ✅"

    return render_template_string(
        register_page,
        message=message
    )


# ----------------------------
# LOGIN
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        password = request.form["password"]

        if (
            username in users
            and users[username]["password"] == password
        ):

            otp = str(
                random.randint(
                    100000,
                    999999
                )
            )

            session["otp"] = otp
            session["username"] = username

            email = users[username]["email"]

            send_email_otp(
                email,
                otp
            )

            return redirect("/otp")

        else:

            message = "Invalid credentials ❌"

    return render_template_string(
        login_page,
        message=message
    )


# ----------------------------
# OTP PAGE
# ----------------------------

@app.route("/otp", methods=["GET", "POST"])
def otp():

    message = ""

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if entered_otp == session.get("otp"):

            username = session.get("username")

            return render_template_string(
                success_page,
                username=username
            )

        else:

            message = "Incorrect OTP ❌"

    return render_template_string(
        otp_page,
        message=message
    )


# ----------------------------
# RUN APP
# ----------------------------

if __name__ == "__main__":

    print("Starting MFA Email Application...")

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))