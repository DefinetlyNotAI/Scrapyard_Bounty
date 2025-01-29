import os
import tempfile
import time
from functools import wraps

import psycopg2
import requests
from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify, make_response, abort
from flask import send_from_directory
from psycopg2 import sql
from psycopg2._psycopg import DatabaseError
from scapy.all import rdpcap
from waitress import serve
from werkzeug.security import check_password_hash, generate_password_hash

# ------------------------ FLASK APP ------------------------- #

# Flask app instance
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

START_TIME = time.time()

# ------------------ ENVIRONMENT VARIABLES -------------------- #

# Flags and awards
FLAG_1 = os.getenv("FLAG_1", "ERR")
FLAG_1_SCORE = 50
FLAG_2 = os.getenv("FLAG_2", "ERR")
FLAG_2_SCORE = 75
FLAG_3 = os.getenv("FLAG_3", "ERR")
FLAG_3_SCORE = 125
FLAG_4 = os.getenv("FLAG_4", "ERR")
FLAG_4_SCORE = 150
FLAG_5 = os.getenv("FLAG_5", "ERR")
FLAG_5_SCORE = 100

# Key variable
KEY = os.getenv("KEY", "ERR")

if "ERR" in [FLAG_1, FLAG_2, FLAG_3, FLAG_4, FLAG_5, KEY]:
    print("404: Env variable are not fully set, some are running on default - Continuing")


# ------------------------- DATABASE ------------------------- #

# Database connection
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DB_URL_AIVEN"), dbname=os.getenv("DB_NAME"))
    return conn


# Decorator to check if the user is an admin
def admin_required(param: callable):
    def wrap(*args, **kwargs):
        if 'team_name' not in session:
            print("User not signed in, redirecting now")
            return redirect(url_for('signin'))
        if session['team_name'] != 'ADMIN':
            abort(403,
                  description=jsonify({"error": f"Insufficient Permissions, User {session['team_name']} is not admin"}))
        return param(*args, **kwargs)

    wrap.__name__ = param.__name__
    return wrap


# Decorator to rate limit the user - Advised not to use with @admin_required
def rate_limit(limit: int, time_window: int = 3600):
    # Create an independent store for each decorator instance
    request_store = {}

    def decorator(func):
        @wraps(func)  # Preserve the original function metadata
        def wrapper(*args, **kwargs):
            user_ip = request.remote_addr
            current_time = time.time()

            # Ensure user IP is in the request store
            if user_ip not in request_store:
                request_store[user_ip] = []

            timestamps = request_store[user_ip]
            valid_timestamps = [ts for ts in timestamps if current_time - ts <= time_window]
            request_store[user_ip] = valid_timestamps

            if len(valid_timestamps) >= limit:
                abort(429, description=jsonify({"error": "Rate limit exceeded. Try again later."}))

            request_store[user_ip].append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# --------------------------- APIs ---------------------------- #
# ------------------------ Standalone --------------------------#
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({"status": True}), 200
    except Exception:
        return jsonify({"status": False}), 200


@app.route('/api/executeQuery', methods=['POST'])
@admin_required
def execute_query():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = {"message": "Query executed successfully"}
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception:
        return jsonify({"error": "Query Execution Failed"}), 500


@app.route('/api/status', methods=['GET'])
def api_status():
    uptime = round(time.time() - START_TIME, 2)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_status = True
    except Exception:
        db_status = False

    return jsonify({
        "status": "API is running",
        "uptime_seconds": uptime,
        "database_connected": db_status
    }), 200


@app.route('/api/download/<challenge_id>', methods=['GET'])
@rate_limit(limit=5)
def download_challenge_files(challenge_id: str):
    # Ensure the challenge_id is valid (you can expand this with your own validation logic)
    if challenge_id not in ["bin", "images", "pcap"]:
        return jsonify({"error": "Invalid challenge zip, available ['bin', 'images', 'pcap']"}), 404

    # Assuming challenge files are stored in a directory called 'challenge'
    challenge_file_path = f"src/assets/{challenge_id}.zip"

    if os.path.exists(challenge_file_path):
        return send_from_directory('src/assets', f"{challenge_id}.zip", as_attachment=True), 200
    else:
        return jsonify({"error": "Challenge files not found"}), 404


# --------------------------- GET ------------------------------#
@app.route('/api/get/size', methods=['GET'])
def get_db_size():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database())) AS size")
    size = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"size": size}), 200


@app.route('/api/get/activeConnections', methods=['GET'])
@rate_limit(limit=60)
def get_active_connections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid <> pg_backend_pid()")
    active_connections = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"activeConnections": active_connections}), 200


@app.route('/api/get/allTeams', methods=['GET'])
@rate_limit(limit=60)
def view_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, team_name, score FROM teams')
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(teams), 200


@app.route('/api/get/challengesProgress', methods=['GET'])
@rate_limit(limit=50)
def get_challenge_progress():
    if 'team_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    team_name = session['team_name']

    try:
        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT challenge_id, flag_submitted, score
            FROM challenge_progress
            WHERE team_name = %s
        """, (team_name,))

        progress = cursor.fetchall()

        if not progress:
            return jsonify({"message": "No progress found for the team"}), 404

        progress_data = [
            {
                "challenge_id": challenge_id,
                "flag_submitted": flag_submitted,
                "score": score
            }
            for challenge_id, flag_submitted, score in progress
        ]

        return jsonify(progress_data), 200

    except DatabaseError:
        return jsonify({"error": "Database error", "details": "THIS FEATURE IS DEPRECATED DUE TO SECURITY REASONS"}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/get/leaderboard', methods=['GET'])
@rate_limit(limit=30)
def get_leaderboard():
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = int(request.args.get('per_page', 10))  # Default to 10 teams per page

    # Calculate offset for pagination
    offset = (page - 1) * per_page

    # Fetch leaderboard data from the database
    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT team_name, score 
        FROM teams
        ORDER BY score DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    leaderboard_local = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{"team_name": team_name, "score": score} for team_name, score in leaderboard_local]), 200


# ------------------------ GET/Tables --------------------------#
@app.route('/api/get/tables', methods=['GET'])
@admin_required
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'pg_%'
        AND table_name NOT LIKE 'sql_%'
    """)
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([table[0] for table in tables]), 200


@app.route('/api/get/tables/<table_name>', methods=['GET'])
@admin_required
def get_table_rows(table_name: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = sql.SQL("SELECT * FROM {} LIMIT 100").format(sql.Identifier(table_name))
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception:
        return jsonify({"error": "Getting the table rows failed"}), 500


@app.route('/api/get/tables/<table_name>/schema', methods=['GET'])
@admin_required
def get_table_schema(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
    """, (table_name,))
    schema = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(schema), 200


# ------------------------- DELETE ----------------------------#

@app.route('/api/delete/tables/<table_name>/<int:row_id>', methods=['DELETE'])
@admin_required
def delete_table_item(table_name: str, row_id: int):
    try:
        conn = get_db_connection()

        cursor = conn.cursor()
        query = f"DELETE FROM %s WHERE id = %s"
        cursor.execute(query, (table_name, row_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Item deleted successfully."}), 200
    except Exception:
        return jsonify({"error": "Deleting the table item failed"}), 500


@app.route('/api/delete/tables/<table_name>', methods=['DELETE'])
@admin_required
def delete_table(table_name: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Table deleted successfully."}), 200
    except Exception:
        return jsonify({"error": "Deleting the table failed"}), 500


@app.route('/api/delete/database', methods=['POST'])
@admin_required
def delete_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS teams")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Database deleted successfully."}), 200


# ------------------------ GET/User ---------------------------#
@app.route('/api/get/user/profile', methods=['GET'])
@rate_limit(limit=100)
def get_user_profile():
    if 'team_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    team_name = session['team_name']

    # Fetch user profile data from the database
    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute('SELECT team_name, score, flags_submitted FROM teams WHERE team_name = %s', (team_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        team_name, score, flags_submitted = result
        return jsonify({
            "team_name": team_name,
            "score": score,
            "flags_submitted": flags_submitted.split(',')
        }), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/get/user/rank', methods=['GET'])
@rate_limit(limit=20)
def get_team_rank():
    if 'team_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    team_name = session['team_name']

    # Fetch the team's score and rank from the database
    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT team_name, score 
        FROM teams 
        ORDER BY score DESC
    """)
    teams = cursor.fetchall()
    cursor.close()
    conn.close()

    # Calculate the rank of the logged-in team
    rank = next((i + 1 for i, (name, score) in enumerate(teams) if name == team_name), None)

    if rank:
        # Find the score of the next team to compare
        next_team_score = teams[rank] if rank < len(teams) else None
        return jsonify({"rank": rank, "next_team_score": next_team_score}), 200
    else:
        return jsonify({"error": "Team not found"}), 404


@app.route('/api/get/user/history', methods=['GET'])
@rate_limit(limit=50)
def get_team_history():
    if 'team_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    team_name = session['team_name']

    try:
        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, flags_submitted, score 
            FROM team_history
            WHERE team_name = %s
            ORDER BY timestamp DESC
        """, (team_name,))

        history = cursor.fetchall()

        if not history:
            return jsonify({"message": "No history found for the team"}), 404

        history_data = [
            {
                "timestamp": timestamp,
                "flags_submitted": flags_submitted.split(",") if flags_submitted else [],
                "score": score
            }
            for timestamp, flags_submitted, score in history
        ]

        return jsonify(history_data), 200

    except DatabaseError:
        return jsonify({"error": "Database error", "details": "THIS FEATURE IS DEPRECATED DUE TO SECURITY REASONS"}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/get/user/submissions', methods=['GET'])
@rate_limit(limit=100)
def get_submission_history():
    if 'team_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    team_name = session['team_name']

    try:
        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT flag, timestamp 
            FROM flag_submissions
            WHERE team_name = %s
            ORDER BY timestamp DESC
        """, (team_name,))

        submissions = cursor.fetchall()

        if not submissions:
            return jsonify({"message": "No submissions found for the team"}), 404

        submission_data = [
            {"flag": flag, "timestamp": timestamp}
            for flag, timestamp in submissions
        ]

        return jsonify(submission_data), 200

    except DatabaseError:
        return jsonify({"error": "Database error", "details": "THIS FEATURE IS DEPRECATED DUE TO SECURITY REASONS"}), 500

    finally:
        cursor.close()
        conn.close()


# ------------------------ END APIs ------------------------- #

# ------------------------ RESOURCES ------------------------ #


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon'), 200


@app.route('/retry/<url_to_check>', methods=['POST'])
@rate_limit(limit=60)
def retry(url_to_check: str):
    try:
        response = requests.get(url_to_check)
        if response.status_code == 200:
            return jsonify({"message": "Retry successful"}), 200
    except requests.RequestException:
        return jsonify({"message": "Retry failed after attempt."}), 500


# ---------------------- ERROR HANDLERS --------------------- #


# noinspection PyUnusedLocal
@app.errorhandler(403)
def forbidden(e):
    return render_template_string(ERROR_403_TEMPLATE), 403


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e):
    return render_template_string(ERROR_404_TEMPLATE), 404


# noinspection PyUnusedLocal
@app.errorhandler(429)
def too_many_requests(e):
    return render_template_string(ERROR_429_TEMPLATE), 429


# noinspection PyUnusedLocal
@app.errorhandler(500)
def internal_server_error(e):
    return render_template_string(ERROR_500_TEMPLATE), 500


# -------------------------- PAGES -------------------------- #

@app.route('/')
def home():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    if 'start_time' not in session:
        session['start_time'] = time.time()
    return render_template_string(HOME_TEMPLATE), 200


@app.route('/admin')
@admin_required
def admin():
    return render_template_string(ADMIN_TEMPLATE), 200


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        if not team_name or not password:
            return render_template_string(SIGNIN_TEMPLATE, error="Team name and password are required."), 400

        conn = get_db_connection()

        cursor = conn.cursor()
        cursor.execute('SELECT password, ip_address FROM teams WHERE team_name = %s', (team_name,))
        result = cursor.fetchone()

        if result:
            stored_password, stored_ip = result
            if check_password_hash(stored_password, password):
                if stored_ip and stored_ip != request.remote_addr and team_name != 'ADMIN':
                    return render_template_string(SIGNIN_TEMPLATE,
                                                  error="Account is already in use from another device, only 1 account per device (Uses IP tracking) - To fix, please contact ADMIN"), 409
                session['team_name'] = team_name
                cursor.execute('UPDATE teams SET ip_address = %s WHERE team_name = %s',
                               (request.remote_addr, team_name))
            else:
                return render_template_string(SIGNIN_TEMPLATE, error="Invalid password."), 401
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO teams (team_name, password, ip_address, flags_submitted) VALUES (%s, %s, %s, %s)',
                (team_name, hashed_password, request.remote_addr, ''))
            session['team_name'] = team_name

        conn.commit()
        cursor.close()
        conn.close()

        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('team_name', team_name, secure=True, samesite='Strict')
        return resp
    return render_template_string(SIGNIN_TEMPLATE), 200


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    points = 0
    if request.method == 'POST':
        flag = request.form.get('flag')
        team_name = session.get('team_name')
        if not team_name:
            return redirect(url_for('signin'))

        if flag in [FLAG_1, FLAG_2, FLAG_3, FLAG_4, FLAG_5]:
            flag_scores = {
                FLAG_1: FLAG_1_SCORE,
                FLAG_2: FLAG_2_SCORE,
                FLAG_3: FLAG_3_SCORE,
                FLAG_4: FLAG_4_SCORE,
                FLAG_5: FLAG_5_SCORE
            }
            points = round(flag_scores[flag], 2)

        conn = get_db_connection()

        cursor = conn.cursor()
        cursor.execute('SELECT flags_submitted FROM teams WHERE team_name = %s', (team_name,))
        result = cursor.fetchone()
        flags_submitted = result[0].split(',') if result else []

        if flag in flags_submitted:
            return render_template_string(SUBMIT_TEMPLATE, error="Flag already submitted."), 406

        if flag in [FLAG_1, FLAG_2, FLAG_3, FLAG_4, FLAG_5]:
            flags_submitted.append(flag)
            cursor.execute('UPDATE teams SET score = score + %s, flags_submitted = %s WHERE team_name = %s',
                           (round(points, 2), ','.join(flags_submitted), team_name))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template_string(SUBMIT_TEMPLATE, success=True, points=round(points, 2)), 200
        else:
            return render_template_string(SUBMIT_TEMPLATE, error="Invalid flag."), 400
    return render_template_string(SUBMIT_TEMPLATE), 200


@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT team_name, score FROM teams ORDER BY score DESC')
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(LEADERBOARD_TEMPLATE, teams=teams), 200


# ------------------------ CHALLENGES ------------------------ #


# Challenge 1: Cryptography
@app.route('/cryptography', methods=['GET', 'POST'])
def cryptography():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    description = "Decrypt a ROT13-encrypted message to uncover the flag."
    encrypted_message = "GUVF_VF_GUR_SYNT"

    if request.method == 'POST':
        user_input = request.form.get('decrypted')
        if user_input == "THIS_IS_THE_FLAG":
            return render_template_string(COMP_TEMPLATE, challenge=1, success=True, flag=FLAG_1,
                                          description=description, encrypted=encrypted_message), 200
        else:
            return render_template_string(COMP_TEMPLATE, challenge=1, error="Incorrect decryption.",
                                          description=description, encrypted=encrypted_message), 400

    return render_template_string(COMP_TEMPLATE, challenge=1, description=description, encrypted=encrypted_message), 200


# Challenge 2: Web Exploitation
@app.route('/weblogin', methods=['GET', 'POST'])
def weblogin():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    description = "Bypass the login page using SQL Injection to discover the flag."
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return render_template_string(COMP_TEMPLATE, challenge=2, success=True, flag=FLAG_2,
                                          description=description), 200
        else:
            return render_template_string(COMP_TEMPLATE, challenge=2, error="Invalid credentials.",
                                          description=description), 400

    return render_template_string(COMP_TEMPLATE, challenge=2, description=description), 200


# Challenge 3: Reverse Engineering
@app.route('/binary', methods=['GET', 'POST'])
def binary():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    description = "Analyze a binary file to find a hardcoded key (Format KEY{xxxx}). First you must find the correct BIN file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if not uploaded_file:
            return render_template_string(COMP_TEMPLATE, challenge=3,
                                          error="No file uploaded",
                                          description=description), 400
        if not uploaded_file.filename.endswith('.bin'):
            return render_template_string(COMP_TEMPLATE, challenge=3,
                                          error="Invalid file type",
                                          description=description), 400
        binary_data = uploaded_file.read()
        if KEY.encode() in binary_data and request.form.get('line', '') == '136':  # File C3_79.bin
            return render_template_string(COMP_TEMPLATE, challenge=3, success=True, flag=FLAG_3,
                                          description=description), 200
        else:
            return render_template_string(COMP_TEMPLATE, challenge=3,
                                          error="Flag not found in the binary or Line number incorrect.",
                                          description=description), 400

    return render_template_string(COMP_TEMPLATE, challenge=3, description=description), 200


# Challenge 4: Forensics
@app.route('/forensics', methods=['GET', 'POST'])
def forensics():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    description = "Analyze a PCAP file in [Wireshark] to find a hidden key (Format KEY{xxxx}). First you must find the correct PCAP file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if not uploaded_file:
            return render_template_string(COMP_TEMPLATE, challenge=4,
                                          error="No file uploaded",
                                          description=description), 400

        if not uploaded_file.filename.endswith('.pcap'):
            return render_template_string(COMP_TEMPLATE, challenge=4,
                                          error="Invalid file type",
                                          description=description), 400

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
        finally:
            packets = rdpcap(temp_file_path)
            os.remove(temp_file_path)  # Clean up the temporary file

        for packet in packets:
            if (packet.haslayer('Raw') and KEY in packet['Raw'].load.decode(
                    'utf-8', errors='ignore')
                    and request.form.get('line', '') == '452'):  # File C4_68.pcap
                return render_template_string(COMP_TEMPLATE, challenge=4, success=True, flag=FLAG_4,
                                              description=description), 200
        return render_template_string(COMP_TEMPLATE, challenge=4,
                                      error="Flag not found in PCAP or Line number incorrect.",
                                      description=description), 400

    return render_template_string(COMP_TEMPLATE, challenge=4, description=description), 200


# Challenge 5: Steganography
@app.route('/steganography', methods=['GET', 'POST'])
def steganography():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    description = "Extract hidden data (Format KEY{xxxx}) from an image file using a automated script. First you must find the correct JPEG file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if not uploaded_file:
            return render_template_string(COMP_TEMPLATE, challenge=5,
                                          error="No file uploaded",
                                          description=description), 400

        if not uploaded_file.filename.endswith('.jpeg'):
            return render_template_string(COMP_TEMPLATE, challenge=5,
                                          error="Invalid file type",
                                          description=description), 400

        try:
            # Read the entire file content
            file_content = uploaded_file.read()
            flag = KEY.encode()
            if flag in file_content and request.form.get('line', '') == '206':  # File C5_51.jpeg
                return render_template_string(COMP_TEMPLATE, challenge=5, success=True, flag=FLAG_5,
                                              description=description), 200
            else:
                return render_template_string(COMP_TEMPLATE, challenge=5,
                                              error="Hidden flag not found or Line number incorrect.",
                                              description=description), 400
        except Exception:
            return render_template_string(COMP_TEMPLATE, challenge=5, error=f"An error occurred. Please try again!",
                                          description=description), 500

    return render_template_string(COMP_TEMPLATE, challenge=5, description=description)


# --------------------------- HTML --------------------------- #

# HTML template for home page
with open("src/html/home.html", "r") as f:
    HOME_TEMPLATE = f.read()

# HTML template for challenges
with open("src/html/competition.html", "r") as f:
    COMP_TEMPLATE = f.read()

# HTML templates for sign-in, submit and leaderboard pages
with open("src/html/signin.html", "r") as f:
    SIGNIN_TEMPLATE = f.read()

with open("src/html/submit.html", "r", encoding="UTF-8") as f:
    SUBMIT_TEMPLATE = f.read()

with open("src/html/leaderboard.html", "r") as f:
    LEADERBOARD_TEMPLATE = f.read()

# HTML template for admin page
with open("src/html/admin.html", "r") as f:
    ADMIN_TEMPLATE = f.read()

# Error templates
with open("src/html/error/403.html", "r") as f:
    ERROR_403_TEMPLATE = f.read()

with open("src/html/error/404.html", "r") as f:
    ERROR_404_TEMPLATE = f.read()

with open("src/html/error/429.html", "r") as f:
    ERROR_429_TEMPLATE = f.read()

with open("src/html/error/500.html", "r") as f:
    ERROR_500_TEMPLATE = f.read()

# ------------------------- MAIN APP ------------------------- #

# Run the app
if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)

# --------------------------- END ---------------------------- #
