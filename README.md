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

This document provides a detailed overview of the available API endpoints for the project. Each endpoint includes information on the HTTP method, URL, required parameters, and whether admin access is required.

## Endpoints

### Health Check
- **URL:** `/api/health`
- **Method:** GET
- **Description:** Checks the health status of the API.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "status": true
  }
  ```

---

### Execute Query
- **URL:** `/api/executeQuery`
- **Method:** POST
- **Description:** Executes a query on the database. The query is provided in the request body. This endpoint requires admin access.
- **Admin Required:** ✅
- **Parameters:**
    - `query`: A string representing the SQL query to be executed.
- **Response:**
    - **Success (200):**
      ```json
      {
        "message": "Query executed successfully"
      }
      ```
    - **Failure (400):**
      ```json
      {
        "error": "No query provided"
      }
      ```
    - **Error (500):**
      ```json
      {
        "error": "Database error"
      }
      ```

---

### API Status
- **URL:** `/api/status`
- **Method:** GET
- **Description:** Provides the status of the API, uptime, and database connection status.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "status": "API is running",
    "uptime_seconds": 3600,
    "database_connected": true
  }
  ```

---

### Download Challenge Files
- **URL:** `/api/download/<challenge_id>`
- **Method:** GET
- **Description:** Downloads a zip file for a specific challenge. Valid challenge IDs are `bin`, `images`, and `pcap`. Rate limiting applies.
- **Admin Required:** ❌
- **Parameters:**
    - `challenge_id`: A string identifying the challenge to download (`bin`, `images`, or `pcap`).
- **Response:**
    - **Success (200):**
      Returns the challenge file as a download.
    - **Failure (404):**
      ```json
      {
        "error": "Invalid challenge zip, available ['bin', 'images', 'pcap']"
      }
      ```

---

### Get DB Size
- **URL:** `/api/get/size`
- **Method:** GET
- **Description:** Retrieves the size of the current database.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "size": "10 MB"
  }
  ```

---

### Get Active Connections
- **URL:** `/api/get/activeConnections`
- **Method:** GET
- **Description:** Returns the number of active database connections. Requires admin access.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "activeConnections": 5
  }
  ```

---

### View All Teams
- **URL:** `/api/get/allTeams`
- **Method:** GET
- **Description:** Retrieves all teams and their scores. Requires admin access.
- **Admin Required:** ❌
- **Response:**
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

### Get Challenge Progress
- **URL:** `/api/get/challengesProgress`
- **Method:** GET
- **Description:** Retrieves the progress of a team's challenges. Requires the user to be logged in.
- **Admin Required:** ❌
- **Response:**
    - **Success (200):**
      ```json
      [
        {
          "challenge_id": "bin",
          "flag_submitted": true,
          "score": 50
        }
      ]
      ```
    - **Failure (404):**
      ```json
      {
        "message": "No progress found for the team"
      }
      ```

---

### Get Leaderboard
- **URL:** `/api/get/leaderboard`
- **Method:** GET
- **Description:** Retrieves the leaderboard, paginated. Rate limiting applies.
- **Admin Required:** ❌
- **Parameters:**
    - `page`: The page number to retrieve (default is 1).
    - `per_page`: The number of teams per page (default is 10).
- **Response:**
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

### Get Tables
- **URL:** `/api/get/tables`
- **Method:** GET
- **Description:** Retrieves a list of all tables in the public schema. Requires admin access.
- **Admin Required:** ✅
- **Response:**
  ```json
  [
    "teams",
    "users"
  ]
  ```

---

### Get Table Rows
- **URL:** `/api/get/tables/<table_name>`
- **Method:** GET
- **Description:** Retrieves the first 100 rows from the specified table. Requires admin access.
- **Admin Required:** ✅
- **Parameters:**
    - `table_name`: The name of the table to retrieve rows from.
- **Response:**
  ```json
  [
    {
      "id": 1,
      "team_name": "Team A",
      "score": 100
    }
  ]
  ```

---

### Get Table Schema
- **URL:** `/api/get/tables/<table_name>/schema`
- **Method:** GET
- **Description:** Retrieves the schema (column names and data types) for the specified table. Requires admin access.
- **Admin Required:** ✅
- **Parameters:**
    - `table_name`: The name of the table to retrieve the schema for.
- **Response:**
  ```json
  [
    {
      "column_name": "id",
      "data_type": "integer"
    },
    {
      "column_name": "team_name",
      "data_type": "text"
    }
  ]
  ```

---

### Delete Table Item
- **URL:** `/api/delete/tables/<table_name>/<int:row_id>`
- **Method:** DELETE
- **Description:** Deletes a specific row from a table. Requires admin access.
- **Admin Required:** ✅
- **Parameters:**
    - `table_name`: The name of the table from which the row will be deleted.
    - `row_id`: The ID of the row to be deleted.
- **Response:**
  ```json
  {
    "message": "Item deleted successfully."
  }
  ```

---

### Delete Table
- **URL:** `/api/delete/tables/<table_name>`
- **Method:** DELETE
- **Description:** Deletes the specified table. Requires admin access.
- **Admin Required:** ✅
- **Parameters:**
    - `table_name`: The name of the table to be deleted.
- **Response:**
  ```json
  {
    "message": "Table deleted successfully."
  }
  ```

---

### Delete Database
- **URL:** `/api/delete/database`
- **Method:** POST
- **Description:** Deletes the entire database by dropping tables `users` and `teams`. Requires admin access.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "message": "Database deleted successfully."
  }
  ```

---

### Get User Profile
- **URL:** `/api/get/user/profile`
- **Method:** GET
- **Description:** Retrieves the profile of the logged-in user. Requires the user to be logged in.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "team_name": "Team A",
    "score": 100,
    "flags_submitted": ["flag1", "flag2"]
  }
  ```

---

### Get Team Rank
- **URL:** `/api/get/user/rank`
- **Method:** GET
- **Description:** Retrieves the rank of the logged-in team based on the current score.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "rank": 1,
    "next_team_score": {"team_name": "Team B", "score": 90}
  }
  ```

---

### Get Team History
- **URL:** `/api/get/user/history`
- **Method:** GET
- **Description:** Retrieves the history of the logged-in team's submissions and scores.
- **Admin Required:** ❌
- **Response:**
  ```json
  [
    {
      "timestamp": "2025-01-01T12:00:00",
      "flags_submitted": ["flag1"],
      "score": 100
    }
  ]
  ```

---

### Get Flag Submissions
- **URL:** `/api/get/user/submissions`
- **Method:** GET
- **Description:** Retrieves the history of the logged-in team's flag submissions.
- **Admin Required:** ❌
- **Response:**
  ```json
  [
    {
      "flag": "flag1",
      "timestamp": "2025-01-01T12:00:00"
    }
  ]
  ```

---
