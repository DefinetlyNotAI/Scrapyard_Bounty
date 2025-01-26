import os
import tempfile
import time

import psycopg2
from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify, make_response
from flask import send_from_directory
from psycopg2._psycopg import AsIs
from scapy.all import rdpcap
from waitress import serve
from werkzeug.security import check_password_hash, generate_password_hash


# ------------------------ FLASK APP ------------------------- #

# Flask app instance
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# ------------------ ENVIRONMENT VARIABLES -------------------- #

# Flags and awards
FLAG_1 = os.getenv("FLAG_1")
FLAG_1_SCORE = 50
FLAG_2 = os.getenv("FLAG_2")
FLAG_2_SCORE = 75
FLAG_3 = os.getenv("FLAG_3")
FLAG_3_SCORE = 125
FLAG_4 = os.getenv("FLAG_4")
FLAG_4_SCORE = 150
FLAG_5 = os.getenv("FLAG_5")
FLAG_5_SCORE = 100


# ------------------------- DATABASE ------------------------- #

# Database connection
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DB_URL_AIVEN"), dbname=os.getenv("DB_NAME"))
    return conn


# Decorator to check if the user is an admin
def admin_required(param):
    def wrap(*args, **kwargs):
        if 'team_name' not in session or session['team_name'] != 'ADMIN':
            return redirect(url_for('signin'))
        return param(*args, **kwargs)

    wrap.__name__ = param.__name__
    return wrap


# --------------------------- APIs ---------------------------- #

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({"status": True})
    except Exception:
        return jsonify({"status": False})


@app.route('/api/dbsize', methods=['GET'])
@admin_required
def get_db_size():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database())) AS size")
    size = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"size": size})


# noinspection SqlResolve
@app.route('/api/tables', methods=['GET'])
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
    return jsonify([table[0] for table in tables])


@app.route('/api/tables/<table_name>', methods=['GET'])
@admin_required
def get_table_rows(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM %s LIMIT 100", (AsIs(table_name),))  # Use parameterized query
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# noinspection SqlResolve
@app.route('/api/tables/<table_name>/schema', methods=['GET'])
@admin_required
def get_table_schema(table_name):
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
    return jsonify(schema)


@app.route('/api/query', methods=['POST'])
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
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to view teams
# noinspection SqlResolve
@app.route('/api/teams', methods=['GET'])
@admin_required
def view_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, team_name, score FROM teams')
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(teams)


# API endpoint to delete the database
@app.route('/api/delete', methods=['POST'])
@admin_required
def delete_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS teams")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Database deleted successfully."})


# noinspection SqlResolve
@app.route('/api/activeConnections', methods=['GET'])
@admin_required
def get_active_connections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid <> pg_backend_pid()")
    active_connections = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"activeConnections": active_connections})


@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({"status": "API is running"}), 200


@app.route('/api/tables/<table_name>/<int:row_id>', methods=['DELETE'])
@admin_required
def delete_table_item(table_name, row_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = %s"
        cursor.execute(query, (row_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Item deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tables/<table_name>', methods=['DELETE'])
@admin_required
def delete_table(table_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Table deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------- RESOURCES ----------------------- #

# Route to download zip files
@app.route('/src/assets/<filename>')
def download_file(filename):
    return send_from_directory('src/assets', filename, as_attachment=True)


# ------------------------- PAGES ------------------------- #

# Home Route
@app.route('/')
def home():
    if 'team_name' not in session or request.cookies.get('team_name') != session['team_name']:
        return redirect(url_for('signin'))
    if 'start_time' not in session:
        session['start_time'] = time.time()
    return render_template_string(HOME_TEMPLATE)


# Admin route to render the admin page
@app.route('/admin')
@admin_required
def admin():
    return render_template_string(ADMIN_TEMPLATE)


# Sign-in page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        if not team_name or not password:
            return render_template_string(SIGNIN_TEMPLATE, error="Team name and password are required.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password, ip_address FROM teams WHERE team_name = %s', (team_name,))
        result = cursor.fetchone()

        if result:
            stored_password, stored_ip = result
            if check_password_hash(stored_password, password):
                if stored_ip and stored_ip != request.remote_addr:
                    return render_template_string(SIGNIN_TEMPLATE,
                                                  error="Account is already in use from another device.")
                session['team_name'] = team_name
                cursor.execute('UPDATE teams SET ip_address = %s WHERE team_name = %s',
                               (request.remote_addr, team_name))
            else:
                return render_template_string(SIGNIN_TEMPLATE, error="Invalid password.")
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
        resp.set_cookie('team_name', team_name)
        return resp
    return render_template_string(SIGNIN_TEMPLATE)


# Submit page
@app.route('/submit', methods=['GET', 'POST'])
def submit():
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
        flags_submitted = cursor.fetchone()[0].split(',')

        if flag in flags_submitted:
            return render_template_string(SUBMIT_TEMPLATE, error="Flag already submitted.")

        if flag in [FLAG_1, FLAG_2, FLAG_3, FLAG_4, FLAG_5]:
            flags_submitted.append(flag)
            cursor.execute('UPDATE teams SET score = score + %s, flags_submitted = %s WHERE team_name = %s',
                           (round(points, 2), ','.join(flags_submitted), team_name))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template_string(SUBMIT_TEMPLATE, success=True, points=round(points, 2))
        else:
            return render_template_string(SUBMIT_TEMPLATE, error="Invalid flag.")
    return render_template_string(SUBMIT_TEMPLATE)


# Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT team_name, score FROM teams ORDER BY score DESC')
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(LEADERBOARD_TEMPLATE, teams=teams)


# ----------------------- CHALLENGES ----------------------- #


# Challenge 1: Cryptography
@app.route('/cryptography', methods=['GET', 'POST'])
def cryptography():
    description = "Decrypt a ROT13-encrypted message to uncover the flag."
    encrypted_message = "GUVF_VF_GUR_SYNT"

    if request.method == 'POST':
        user_input = request.form.get('decrypted')
        if user_input == "THIS_IS_THE_FLAG":
            return render_template_string(COMP_TEMPLATE, challenge=1, success=True, flag=FLAG_1,
                                          description=description, encrypted=encrypted_message)
        else:
            return render_template_string(COMP_TEMPLATE, challenge=1, error="Incorrect decryption.",
                                          description=description, encrypted=encrypted_message)

    return render_template_string(COMP_TEMPLATE, challenge=1, description=description, encrypted=encrypted_message)


# Challenge 2: Web Exploitation
@app.route('/weblogin', methods=['GET', 'POST'])
def weblogin():
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
                                          description=description)
        else:
            return render_template_string(COMP_TEMPLATE, challenge=2, error="Invalid credentials.",
                                          description=description)

    return render_template_string(COMP_TEMPLATE, challenge=2, description=description)


# Challenge 3: Reverse Engineering
@app.route('/binary', methods=['GET', 'POST'])
def binary():
    description = "Analyze a binary file to find a hardcoded key (Format KEY{xxxx}). First you must find the correct BIN file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            binary_data = uploaded_file.read()
            if "KEY{i_tES_TYU564678IUY^&*(I_E%$rf}".encode() in binary_data and request.form.get('line',
                                                                                                 '') == '136':  # File C3_79.bin
                return render_template_string(COMP_TEMPLATE, challenge=3, success=True, flag=FLAG_3,
                                              description=description)
            else:
                return render_template_string(COMP_TEMPLATE, challenge=3,
                                              error="Flag not found in the binary or Line number incorrect.",
                                              description=description)

    return render_template_string(COMP_TEMPLATE, challenge=3, description=description)


# Challenge 4: Forensics
@app.route('/forensics', methods=['GET', 'POST'])
def forensics():
    description = "Analyze a PCAP file in [Wireshark] to find a hidden key (Format KEY{xxxx}). First you must find the correct PCAP file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            packets = rdpcap(temp_file_path)
            os.remove(temp_file_path)  # Clean up the temporary file

            for packet in packets:
                if (packet.haslayer('Raw') and "KEY{i_tES_TYU564678IUY^&*(I_E%$rf}" in packet['Raw'].load.decode(
                        'utf-8', errors='ignore')
                        and request.form.get('line', '') == '452'):  # File C4_68.pcap
                    return render_template_string(COMP_TEMPLATE, challenge=4, success=True, flag=FLAG_4,
                                                  description=description)
            return render_template_string(COMP_TEMPLATE, challenge=4,
                                          error="Flag not found in PCAP or Line number incorrect.",
                                          description=description)

    return render_template_string(COMP_TEMPLATE, challenge=4, description=description)


# Challenge 5: Steganography
@app.route('/steganography', methods=['GET', 'POST'])
def steganography():
    description = "Extract hidden data (Format KEY{xxxx}) from an image file using a automated script. First you must find the correct JPEG file, then the correct line number."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            try:
                # Read the entire file content
                file_content = uploaded_file.read()
                flag = b"KEY{i_tES_TYU564678IUY^&*(I_E%$rf}"
                if flag in file_content and request.form.get('line', '') == '206':  # File C5_51.jpeg
                    return render_template_string(COMP_TEMPLATE, challenge=5, success=True, flag=FLAG_5,
                                                  description=description)
                else:
                    return render_template_string(COMP_TEMPLATE, challenge=5,
                                                  error="Hidden flag not found or Line number incorrect.",
                                                  description=description)
            except Exception as e:
                return render_template_string(COMP_TEMPLATE, challenge=5, error=f"EXCEPTION: {e}",
                                              description=description)

    return render_template_string(COMP_TEMPLATE, challenge=5, description=description)


# ------------------------- SETUP -------------------------- #

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

# Run the app
if __name__ == "__main__":
    # init_db()
    serve(app, host='0.0.0.0', port=5000)
