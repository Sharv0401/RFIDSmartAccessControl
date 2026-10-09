from flask import Flask, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

DATABASE = "rfid_system.db"

app.secret_key = "rfid_access_control_secret"


def get_database():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if "username" in session:
        return redirect(url_for("dashboard"))

    error = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["username"] = username

            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>RFID Login</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;

                font-family: Arial, sans-serif;

                background: #f4f6f8;

                display: flex;

                justify-content: center;

                align-items: center;

                min-height: 100vh;
            }}

            .login-box {{
                background: white;

                width: 90%;

                max-width: 400px;

                padding: 35px;

                border-radius: 12px;

                box-shadow:
                    0 4px 15px rgba(0,0,0,0.1);
            }}

            h1 {{
                text-align: center;

                font-size: 24px;

                margin-bottom: 10px;
            }}

            .subtitle {{
                text-align: center;

                color: #666;

                margin-bottom: 25px;
            }}

            label {{
                font-weight: bold;
            }}

            input {{
                width: 100%;

                padding: 12px;

                margin-top: 6px;

                margin-bottom: 18px;

                border: 1px solid #ccc;

                border-radius: 6px;
            }}

            button {{
                width: 100%;

                padding: 12px;

                border: none;

                border-radius: 6px;

                background: #2563eb;

                color: white;

                font-size: 16px;

                cursor: pointer;
            }}

            button:hover {{
                background: #1d4ed8;
            }}

            .error {{
                color: red;

                text-align: center;
            }}

        </style>

    </head>


    <body>

        <div class="login-box">

            <h1>
                🔐 RFID Access Control
            </h1>

            <p class="subtitle">
                System Login
            </p>

            <p class="error">
                {error}
            </p>

            <form method="POST">

                <label>
                    Username
                </label>

                <input
                    type="text"
                    name="username"
                    required
                >

                <label>
                    Password
                </label>

                <input
                    type="password"
                    name="password"
                    required
                >

                <button type="submit">
                    Login
                </button>

            </form>

        </div>

    </body>

    </html>
    """


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect(url_for("login"))

    conn = get_database()


    cards = conn.execute("""
        SELECT id, uid, name, status
        FROM registered_cards
        ORDER BY id DESC
    """).fetchall()


    logs = conn.execute("""
        SELECT uid, name, result, timestamp
        FROM access_logs
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()


    total_cards = conn.execute("""
        SELECT COUNT(*) AS count
        FROM registered_cards
    """).fetchone()["count"]


    granted = conn.execute("""
        SELECT COUNT(*) AS count
        FROM access_logs
        WHERE result = 'GRANTED'
    """).fetchone()["count"]


    denied = conn.execute("""
        SELECT COUNT(*) AS count
        FROM access_logs
        WHERE result = 'DENIED'
    """).fetchone()["count"]


    conn.close()


    # ========================================================
    # CARD TABLE
    # ========================================================

    card_rows = ""

    for card in cards:

        if card["status"] == "ACTIVE":

            status_class = "status-active"

            action = f"""
            <a
                class="action deactivate"
                href="/deactivate/{card['id']}"
                onclick="return confirm('Deactivate this card?')"
            >
                Deactivate
            </a>
            """

        else:

            status_class = "status-inactive"

            action = f"""
            <a
                class="action activate"
                href="/activate/{card['id']}"
                onclick="return confirm('Activate this card?')"
            >
                Activate
            </a>
            """


        card_rows += f"""
        <tr>

            <td>
                {card['uid']}
            </td>

            <td>
                {card['name']}
            </td>

            <td class="{status_class}">
                {card['status']}
            </td>

            <td>

                {action}

                <a
                    class="action delete"
                    href="/delete_card/{card['id']}"
                    onclick="return confirm('Delete this card permanently?')"
                >
                    Delete
                </a>

            </td>

        </tr>
        """


    # ========================================================
    # ACCESS LOG TABLE
    # ========================================================

    log_rows = ""

    for log in logs:

        if log["result"] == "GRANTED":

            result_class = "result-granted"

        else:

            result_class = "result-denied"


        log_rows += f"""
        <tr>

            <td>
                {log['uid']}
            </td>

            <td>
                {log['name']}
            </td>

            <td class="{result_class}">
                {log['result']}
            </td>

            <td>
                {log['timestamp']}
            </td>

        </tr>
        """


    # ========================================================
    # DASHBOARD HTML
    # ========================================================

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>RFID Dashboard</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <meta http-equiv="Cache-Control"
              content="no-cache, no-store, must-revalidate">

        <meta http-equiv="Pragma"
              content="no-cache">

        <meta http-equiv="Expires"
              content="0">


        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>


        <style>

            * {{
                box-sizing: border-box;
            }}


            body {{
                margin: 0;

                font-family: Arial, sans-serif;

                background: #f4f6f8;

                color: #222;
            }}


            /* HEADER */

            .header {{
                background: #111827;

                color: white;

                padding: 20px;
            }}


            .header-content {{
                max-width: 1200px;

                margin: auto;

                display: flex;

                justify-content: space-between;

                align-items: center;

                gap: 15px;
            }}


            .header h1 {{
                margin: 0;

                font-size: 24px;
            }}


            .logout {{
                color: white;

                text-decoration: none;

                background: #dc2626;

                padding: 9px 15px;

                border-radius: 6px;
            }}


            .logout:hover {{
                background: #b91c1c;
            }}


            /* MAIN */

            .container {{
                max-width: 1200px;

                margin: auto;

                padding: 25px;
            }}


            .welcome {{
                margin-bottom: 20px;
            }}


            /* STATISTICS */

            .stats {{
                display: grid;

                grid-template-columns:
                    repeat(3, 1fr);

                gap: 20px;

                margin-bottom: 30px;
            }}


            .card {{
                background: white;

                padding: 25px;

                border-radius: 10px;

                box-shadow:
                    0 3px 10px rgba(0,0,0,0.08);
            }}


            .stat-title {{
                color: #666;

                font-size: 15px;
            }}


            .stat-number {{
                font-size: 35px;

                font-weight: bold;

                margin-top: 10px;
            }}


            .green {{
                color: #16a34a;
            }}


            .red {{
                color: #dc2626;
            }}


            .blue {{
                color: #2563eb;
            }}


            /* REFRESH */

            .refresh-info {{
                background: white;

                padding: 12px 15px;

                border-radius: 8px;

                margin-bottom: 20px;

                color: #555;

                font-size: 14px;

                box-shadow:
                    0 2px 6px rgba(0,0,0,0.05);
            }}


            /* REGISTER CARD */

            .register-box {{
                background: white;

                padding: 25px;

                border-radius: 10px;

                box-shadow:
                    0 3px 10px rgba(0,0,0,0.08);

                margin-bottom: 30px;
            }}


            .register-form {{
                display: grid;

                grid-template-columns:
                    1fr 1fr auto;

                gap: 10px;

                align-items: end;
            }}


            .form-group label {{
                display: block;

                font-weight: bold;

                margin-bottom: 6px;
            }}


            .form-group input {{
                width: 100%;

                padding: 11px;

                border: 1px solid #ccc;

                border-radius: 6px;
            }}


            .register-button {{
                padding: 11px 20px;

                border: none;

                border-radius: 6px;

                background: #2563eb;

                color: white;

                font-size: 15px;

                cursor: pointer;
            }}


            .register-button:hover {{
                background: #1d4ed8;
            }}


            /* CHART */

            .chart-container {{
                background: white;

                padding: 25px;

                border-radius: 10px;

                box-shadow:
                    0 3px 10px rgba(0,0,0,0.08);

                max-width: 650px;

                margin-bottom: 30px;
            }}


            .chart-box {{
                position: relative;

                height: 350px;
            }}


            /* TABLE */

            h2 {{
                margin-top: 30px;
            }}


            .table-container {{
                background: white;

                padding: 20px;

                border-radius: 10px;

                overflow-x: auto;

                box-shadow:
                    0 3px 10px rgba(0,0,0,0.08);
            }}


            table {{
                width: 100%;

                border-collapse: collapse;

                min-width: 700px;
            }}


            th,
            td {{
                padding: 12px;

                text-align: left;

                border-bottom: 1px solid #ddd;
            }}


            th {{
                background: #f1f5f9;
            }}


            .status-active {{
                color: #16a34a;

                font-weight: bold;
            }}


            .status-inactive {{
                color: #dc2626;

                font-weight: bold;
            }}


            .result-granted {{
                color: #16a34a;

                font-weight: bold;
            }}


            .result-denied {{
                color: #dc2626;

                font-weight: bold;
            }}


            /* ACTION BUTTONS */

            .action {{
                display: inline-block;

                padding: 6px 10px;

                margin-right: 5px;

                border-radius: 5px;

                text-decoration: none;

                font-size: 13px;

                color: white;
            }}


            .activate {{
                background: #16a34a;
            }}


            .deactivate {{
                background: #f59e0b;
            }}


            .delete {{
                background: #dc2626;
            }}


            /* MOBILE */

            @media (max-width: 700px) {{

                .header-content {{
                    flex-direction: column;

                    align-items: flex-start;
                }}


                .stats {{
                    grid-template-columns: 1fr;
                }}


                .container {{
                    padding: 15px;
                }}


                .header h1 {{
                    font-size: 20px;
                }}


                .register-form {{
                    grid-template-columns: 1fr;
                }}


                .chart-container {{
                    padding: 15px;
                }}


                .chart-box {{
                    height: 300px;
                }}

            }}

        </style>

    </head>


    <body>


        <!-- HEADER -->

        <div class="header">

            <div class="header-content">

                <h1>
                    🔐 RFID Access Control System
                </h1>

                <a
                    class="logout"
                    href="/logout"
                >
                    Logout
                </a>

            </div>

        </div>


        <div class="container">


            <!-- WELCOME -->

            <div class="welcome">

                <h2>
                    Dashboard
                </h2>

                <p>
                    Welcome,
                    <strong>{session["username"]}</strong>.
                    Monitor RFID access activity below.
                </p>

            </div>


            <!-- AUTO REFRESH -->

            <div class="refresh-info">

                🔄 Dashboard automatically refreshes
                every <strong>5 seconds</strong>.

            </div>


            <!-- STATISTICS -->

            <div class="stats">


                <div class="card">

                    <div class="stat-title">
                        Registered Cards
                    </div>

                    <div class="stat-number blue">
                        {total_cards}
                    </div>

                </div>


                <div class="card">

                    <div class="stat-title">
                        Access Granted
                    </div>

                    <div class="stat-number green">
                        {granted}
                    </div>

                </div>


                <div class="card">

                    <div class="stat-title">
                        Access Denied
                    </div>

                    <div class="stat-number red">
                        {denied}
                    </div>

                </div>


            </div>


            <!-- REGISTER CARD -->

            <h2>
                Register New RFID Card
            </h2>


            <div class="register-box">

                <form
                    class="register-form"
                    method="POST"
                    action="/register_card"
                >


                    <div class="form-group">

                        <label>
                            RFID UID
                        </label>

                        <input
                            type="text"
                            name="uid"
                            placeholder="Enter RFID UID"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Name
                        </label>

                        <input
                            type="text"
                            name="name"
                            placeholder="Enter person's name"
                            required
                        >

                    </div>


                    <button
                        class="register-button"
                        type="submit"
                    >
                        ➕ Register Card
                    </button>


                </form>

            </div>


            <!-- CHART -->

            <h2>
                Access Activity
            </h2>


            <div class="chart-container">

                <div class="chart-box">

                    <canvas id="accessChart"></canvas>

                </div>

            </div>


            <!-- REGISTERED CARDS -->

            <h2>
                Registered RFID Cards
            </h2>


            <div class="table-container">

                <table>

                    <tr>

                        <th>
                            UID
                        </th>

                        <th>
                            Name
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Actions
                        </th>

                    </tr>

                    {card_rows}

                </table>

            </div>


            <!-- ACCESS LOGS -->

            <h2>
                Recent Access Logs
            </h2>


            <div class="table-container">

                <table>

                    <tr>

                        <th>
                            UID
                        </th>

                        <th>
                            Name
                        </th>

                        <th>
                            Result
                        </th>

                        <th>
                            Timestamp
                        </th>

                    </tr>

                    {log_rows}

                </table>

            </div>


        </div>


        <!-- CHART -->

        <script>

            const ctx =
                document.getElementById(
                    "accessChart"
                );


            new Chart(ctx, {{

                type: "doughnut",


                data: {{

                    labels: [
                        "Granted",
                        "Denied"
                    ],


                    datasets: [{{

                        data: [
                            {granted},
                            {denied}
                        ],


                        backgroundColor: [
                            "#16a34a",
                            "#dc2626"
                        ],


                        borderWidth: 1

                    }}]

                }},


                options: {{

                    responsive: true,

                    maintainAspectRatio: false,


                    plugins: {{

                        legend: {{

                            position: "bottom"

                        }},


                        title: {{

                            display: true,

                            text:
                                "RFID Access Results"

                        }}

                    }}

                }}

            }});


            // Auto refresh every 5 seconds

           setTimeout(function() {{

           window.location.reload();

           }}, 5000);

        </script>


    </body>

    </html>
    """


    return html


# ============================================================
# REGISTER NEW CARD
# ============================================================

@app.route("/register_card", methods=["POST"])
def register_card():

    if "username" not in session:

        return redirect(url_for("login"))


    uid = request.form["uid"].strip()

    name = request.form["name"].strip()


    if uid == "" or name == "":

        return redirect(url_for("dashboard"))


    conn = get_database()


    try:

        conn.execute("""
            INSERT INTO registered_cards
            (uid, name, status)
            VALUES (?, ?, 'ACTIVE')
        """, (uid, name))

        conn.commit()

    except sqlite3.IntegrityError:

        pass


    conn.close()


    return redirect(url_for("dashboard"))


# ============================================================
# ACTIVATE CARD
# ============================================================

@app.route("/activate/<int:card_id>")
def activate_card(card_id):

    if "username" not in session:

        return redirect(url_for("login"))


    conn = get_database()


    conn.execute("""
        UPDATE registered_cards
        SET status = 'ACTIVE'
        WHERE id = ?
    """, (card_id,))


    conn.commit()

    conn.close()


    return redirect(url_for("dashboard"))


# ============================================================
# DEACTIVATE CARD
# ============================================================

@app.route("/deactivate/<int:card_id>")
def deactivate_card(card_id):

    if "username" not in session:

        return redirect(url_for("login"))


    conn = get_database()


    conn.execute("""
        UPDATE registered_cards
        SET status = 'INACTIVE'
        WHERE id = ?
    """, (card_id,))


    conn.commit()

    conn.close()


    return redirect(url_for("dashboard"))


# ============================================================
# DELETE CARD
# ============================================================

@app.route("/delete_card/<int:card_id>")
def delete_card(card_id):

    if "username" not in session:

        return redirect(url_for("login"))


    conn = get_database()


    conn.execute("""
        DELETE FROM registered_cards
        WHERE id = ?
    """, (card_id,))


    conn.commit()

    conn.close()


    return redirect(url_for("dashboard"))


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()


    response = redirect(
        url_for("login")
    )


    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"


    return response


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
