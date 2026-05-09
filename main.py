from flask import Flask, render_template, session, redirect, flash
from controllers.auth_controller import login, register

app = Flask(__name__)
app.secret_key = "abc123"

@app.route("/auth")
def auth():
    return render_template("login.html")
# Login
@app.route("/login", methods=["POST"])
def login_route():
    return login()

# Register
@app.route("/register", methods=["POST"])
def register_route():
    return register()

# Trang chính
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/auth")
    return render_template("home.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth")

if __name__ == "__main__":
    app.run(debug=True)