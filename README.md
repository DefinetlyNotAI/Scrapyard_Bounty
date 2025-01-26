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

This document provides an overview of the available API endpoints for the project. Each endpoint includes information on the HTTP method, URL, required parameters, and whether admin access is required.

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

### Database Size
- **URL:** `/api/dbsize`
- **Method:** GET
- **Description:** Retrieves the size of the database.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "size": "123 MB"
  }
  ```

### List Tables
- **URL:** `/api/tables`
- **Method:** GET
- **Description:** Lists all tables in the database.
- **Admin Required:** ✅
- **Response:**
  ```json
  [
    "table1",
    "table2"
  ]
  ```

### Get Table Rows
- **URL:** `/api/tables/<table_name>`
- **Method:** GET
- **Description:** Retrieves rows from a specified table.
- **Admin Required:** ✅
- **Response:**
  ```json
  [
    ["row1_col1", "row1_col2"],
    ["row2_col1", "row2_col2"]
  ]
  ```

### Get Table Schema
- **URL:** `/api/tables/<table_name>/schema`
- **Method:** GET
- **Description:** Retrieves the schema of a specified table.
- **Admin Required:** ✅
- **Response:**
  ```json
  [
    {"column_name": "id", "data_type": "integer"},
    {"column_name": "name", "data_type": "text"}
  ]
  ```

### Execute Query
- **URL:** `/api/query`
- **Method:** POST
- **Description:** Executes a SQL query.
- **Admin Required:** ✅
- **Request Body:**
  ```json
  {
    "query": "SELECT * FROM table_name"
  }
  ```
- **Response:**
  ```json
  [
    ["row1_col1", "row1_col2"],
    ["row2_col1", "row2_col2"]
  ]
  ```

### View Teams
- **URL:** `/api/teams`
- **Method:** GET
- **Description:** Retrieves a list of teams.
- **Admin Required:** ✅
- **Response:**
  ```json
  [
    {"id": 1, "team_name": "Team1", "score": 100},
    {"id": 2, "team_name": "Team2", "score": 150}
  ]
  ```

### Delete Database
- **URL:** `/api/delete`
- **Method:** POST
- **Description:** Deletes the database.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "message": "Database deleted successfully."
  }
  ```

### Active Connections
- **URL:** `/api/activeConnections`
- **Method:** GET
- **Description:** Retrieves the number of active connections.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "activeConnections": 5
  }
  ```

### API Status
- **URL:** `/api/status`
- **Method:** GET
- **Description:** Checks if the API is running.
- **Admin Required:** ❌
- **Response:**
  ```json
  {
    "status": "API is running"
  }
  ```

### Delete Table Item
- **URL:** `/api/tables/<table_name>/<int:row_id>`
- **Method:** DELETE
- **Description:** Deletes a specific item from a table.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "message": "Item deleted successfully."
  }
  ```

### Delete Table
- **URL:** `/api/tables/<table_name>`
- **Method:** DELETE
- **Description:** Deletes a specified table.
- **Admin Required:** ✅
- **Response:**
  ```json
  {
    "message": "Table deleted successfully."
  }
  ```

## Notes
- Endpoints marked with ✅ require admin access.
- Ensure to handle responses and errors appropriately in your application.
