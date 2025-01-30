# Capture The Flag (CTF) Platform

This project is a Capture The Flag (CTF) platform built using Python and Flask. It includes various challenges such as Cryptography, Web Exploitation, Reverse Engineering, Forensics, and Steganography.


## Features

- User authentication and session management
- Multiple CTF challenges
- Leaderboard to track team scores
- Secure flag submission system
- Simple RESTful API

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/DefinetlyNotAI/Scrapyard_Bounty.git
    cd ctf-platform
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```


## Usage

1. Run the Flask application:
    ```sh
    python CTF.py
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Challenges

1. **Cryptography**: Decrypt a ROT13-encrypted message to uncover the flag.
2. **Web Exploitation**: Bypass the login page using SQL Injection to discover the flag.
3. **Reverse Engineering**: Analyze a binary file to find a hardcoded key.
4. **Forensics**: Analyze a PCAP file in Wireshark to find a hidden key.
5. **Steganography**: Extract hidden data from an image file using an automated script.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.


---

# API Documentation

This document provides a detailed overview of the available API endpoints for the project. 
Each endpoint includes information on the HTTP method, URL, required parameters, 
and whether admin access is required as well as rate limits.

---

### `/api/executeQuery`
- **Method:** POST
- **Description:** Executes raw SQL queries (Select, Insert, Update, Delete).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ❌ (Requires POST request with JSON body)
- **Request Body Preview:**
  ```json
  {
    "query": "SELECT * FROM users"
  }
  ```
- **Response Preview:**
  ```json
  {
    "message": "Query executed successfully"
  }
  ```

---

### `/api/status`
- **Method:** GET
- **Description:** Checks API status and database connection.
- **Admin?:** 🔓
- **Rate Limit:** 🚀
- **Plug and Play?:** ✅
- **Response Preview:**
  ```json
  {
    "status": "API is running",
    "uptime_seconds": 12345,
    "database_connected": true
  }
  ```

---

### `/api/download/<challenge_id>`
- **Method:** GET
- **Description:** Downloads challenge files by ID (e.g., bin, images, pcap).
- **Admin?:** 🔓
- **Rate Limit:** 🔥 5 requests/hour
- **Plug and Play?:** ✔️ (Browser-accessible if challenge exists, must be signed in)
- **Response Preview:** Download file (`.zip` file)

---

### `/api/get/size`
- **Method:** GET
- **Description:** Retrieves the size of the current database.
- **Admin?:** 🔓
- **Rate Limit:** 🚀
- **Plug and Play?:** ✅
- **Response Preview:**
  ```json
  {
    "size": "10 MB"
  }
  ```

---

### `/api/get/activeConnections`
- **Method:** GET
- **Description:** Returns the count of active database connections.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 60 requests/hour
- **Plug and Play?:** ✅
- **Response Preview:**
  ```json
  {
    "activeConnections": 5
  }
  ```

---

### `/api/get/allTeams`
- **Method:** GET
- **Description:** Retrieves all teams' IDs, names, and scores.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 60 requests/hour
- **Plug and Play?:** ✅
- **Response Preview:**
  ```json
  [
    {
      "id": 1,
      "team_name": "Team A",
      "score": 100
    },
    {
      "id": 2,
      "team_name": "Team B",
      "score": 90
    }
  ]
  ```

---

### `/api/get/challengesProgress`
- **Method:** GET
- **Description:** Retrieves a logged-in team's challenge progress (including flags and score).
- **Admin?:** 🔓
- **Rate Limit:** 🔥 50 requests/hour
- **Plug and Play?:** ✔️ (Requires session with logged-in user)
- **Response Preview:**
  ```json
  [
    {
      "challenge_id": "bin",
      "flag_submitted": true,
      "score": 20
    }
  ]
  ```

---

### `/api/get/leaderboard`
- **Method:** GET
- **Description:** Retrieves the leaderboard with pagination.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 30 requests/hour
- **Plug and Play?:** ✅ (Pagination query parameters needed)
- **Response Preview:**
  ```json
  [
    {
      "team_name": "Team A",
      "score": 100
    },
    {
      "team_name": "Team B",
      "score": 90
    }
  ]
  ```

---

### `/api/get/tables`
- **Method:** GET
- **Description:** Retrieves all database table names (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  ["teams", "users"]
  ```

---

### `/api/get/tables/<table_name>`
- **Method:** GET
- **Description:** Retrieves all rows from a specific table (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  [
    [1, "Team A", 100],
    [2, "Team B", 90]
  ]
  ```

---

### `/api/get/tables/<table_name>/schema`
- **Method:** GET
- **Description:** Retrieves the schema of a specific table (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  [
    {"column_name": "id", "data_type": "integer"},
    {"column_name": "team_name", "data_type": "text"}
  ]
  ```

---

### `/api/delete/tables/<table_name>/<int:row_id>`
- **Method:** DELETE
- **Description:** Deletes a specific row from a table (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  {
    "message": "Item deleted successfully."
  }
  ```

---

### `/api/delete/tables/<table_name>`
- **Method:** DELETE
- **Description:** Deletes an entire table (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  {
    "message": "Table deleted successfully."
  }
  ```

---

### `/api/delete/database`
- **Method:** POST
- **Description:** Deletes the entire database (Admin only).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response Preview:**
  ```json
  {
    "message": "Database deleted successfully."
  }
  ```

---

### `/api/get/user/profile`
- **Method:** GET
- **Description:** Retrieves the profile of the logged-in user (team name, score, etc.).
- **Admin?:** 🔓
- **Rate Limit:** 🔥 100 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response Preview:**
  ```json
  {
    "team_name": "Team A",
    "score": 100,
    "flags_submitted": ["flag1", "flag2"]
  }
  ```

---

### `/api/get/user/rank`
- **Method:** GET
- **Description:** Retrieves the rank of the logged-in team.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 20 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response Preview:**
  ```json
  {
    "rank": 1,
    "next_team_score": 90
  }
  ```

---

### `/api/get/user/history`
- **Method:** GET
- **Description:** Retrieves the history of a team's score and flag submissions.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 50 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response Preview:**
  ```json
  [
    {
      "timestamp": "2025-01-01T12:00:00Z",
      "flags_submitted": ["flag1"],
      "score": 100
    }
  ]
  ```

---

### `/api/get/user/submissions`
- **Method:** GET
- **Description:** Retrieves the history of a team's flag submissions.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 100 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response Preview:**
  ```json
  [
    {
      "flag": "flag1",
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
  ```

---

### Mini Table for Emoji Explanation

| Emoji | Sector        | Meaning                                                                             |
|-------|---------------|-------------------------------------------------------------------------------------|
| ❌     | Plug and Play | Impossible to use directly in the browser (requires proper HTTP requests)           |
| ✔️    | Plug and Play | Requires some setup (like being logged in or an admin) but still browser-accessible |
| ✅     | Plug and Play | Fully accessible via browser without any additional setup                           |
| 🔓    | Admin?        | No admin required to use the api                                                    |
| 🔐    | Admin?        | Admin is required to use the api                                                    |
| 🚀    | Rate Limit    | No rate limit                                                                       |

---
