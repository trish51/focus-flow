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

# Calling this function ensures the respective functions don't run unless the user is logged in
# If you aren't logged in, it kicks you out of pages and ensures you are in the login/register pages
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
    # Get the user_id from the session
    user_id = session.get("user_id")
    
    # Gets the users details
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    
    # If user doesn't exist, clear session and go to login
    if not rows:
        session.clear()
        return redirect("/login")
        
    # Returns the users details
    return render_template("index.html", user=rows[0])

# Register Logic
@app.route("/register", methods=["GET", "POST"])
def register():
    # Clear any previous sessions
    session.clear()

    # Stores user inputs in variables
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
        
        # hashes the password so its stored securly 
        hash = generate_password_hash(password)
        
        # Adding to the database
        # Ensures the username doesn't already exist
        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?)",
                username, hash
            )

            # Logs them in immediatley and puts them on the timer page
            session["user_id"] = new_user_id
            session["username"] = username
            return redirect("/")
        except ValueError:
            return "Username already exists.", 400
    # If user cannot be logged in, puts them back on the register page
    return render_template("register.html")


# Login logic
@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any previous sessions
    session.clear()

    # Stores user inputs in variables
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        # Checks if the username exists and if it links to the correct password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username and/or password", 403

        # Remeber which user logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Ensures the theme the user previously selected is on
        session["theme"] = rows[0]["active_theme"]

        # Logs them in immediatley and puts them on the timer page
        return redirect("/")

    # If user cannot be logged in, puts them back on the login page
    return render_template("login.html")

# History page
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
    
    # Returns the historical infomation we have from the user 
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

    # Get all the items availible in the store
    items = db.execute("SELECT * FROM items")

    # Get the ids of the items the user already bought
    owned_rows = db.execute(
        "SELECT item_id FROM purchases WHERE user_id = ?",
        user_id
    )
    owned_ids = [row["item_id"] for row in owned_rows]

    # returns all items to be displayed in the store
    return render_template("store.html", items=items, user_xp=user_xp, owned_ids=owned_ids)

# Spending XP
@app.route("/buy",  methods=["POST"])
@login_required
def buy():

    # Gets the item ids from the items that are clicked by the user
    item_id = request.form.get("item_id")
    user_id = session["user_id"]

    # Item details - also checks if the item exists
    item = db.execute(
        "SELECT * FROM items WHERE id = ?",
        item_id
    )
    if not item:
        return "Item not found", 400

    price = item[0]["price"]

    # Check if user has enough XP to buy the item
    user_data = db.execute(
        "SELECT xp FROM users WHERE id = ?",
        user_id
    )
    current_xp = user_data[0]["xp"]

    if current_xp < price:
        return "Not enough XP", 400

    # If the user can afford
    # Deducts users XP and record purchases
    db.execute(
        "UPDATE users SET xp = xp - ? WHERE id = ?", 
        price, user_id
    )
    db.execute(
        "INSERT INTO purchases (user_id, item_id) VALUES (?,?)",
        user_id, item_id
    )

    # Keeps the user on the store page after a purchase
    return redirect("/store")

# Equiping themes
@app.route("/equip",  methods=["POST"])
@login_required
def equip():
    item_id = request.form.get("item_id")
    user_id = session["user_id"]

    # Check if the default theme is active
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

    # gets the theme name to use it in CSS
    if check:
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
    
    # Keeps the user on the store page after equiping
    return redirect("/store")

# Logout logic
@app.route("/logout")
def logout():

    # Clears session and takes users to the login page
    session.clear()
    return redirect("/")


# Log user data
@app.route("/log_session", methods=["POST"])
@login_required
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

    # Returns that the logging of data was successful
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)