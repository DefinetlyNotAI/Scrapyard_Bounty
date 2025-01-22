## Step-by-Step Guide for Challenge 2: Web Exploitation

---

### Step 1: Start the Flask Server

Run the script to start the server:

```bash
python ctf_challenges_host.py
```

Access the application through `http://127.0.0.1:5000/weblogin` in your browser.

---

### Step 2: Understand the Login Page

You'll see a form with two fields:

- **Username**
- **Password**

---

### Step 3: Identify the Vulnerability

The password field allows SQL Injection due to improper query sanitization. Use the payload `' OR '1'='1` in the
password field to exploit this.

---

### Step 4: Exploit the Vulnerability

Fill the form as follows:

- **Username:** `admin`
- **Password:** `' OR '1'='1`

---

### Step 5: Submit the Form

Click the **Login** button to send the request.

---

### Step 6: Retrieve the Flag

If the injection is successful, you will bypass the login and see a success message with the flag:

```
Congratulations! You've solved the challenge. Here is your flag: CTF{THIS_IS_THE_FLAG}
```

---

### Step 7: Verification

If you see an error like "Invalid credentials," double-check the payload and try again.

---