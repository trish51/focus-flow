from cs50 import SQL
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///focus.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    # 1. Get the user_id from the session
    user_id = session.get("user_id")
    
    # 2. Check the database
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    
    # 3. If user doesn't exist, clear session and go to login
    if not rows:
        session.clear()
        return redirect("/login")
        
    return render_template("index.html", user=rows[0])

# Register Logic
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Data Validation
        if not username:
            return "Please provide a username", 400
        elif not password:
            return "Please provide a password", 400
        elif password != confirmation:
            return "Passwords do not match", 400
        
        hash = generate_password_hash(password)
        
        # Adding to the database
        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?)",
                username, hash
            )

            # Logs them in immediatley
            session["user_id"] = new_user_id
            session["username"] = username
            return redirect("/")
        except ValueError:
            return "Username already exists.", 400
    return render_template("register.html")


# Login logic
@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any previous sessions
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        # Checks if the username exists
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username and/or password", 403

        # Remeber shich user logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        return redirect("/")

    return render_template("login.html")

# History
@app.route("/history")
@login_required
def history():
    # Fetch all sessions for the current user
    sessions = db.execute("""
        SELECT minutes, note, strftime('%Y-%m-%d %H:%M', timestamp) as time 
        FROM sessions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, session["user_id"])
    
    return render_template("history.html", sessions=sessions)


# Logout logic
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Log user data
@app.route("/log_session", methods=["POST"])
def log_session():
    # Get the data from the JS fetch request
    data = request.get_json()
    minutes = data.get("minutes")
    note = data.get("note")
    user_id = session["user_id"]

    
    # Updated the users XP wihin the users table - 10XP for every session
    db.execute(
        "UPDATE users SET xp = xp + 10 WHERE id = ?",
        user_id
    )

    # Log this session in sessions for history/stats
    db.execute(
        "INSERT INTO sessions (user_id, minutes, note) VALUES (?,?,?)",
        user_id, minutes, note
    )

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)