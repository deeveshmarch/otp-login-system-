print("OTP App Starting...")

from flask import Flask, request, render_template_string, redirect, session
import os
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =========================
# EMAIL CONFIG (YOUR EMAIL)
# =========================
EMAIL_ADDRESS = "yourgmail@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# =========================
# SIMPLE USER (for testing)
# =========================
USER_DATA = {
    "admin": {
        "password": "1234",
        "email": "receiver_email@gmail.com"
    }
}

# =========================
# LOGIN PAGE
# =========================
login_page = """
<h2>Login</h2>
<form method="post">
Username: <input name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<input type="submit" value="Login">
</form>
<p>{{message}}</p>
"""

# =========================
# OTP PAGE
# =========================
otp_page = """
<h2>Enter OTP</h2>
<form method="post">
OTP: <input name="otp"><br><br>
<input type="submit" value="Verify">
</form>
<p>{{message}}</p>
"""

# =========================
# SEND EMAIL OTP
# =========================
def send_email_otp(receiver_email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("OTP sent ✅")
    except Exception as e:
        print("Email error:", e)

# =========================
# LOGIN ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER_DATA and USER_DATA[username]["password"] == password:
            session["user"] = username
            session["email"] = USER_DATA[username]["email"]

            # generate OTP ONCE
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["otp_sent"] = False

            return redirect("/otp")
        else:
            message = "Invalid credentials ❌"

    return render_template_string(login_page, message=message)

# =========================
# OTP ROUTE (FIXED)
# =========================
@app.route("/otp", methods=["GET", "POST"])
def otp():
    if "user" not in session:
        return redirect("/")

    message = ""

    # SEND OTP ONLY ONCE
    if not session.get("otp_sent"):
        send_email_otp(session["email"], session["otp"])
        session["otp_sent"] = True

    if request.method == "POST":
        user_otp = request.form["otp"]

        if user_otp == session.get("otp"):
            session.clear()
            return "<h2>Login Successful ✅</h2>"
        else:
            message = "Invalid OTP ❌"

    return render_template_string(otp_page, message=message)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
