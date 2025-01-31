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

### `executeQuery`

- **URL:** `/api/executeQuery`
- **Method:** POST
- **Description:** Executes a SQL query on the database.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ❌ (Requires an HTTP request with a JSON payload)
- **Request Body Preview:**
  ```json
  {
    "query": "SELECT * FROM users"
  }
  ```
- **Response preview**
  - `#200`:
     ```json
     {
       "id": 1,
       "username": "example_user",
       "email": "user@example.com"
     }
     ```
  - `#400`:
     ```json
     {
       "error": "No query provided"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Query Execution Failed - API execute_query"
     }
     ```

---

### `api_status`

- **URL:** `/api/status`
- **Method:** GET
- **Description:** Checks if the API is running and verifies database connectivity.
- **Admin?:** 🔓
- **Rate Limit:** 🚀
- **Plug and Play?:** ✅
- **Response preview**
  - `#200`:
     ```json
     {
       "status": "API is running",
       "uptime_seconds": 12345.67,
       "database_connected": true
     }
     ```

---

### `download_challenge_files`

- **URL:** `/api/download/<challenge_id>`
- **Method:** GET
- **Description:** Downloads challenge zip files.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 5 requests/hour
- **Plug and Play?:** ✔️ (Browser-accessible if challenge exists, must be signed in)
- **Response preview**
  - `#200`: *(Binary file download)*
  - `#404`:
     ```json
     {
       "error": "Challenge files not found"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to fetch challenge files"
     }
     ```

---

### `get_db_size`

- **URL:** `/api/get/size`
- **Method:** GET
- **Description:** Fetches the current database size in a human-readable format.
- **Admin?:** 🔓
- **Rate Limit:** 🚀
- **Plug and Play?:** ✅
- **Response preview**
  - `#200`:
     ```json
     {
       "size": "24 MB"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get database size"
     }
     ```

---

### `get_active_connections`

- **URL:** `/api/get/activeConnections`
- **Method:** GET
- **Description:** Fetches the number of currently active database connections.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 60 requests/hour
- **Plug and Play?:** ✅
- **Response preview**
  - `#200`:
     ```json
     {
       "activeConnections": 12
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get active connections"
     }
     ```

---

### `view_teams`

- **URL:** `/api/get/allTeams`
- **Method:** GET
- **Description:** Fetches all teams with their scores.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 60 requests/hour
- **Plug and Play?:** ✅
- **Response preview**
  - `#200`:
     ```json
     [
       {
         "id": 1,
         "team_name": "Team Alpha",
         "score": 150
       },
       {
         "id": 2,
         "team_name": "Team Beta",
         "score": 100
       }
     ]
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get all teams"
     }
     ```

---

### `get_challenge_progress`

- **URL:** `/api/get/challengesProgress`
- **Method:** GET
- **Description:** Fetches the progress of challenges for the logged-in team.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 50 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response preview**
  - `#200`:
     ```json
     [
       {
         "challenge_id": 1,
         "flag_submitted": true,
         "score": 50
       },
       {
         "challenge_id": 2,
         "flag_submitted": false,
         "score": 0
       }
     ]
     ```
  - `#401`:
     ```json
     {
       "error": "User not logged in"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "An error occurred - Function get_challenge_progress"
     }
     ```

---

### `get_leaderboard`

- **URL:** `/api/get/leaderboard`
- **Method:** GET
- **Description:** Retrieves the leaderboard with paginated results.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 30 requests/hour
- **Plug and Play?:** ✅ (Pagination query parameters needed)
- **Response preview**
  - `#200`:
     ```json
     [
       {
         "team_name": "Team Alpha",
         "score": 300
       },
       {
         "team_name": "Team Beta",
         "score": 250
       }
     ]
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get leaderboard"
     }
     ```

---

I'll continue with the documentation in the same format.

---

### `get_tables`

- **URL:** `/api/get/tables`
- **Method:** GET
- **Description:** Retrieves a list of all tables in the database.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     ["users", "teams", "challenges"]
     ```
  - `#500`:
     ```json
     {
       "error": "Getting the tables failed"
     }
     ```

---

### `get_table_rows`

- **URL:** `/api/get/tables/<table_name>`
- **Method:** GET
- **Description:** Retrieves up to 100 rows from a specific table.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     [
       {"id": 1, "username": "admin", "email": "admin@example.com"},
       {"id": 2, "username": "user1", "email": "user1@example.com"}
     ]
     ```
  - `#500`:
     ```json
     {
       "error": "Getting the table rows failed"
     }
     ```

---

### `get_table_schema`

- **URL:** `/api/get/tables/<table_name>/schema`
- **Method:** GET
- **Description:** Retrieves the schema of a given table.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     [
       {"column_name": "id", "data_type": "integer"},
       {"column_name": "username", "data_type": "text"},
       {"column_name": "email", "data_type": "text"}
     ]
     ```
  - `#500`:
     ```json
     {
       "error": "Getting the table schema failed"
     }
     ```

---

### `delete_table_item`

- **URL:** `/api/delete/tables/<table_name>/<row_id>`
- **Method:** DELETE
- **Description:** Deletes a specific row from a table based on its ID.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     {
       "message": "Item deleted successfully."
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Deleting the table item failed"
     }
     ```

---

### `delete_table`

- **URL:** `/api/delete/tables/<table_name>`
- **Method:** DELETE
- **Description:** Deletes an entire table from the database.
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     {
       "message": "Table deleted successfully."
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Deleting the table failed"
     }
     ```

---

### `delete_database`

- **URL:** `/api/delete/database`
- **Method:** POST
- **Description:** Deletes the entire database (users and teams tables).
- **Admin?:** 🔐
- **Rate Limit:** 🚀
- **Plug and Play?:** ✔️ (Admin required)
- **Response preview**
  - `#200`:
     ```json
     {
       "message": "Database deleted successfully."
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Deleting the database failed"
     }
     ```

---

### `get_user_profile`

- **URL:** `/api/get/user/profile`
- **Method:** GET
- **Description:** Fetches the logged-in user's profile data.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 100 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response preview**
  - `#200`:
     ```json
     {
       "team_name": "Team Alpha",
       "score": 150,
       "flags_submitted": ["flag{example1}", "flag{example2}"]
     }
     ```
  - `#401`:
     ```json
     {
       "error": "User not logged in"
     }
     ```
  - `#404`:
     ```json
     {
       "error": "User not found"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get user profile"
     }
     ```

---

### `get_team_rank`

- **URL:** `/api/get/user/rank`
- **Method:** GET
- **Description:** Fetches the rank of the logged-in team.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 20 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response preview**
  - `#200`:
     ```json
     {
       "rank": 3,
       "next_team_score": 250
     }
     ```
  - `#401`:
     ```json
     {
       "error": "User not logged in"
     }
     ```
  - `#404`:
     ```json
     {
       "error": "Team not found"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get team rank"
     }
     ```

---

### `get_team_history`

- **URL:** `/api/get/user/history`
- **Method:** GET
- **Description:** Fetches the history of a logged-in team’s progress.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 50 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response preview**
  - `#200`:
     ```json
     [
       {
         "timestamp": "2025-01-30T14:23:00Z",
         "flags_submitted": ["flag{example3}"],
         "score": 50
       },
       {
         "timestamp": "2025-01-29T10:15:00Z",
         "flags_submitted": ["flag{example1}", "flag{example2}"],
         "score": 100
       }
     ]
     ```
  - `#404`:
     ```json
     {
       "message": "No history found for the team"
     }
     ```
  - `#500`:
     ```json
     {
       "error": "Failed to get team history"
     }
     ```

---

### `get_submission_history`

- **URL:** `/api/get/user/submissions`
- **Method:** GET
- **Description:** Fetches the logged-in team's flag submission history.
- **Admin?:** 🔓
- **Rate Limit:** 🔥 100 requests/hour
- **Plug and Play?:** ✔️ (User must be logged in)
- **Response preview**
  - `#200`:
     ```json
     [
       {
         "flag": "flag{example1}",
         "timestamp": "2025-01-30T12:00:00Z"
       },
       {
         "flag": "flag{example2}",
         "timestamp": "2025-01-29T08:45:00Z"
       }
     ]
     ```
    - `#404`:
       ```json
       {
         "message": "No submissions found for the team"
       }
       ```
    - `#500`:
       ```json
       {
         "error": "Failed to get submission history"
       }
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
