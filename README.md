# Capture The Flag (CTF) Platform

This project is a Capture The Flag (CTF) platform built using Python and Flask.
It includes various challenges such as Cryptography, Web Exploitation, Reverse Engineering,
Forensics, and Steganography. (Although very basic and not purely accurate)

## Features

- User authentication and session management
- Multiple CTF challenges
- Leaderboard to track team scores
- Secure flag submission system

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/DefinetlyNotAI/Scrapyard_Bounty.git
    cd Scrapyard_Bounty
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
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