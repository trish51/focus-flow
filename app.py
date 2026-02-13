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

        # Remeber which user logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Ensures user selected theme is on
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["theme"] = rows[0]["active_theme"]

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

# XP stop
@app.route("/store")
@login_required
def store():
    user_id = session["user_id"]

    # Get users current XP
    user_data = db.execute(
        "SELECT xp FROM users WHERE id = ?", 
        user_id
    )
    user_xp = user_data[0]["xp"]

    # Get items from the store
    items = db.execute("SELECT * FROM items")

    # Get ids of what the user already bought
    owned_rows = db.execute(
        "SELECT item_id FROM purchases WHERE user_id = ?",
        user_id
    )
    owned_ids = [row["item_id"] for row in owned_rows]

    return render_template("store.html", items=items, user_xp=user_xp, owned_ids=owned_ids)

# Spending XP
@app.route("/buy",  methods=["POST"])
@login_required
def buy():
    item_id = request.form.get("item_id")
    user_id = session["user_id"]

    # Item details
    item = db.execute(
        "SELECT * FROM items WHERE id = ?",
        item_id
    )
    if not item:
        return "Item not found", 400

    price = item[0]["price"]

    # Check if user can afford
    user_data = db.execute(
        "SELECT xp FROM users WHERE id = ?",
        user_id
    )
    current_xp = user_data[0]["xp"]

    if current_xp < price:
        return "Not enough XP", 400

    # Deduct XP and record purchases
    db.execute(
        "UPDATE users SET xp = xp - ? WHERE id = ?", 
        price, user_id
    )
    db.execute(
        "INSERT INTO purchases (user_id, item_id) VALUES (?,?)",
        user_id, item_id
    )

    return redirect("/store")

# Equiping themes
@app.route("/equip",  methods=["POST"])
@login_required
def equip():
    item_id = request.form.get("item_id")
    user_id = session["user_id"]

    # Check if default
    if item_id == "0":
        db.execute(
            "UPDATE users SET active_theme = 'default' WHERE id = ?", 
            user_id
        )
        session["theme"] = "default"
        return redirect("/store")

    # Otherwise verify ownership of purchasable themes
    check = db.execute(
        "SELECT * FROM purchases WHERE user_id = ? AND item_id = ?", 
        user_id, item_id
    )

    if check:
        # get the name and use it in CSS
        item = db.execute(
            "SELECT name FROM items WHERE id = ?", 
            item_id
        )
        theme_name = item[0]["name"].lower().replace(" ","-")

        db.execute(
            "UPDATE users SET active_theme = ? WHERE id = ?",
            theme_name, user_id
        )
        session["theme"] = theme_name
    
    return redirect("/store")

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