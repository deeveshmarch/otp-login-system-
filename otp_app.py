from flask import Flask, request, render_template_string, redirect, session
import json
import os
import random
import smtplib
from email.mime.text import MIMEText
import threading

app = Flask(__name__)
app.secret_key = "mfa_secret_key"

# Database file
DATA_FILE = "sara.json"

# Gmail credentials
EMAIL_ADDRESS = "ritesh47748@gmail.com"
EMAIL_PASSWORD = "ehbe chvg miyt esgg"


# ----------------------------
# DATABASE FUNCTIONS
# ----------------------------

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except:
        return {}


def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ----------------------------
# EMAIL OTP FUNCTION
# ----------------------------

def send_email_otp(receiver_email, otp):
    try:
        subject = "Your MFA OTP Code"

        body = f"""
Hello,

Your OTP is:

{otp}

Do not share this code.

Regards,
MFA System
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("OTP sent successfully ✅")

    except Exception as e:
        print("Email error:", e)


# ----------------------------
# STYLE
# ----------------------------

style = """
<style>
body{
    margin:0;
    font-family:Arial;
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
<input name="username" placeholder="Username" required>
<input name="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<br><br>
<button type="submit">Register</button>
</form>

<p class="message">{{message}}</p>
<a href="/">Back to Login</a>
</div>
"""


login_page = style + """
<div class="container">
<h2>MFA Login</h2>

<form method="POST">
<input name="username" placeholder="Username" required>
<input name="password" type="password" placeholder="Password" required>
<br><br>
<button type="submit">Login</button>
</form>

<p class="message">{{message}}</p>
<a href="/register">Create Account</a>
</div>
"""


otp_page = style + """
<div class="container">
<h2>OTP Verification</h2>

<p>OTP sent to your email</p>

<form method="POST">
<input name="otp" placeholder="Enter OTP" required>
<br><br>
<button type="submit">Verify</button>
</form>

<p class="message">{{message}}</p>
</div>
"""


success_page = style + """
<div class="container">
<h1>Login Successful ✅</h1>
<h3>Welcome {{username}}</h3>
<a href="/">Logout</a>
</div>
"""


# ----------------------------
# REGISTER
# ----------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    users = load_users()

    if request.method == "POST":
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

    return render_template_string(register_page, message=message)


# ----------------------------
# LOGIN
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    users = load_users()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:

            otp = str(random.randint(100000, 999999))

            session["otp"] = otp
            session["username"] = username

            email = users[username]["email"]

            # 🔥 FIX: non-blocking email (prevents Render freezing)
            threading.Thread(
                target=send_email_otp,
                args=(email, otp)
            ).start()

            return redirect("/otp")

        else:
            message = "Invalid credentials ❌"

    return render_template_string(login_page, message=message)


# ----------------------------
# OTP VERIFY
# ----------------------------

@app.route("/otp", methods=["GET", "POST"])
def otp():
    if "username" not in session:
        return redirect("/")

    message = ""

    if request.method == "POST":
        entered = request.form["otp"]

        if entered == session.get("otp"):
            username = session.get("username")
            return render_template_string(success_page, username=username)
        else:
            message = "Incorrect OTP ❌"

    return render_template_string(otp_page, message=message)


# ----------------------------
# RUN (RENDER SAFE)
# ----------------------------

if __name__ == "__main__":
    print("Starting MFA App...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
