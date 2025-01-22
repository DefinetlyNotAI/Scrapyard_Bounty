import os
import sqlite3
import tempfile

from flask import Flask, request, render_template_string
from scapy.all import rdpcap
from stegano import lsb

# Flask app instance
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = "i_tES_TYU564678IUY^&*(I_E%$rf"  # Also the key for c3, c4 and c5
FLAG_1 = "CTF{ROT-13-FLAG}"
FLAG_2 = "CTF{SQLI_FLAG}"
FLAG_3 = "CTF{REVERSE_ME}"
FLAG_4 = "CTF{PCAP_FLAG}"
FLAG_5 = "CTF{STEGANOGRAPHY_FLAG}"


# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', 'password123'))
    conn.commit()
    conn.close()


if not os.path.exists('users.db'):
    init_db()


# Challenge 1: Cryptography
@app.route('/cryptography', methods=['GET', 'POST'])
def cryptography():
    description = "Decrypt a ROT13-encrypted message to uncover the flag."
    encrypted_message = "GUVF_VF_GUR_SYNT"

    if request.method == 'POST':
        user_input = request.form.get('decrypted')
        if user_input == "THIS_IS_THE_FLAG":
            return render_template_string(HTML_TEMPLATE, challenge=1, success=True, flag=FLAG_1,
                                          description=description, encrypted=encrypted_message)
        else:
            return render_template_string(HTML_TEMPLATE, challenge=1, error="Incorrect decryption.",
                                          description=description, encrypted=encrypted_message)

    return render_template_string(HTML_TEMPLATE, challenge=1, description=description, encrypted=encrypted_message)


# Challenge 2: Web Exploitation
@app.route('/weblogin', methods=['GET', 'POST'])
def weblogin():
    description = "Bypass the login page using SQL Injection to discover the flag."
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template_string(HTML_TEMPLATE, challenge=2, success=True, flag=FLAG_2,
                                          description=description)
        else:
            return render_template_string(HTML_TEMPLATE, challenge=2, error="Invalid credentials.",
                                          description=description)

    return render_template_string(HTML_TEMPLATE, challenge=2, description=description)


# Challenge 3: Reverse Engineering
@app.route('/reverse-engineering', methods=['GET', 'POST'])
def reverse_engineering():
    description = "Analyze a binary file to find a hardcoded flag."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            binary_data = uploaded_file.read()
            if "KEY{i_tES_TYU564678IUY^&*(I_E%$rf}".encode() in binary_data and request.form.get('line',
                                                                                                 '') == '136':  # File C3_79.bin
                return render_template_string(HTML_TEMPLATE, challenge=3, success=True, flag=FLAG_3,
                                              description=description)
            else:
                return render_template_string(HTML_TEMPLATE, challenge=3, error="Flag not found in the binary.",
                                              description=description)

    return render_template_string(HTML_TEMPLATE, challenge=3, description=description)


# Challenge 4: Forensics
@app.route('/forensics', methods=['GET', 'POST'])
def forensics():
    description = "Analyze a PCAP file in Wireshark to find a hidden HTTP flag."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            packets = rdpcap(temp_file_path)
            os.remove(temp_file_path)  # Clean up the temporary file

            for packet in packets:
                print(packet.haslayer('Raw'))
                if packet.haslayer('Raw') and "KEY{i_tES_TYU564678IUY^&*(I_E%$rf}" in packet['Raw'].load.decode('utf-8',
                                                                                                                errors='ignore') and request.form.get(
                    'line', '') == '452':
                    return render_template_string(HTML_TEMPLATE, challenge=4, success=True, flag=FLAG_4,
                                                  description=description)
            return render_template_string(HTML_TEMPLATE, challenge=4, error="Flag not found in PCAP.",
                                          description=description)

    return render_template_string(HTML_TEMPLATE, challenge=4, description=description)


# Challenge 5: Steganography
@app.route('/steganography', methods=['GET', 'POST'])
def steganography():
    description = "Extract hidden data from an image file using src like StegSolve."
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            try:
                hidden_message = lsb.reveal(uploaded_file.stream)
                if hidden_message == "KEY{i_tES_TYU564678IUY^&*(I_E%$rf}" and request.form.get('line',
                                                                                               '') == '206':  # File C5_51.jpeg
                    return render_template_string(HTML_TEMPLATE, challenge=5, success=True, flag=FLAG_5,
                                                  description=description)
                else:
                    return render_template_string(HTML_TEMPLATE, challenge=5, error="Hidden flag not found.",
                                                  description=description)
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, challenge=5, error=f"Error: {e}", description=description)

    return render_template_string(HTML_TEMPLATE, challenge=5, description=description)


# Home Route
@app.route('/')
def home():
    return """
    <h1>Welcome to the CTF Challenges!</h1>
    <p>Select a challenge to start:</p>
    <ul>
        <li><a href="/cryptography">Cryptography Challenge</a></li>
        <li><a href="/weblogin">Web Exploitation Challenge</a></li>
        <li><a href="/reverse-engineering">Reverse Engineering Challenge</a></li>
        <li><a href="/forensics">Forensics Challenge</a></li>
        <li><a href="/steganography">Steganography Challenge</a></li>
    </ul>
    """


# HTML template for challenges
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CTF Challenge</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: auto; }
        .success { color: green; }
        .error { color: red; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"] { width: 100%; padding: 8px; box-sizing: border-box; }
        input[type="file"] { margin-bottom: 15px; }
        button { padding: 10px 15px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Challenge {{ challenge }}</h1>
        {% if description %}
        <p><strong>Description:</strong> {{ description }}</p>
        {% endif %}
        {% if encrypted %}
        <p><strong>Encrypted Message:</strong> {{ encrypted }}</p>
        {% endif %}
        {% if success %}
        <p class="success"><strong>Congratulations!</strong> You've solved the challenge.</p>
        <p><strong>Your Token:</strong> {{ flag }}</p>
        {% elif error %}
        <p class="error"><strong>Error:</strong> {{ error }}</p>
        {% endif %}
        {% if challenge in [1, 2] %}
            <form method="post">
                {% if challenge == 1 %}
                <div class="form-group">
                    <label for="decrypted">Decrypted Message:</label>
                    <input type="text" id="decrypted" name="decrypted" value="{{ request.form.get('decrypted', '') }}">
                </div>
                {% elif challenge == 2 %}
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username">
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="text" id="password" name="password">
                </div>
                {% endif %}
                <button type="submit">Submit</button>
            </form>
        {% elif challenge in [3, 4, 5] %}
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Upload File:</label>
                    <input type="file" id="file" name="file">
                </div>
                <div class="form-group">
                    <label for="line">Line Number:</label>
                    <input type="text" id="line" name="line">
                </div>
                <button type="submit">Submit</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
