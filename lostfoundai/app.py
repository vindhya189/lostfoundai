from flask import Flask, render_template, request, redirect, session
import mysql.connector
from fuzzywuzzy import fuzz
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "lostfoundai_secret"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vindhya@123",
    database="lostfounddb"
)

cursor = db.cursor(buffered=True)
@app.route("/")
def start():

    return redirect("/login")

@app.route("/home")
def home():

    cursor.execute(
        "SELECT COUNT(*) FROM lost_items"
    )
    lost_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM found_items"
    )
    found_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM lost_items"
    )
    total_reports = cursor.fetchone()[0] + found_count

    return render_template(
    "index.html",
    lost_count=lost_count,
    found_count=found_count,
    total_reports=total_reports,
    username=session.get("username")
)

@app.route("/lost")
def lost():
    return render_template("lost.html")

@app.route("/found")
def found():
    return render_template("found.html")

@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/submit_lost", methods=["POST"])
def submit_lost():

    item_name = request.form["item_name"]
    category = request.form["category"]
    description = request.form["description"]
    location = request.form["location"]
    phone = request.form["phone"]

    image = request.files["image"]
    filename = str(int(time.time())) + "_" + secure_filename(image.filename)

    image.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    )

    sql = """
    INSERT INTO lost_items
    (item_name, category, description, location, phone, image)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    values = (
        item_name,
        category,
        description,
        location,
        phone,
        filename
    )

    cursor.execute(sql, values)
    db.commit()

    return "Lost Item Saved Successfully!"
@app.route("/submit_found", methods=["POST"])
def submit_found():

    print(request.files)

    item_name = request.form["item_name"]
    category = request.form["category"]
    description = request.form["description"]
    location = request.form["location"]
    phone = request.form["phone"]

    image = request.files.get("image")

    filename = ""

    if image and image.filename != "":
        filename = str(int(time.time())) + "_" + secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    sql = """
    INSERT INTO found_items
    (item_name, category, description,
     location, phone, image)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    values = (
        item_name,
        category,
        description,
        location,
        phone,
        filename
    )

    cursor.execute(sql, values)
    print("Filename =", filename)
    db.commit()

    return "Found Item Saved Successfully!"
@app.route("/match")
def match():
    print(match)

    cursor.execute("""
        SELECT item_name,
               phone,
               location,
               image
        FROM lost_items
    """)
    lost_items = cursor.fetchall()

    cursor.execute("""
        SELECT item_name,
               phone,
               location,
               image
        FROM found_items
    """)
    found_items = cursor.fetchall()

    matches = []

    for lost in lost_items:

        for found in found_items:

            score = fuzz.partial_ratio(
                lost[0].lower(),
                found[0].lower()
            )

            if score > 30:

                matches.append(
                    (
                        lost[0],   # Lost Item
                        found[0],  # Found Item
                        score,     # Match Score

                        lost[1],   # Lost Phone
                        found[1],  # Found Phone

                        lost[2],   # Lost Location
                        found[2],
                        
                        lost[3],
                        found[3]   # Found Location
                    )
                )

    return render_template(
        "match.html",
        matches=matches
    )
@app.route("/search_item")
def search_item():

    keyword = request.args.get("keyword")

    sql = """
    SELECT *
    FROM lost_items
    WHERE item_name LIKE %s
    """

    cursor.execute(
        sql,
        ("%" + keyword + "%",)
    )

    results = cursor.fetchall()

    return render_template(
        "search.html",
        results=results
    )
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        roll_no = request.form["roll_no"]
        email = request.form["email"]
        password = request.form["password"]

        sql = """
        INSERT INTO users
        (username,roll_no,email,password)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(
            sql,
            (username,roll_no,email,password)
        )

        db.commit()

        return redirect("/login")

    return render_template(
        "register.html"
    )
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        roll_no = request.form["roll_no"]
        password = request.form["password"]

        sql = """
        SELECT *
        FROM users
        WHERE roll_no=%s
        AND password=%s
        """

        cursor.execute(
            sql,
            (roll_no,password)
        )
        user = cursor.fetchone()

        cursor.fetchall()


        if user:
            session["username"] = user[1]
            return redirect("/home")
        return "INVALID ROLL_NO OR PASSWORD "

    return render_template(
        "login.html"
    )
@app.route("/logout")
def logout():

    session.pop(
        "username",
        None
    )

    return redirect("/login")
@app.route("/admin")
def admin():

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )
    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM lost_items"
    )
    total_lost = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM found_items"
    )
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lost_items")
    total_lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM found_items")
    total_found = cursor.fetchone()[0]
    return render_template(
        "admin.html",
        total_users=total_users,
        total_lost=total_lost,
        total_found=total_found
    )
     
   
    
if __name__ == "__main__":
    app.run(debug=True)