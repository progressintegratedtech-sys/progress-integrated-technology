from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = "progress_technology_secret_key"


# ==========================
# DATABASE SETUP
# ==========================

def init_db():

    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT,

        subject TEXT,

        message TEXT,

        created_at TEXT

    )
    """)

    conn.commit()
    conn.close()


init_db()


# ==========================
# HOME
# ==========================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================
# CONTACT
# ==========================

@app.route("/contact", methods=["POST"])
def contact():

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    created_at = datetime.now().strftime("%d %b %Y, %I:%M %p")


    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO messages
    (name,email,subject,message,created_at,status)

    VALUES (?,?,?,?,?,?)

    """,
    (name,email,subject,message,created_at,"new"))


    conn.commit()
    conn.close()


    return render_template("success.html")


# ==========================
# ADMIN LOGIN
# ==========================

@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        if username == "admin" and password == "progress123":

            session["admin"] = True

            return redirect(url_for("admin"))


        else:

            return "Invalid username or password"


    return render_template("admin_login.html")



# ==========================
# ADMIN DASHBOARD + SEARCH
# ==========================

@app.route("/admin")
def admin():

    if "admin" not in session:

        return redirect(url_for("admin_login"))


    search = request.args.get("search","")


    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()


    if search:

        cursor.execute("""
        SELECT * FROM messages

        WHERE name LIKE ?

        OR email LIKE ?

        OR subject LIKE ?

        OR message LIKE ?

        ORDER BY id DESC

        """,
        (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))


    else:

        cursor.execute("""
        SELECT * FROM messages
        ORDER BY id DESC
        """)


    messages = cursor.fetchall()


    cursor.execute("SELECT COUNT(*) FROM messages")

    total_messages = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "admin.html",
        messages=messages,
        total_messages=total_messages,
        search=search
    )



# ==========================
# DELETE MESSAGE
# ==========================

@app.route("/delete-message/<int:message_id>")
def delete_message(message_id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))


    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()


    cursor.execute(
        "DELETE FROM messages WHERE id=?",
        (message_id,)
    )


    conn.commit()
    conn.close()


    return redirect(url_for("admin"))


# ==========================
# MARK MESSAGE AS READ
# ==========================

@app.route("/mark-read/<int:message_id>")
def mark_read(message_id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))


    conn = sqlite3.connect("messages.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE messages
        SET status = 'read'
        WHERE id = ?
        """,
        (message_id,)
    )


    conn.commit()

    conn.close()


    return redirect(url_for("admin"))

# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.pop("admin",None)

    return redirect(url_for("admin_login"))



# ==========================
# RUN
# ==========================

if __name__ == "__main__":

    app.run(debug=True, port=5001)