# `hashlib` is used to create secure password hashes.
import hashlib
# `hmac` is used for safe hash comparison during login.
import hmac
# `json` is used to read request data and send JSON responses.
import json
# `os` is used here to print the database path nicely.
import os
# `secrets` is used to generate a random salt for each password.
import secrets
# `sqlite3` gives us a lightweight built-in database.
import sqlite3
# These classes let us create a simple HTTP server in Python.
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
# `Path` helps us build file paths safely.
from pathlib import Path


# This gets the folder where this Python file is stored.
BASE_DIR = Path(__file__).resolve().parent
# This creates the full path for the SQLite database file.
DB_PATH = BASE_DIR / "users.db"
# This is the local address where the server will run.
HOST = "127.0.0.1"
# This is the port number where the server will listen.
PORT = 8000


# This function opens a connection to the SQLite database.
def get_connection():
    # Connect to the database file stored in `DB_PATH`.
    connection = sqlite3.connect(DB_PATH)
    # Make rows act like dictionaries so we can use column names like `user["salt"]`.
    connection.row_factory = sqlite3.Row
    # Return the ready-to-use database connection.
    return connection


# This function creates the `users` table if it does not already exist.
def init_db():
    # Open a database connection and close it automatically when done.
    with get_connection() as connection:
        # Run SQL to create the table structure.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )


# This function converts a plain password into a secure hash using a salt.
def hash_password(password, salt):
    # Use PBKDF2 with SHA-256 to derive a secure password hash.
    password_hash = hashlib.pbkdf2_hmac(
        # Choose the hashing algorithm.
        "sha256",
        # Convert the password string into bytes.
        password.encode("utf-8"),
        # Convert the stored hex salt back into bytes.
        bytes.fromhex(salt),
        # Run many iterations to make brute-force attacks harder.
        100000,
    )
    # Convert the hash bytes into a hex string for storage.
    return password_hash.hex()


# This function registers a new user in the database.
def create_user(username, password):
    # Create a random 16-byte salt and store it as hex text.
    salt = secrets.token_hex(16)
    # Hash the password with that salt.
    password_hash = hash_password(password, salt)

    # Try to insert the new user into the database.
    try:
        # Open a database connection and auto-save changes on success.
        with get_connection() as connection:
            # Insert username, hashed password, and salt into the table.
            connection.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt),
            )
        # Return success status and a message for the frontend.
        return True, "Registration successful. You can now log in."
    # This happens if the username already exists because it must be unique.
    except sqlite3.IntegrityError:
        # Return failure status and an error message.
        return False, "Username already exists."


# This function checks whether a username and password are valid.
def validate_user(username, password):
    # Open the database connection.
    with get_connection() as connection:
        # Look for a user record with the given username.
        user = connection.execute(
            "SELECT username, password_hash, salt FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    # If no user was found, login fails.
    if user is None:
        return False, "User not found."

    # Hash the entered password using the stored salt from the database.
    expected_hash = hash_password(password, user["salt"])
    # Compare the newly generated hash with the stored hash securely.
    if not hmac.compare_digest(expected_hash, user["password_hash"]):
        return False, "Invalid password."

    # If the hashes match, login is successful.
    return True, f"Login successful. Welcome, {user['username']}."


# This class handles incoming HTTP requests.
class LoginRequestHandler(BaseHTTPRequestHandler):
    # This method adds headers before the response is finished.
    def end_headers(self):
        # Allow requests from any origin, useful when HTML is opened in the browser.
        self.send_header("Access-Control-Allow-Origin", "*")
        # Tell the browser which HTTP methods are allowed.
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        # Tell the browser which request headers are allowed.
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # Call the original `end_headers` method from the parent class.
        super().end_headers()

    # This handles browser preflight requests for CORS.
    def do_OPTIONS(self):
        # Send "No Content" status because no body is needed.
        self.send_response(204)
        # Finish the response headers.
        self.end_headers()

    # This handles POST requests sent to the server.
    def do_POST(self):
        # Map URL paths to the method that should handle them.
        routes = {
            "/register": self.handle_register,
            "/login": self.handle_login,
        }

        # Get the correct handler based on the current request path.
        handler = routes.get(self.path)
        # If the path is not supported, return a 404 error.
        if handler is None:
            self.send_json(404, {"message": "Endpoint not found."})
            return

        # Read and decode the JSON body from the request.
        data = self.read_json()
        # If reading failed, stop here because `read_json` already sent an error.
        if data is None:
            return

        # Call the correct route handler with the parsed request data.
        handler(data)

    # This helper reads JSON data from the request body.
    def read_json(self):
        # Read the `Content-Length` header to know how many bytes to read.
        content_length = int(self.headers.get("Content-Length", "0"))
        # Read that many bytes from the request stream.
        raw_body = self.rfile.read(content_length)

        # Try to convert the bytes into Python data.
        try:
            # Decode bytes to text, then parse JSON text into a dictionary.
            data = json.loads(raw_body.decode("utf-8"))
        # If the body is not valid JSON, send an error.
        except json.JSONDecodeError:
            self.send_json(400, {"message": "Invalid JSON body."})
            return None

        # Return the parsed JSON data.
        return data

    # This handles the `/register` route.
    def handle_register(self, data):
        # Read the username from the request and remove extra spaces.
        username = str(data.get("username", "")).strip()
        # Read the password from the request and remove extra spaces.
        password = str(data.get("password", "")).strip()

        # Validate the username and password before saving them.
        error = self.validate_input(username, password)
        # If validation fails, send the error message back.
        if error:
            self.send_json(400, {"message": error})
            return

        # Try to create the user in the database.
        success, message = create_user(username, password)
        # Choose HTTP status 201 for success, 409 for duplicate username.
        status_code = 201 if success else 409
        # Send the final JSON response back to the browser.
        self.send_json(status_code, {"message": message})

    # This handles the `/login` route.
    def handle_login(self, data):
        # Read the username from the request and remove extra spaces.
        username = str(data.get("username", "")).strip()
        # Read the password from the request and remove extra spaces.
        password = str(data.get("password", "")).strip()

        # Validate the username and password format first.
        error = self.validate_input(username, password)
        # If validation fails, send the error message back.
        if error:
            self.send_json(400, {"message": error})
            return

        # Check the entered credentials against the database.
        success, message = validate_user(username, password)
        # Choose HTTP status 200 for success, 401 for login failure.
        status_code = 200 if success else 401
        # Send the JSON response.
        self.send_json(status_code, {"message": message})

    # This helper checks whether the input meets basic rules.
    @staticmethod
    def validate_input(username, password):
        # Reject usernames shorter than 3 characters.
        if len(username) < 3:
            return "Username must be at least 3 characters long."
        # Reject passwords shorter than 6 characters.
        if len(password) < 6:
            return "Password must be at least 6 characters long."
        # Return `None` when there is no validation error.
        return None

    # This helper sends a JSON response with a status code.
    def send_json(self, status_code, payload):
        # Convert the Python dictionary into JSON bytes.
        body = json.dumps(payload).encode("utf-8")
        # Start the response with the given HTTP status code.
        self.send_response(status_code)
        # Tell the client that the response body is JSON.
        self.send_header("Content-Type", "application/json")
        # Tell the client how large the body is.
        self.send_header("Content-Length", str(len(body)))
        # Finish the headers.
        self.end_headers()
        # Write the JSON bytes to the response output stream.
        self.wfile.write(body)

    # This disables the default server log messages in the terminal.
    def log_message(self, format, *args):
        # Do nothing, so each request is not printed automatically.
        return


# This block runs only when the file is executed directly.
if __name__ == "__main__":
    # Make sure the database and table exist before starting the server.
    init_db()
    # Create the HTTP server and tell it which host, port, and handler to use.
    server = ThreadingHTTPServer((HOST, PORT), LoginRequestHandler)
    # Print the local server address for convenience.
    print(f"Login server running at http://{HOST}:{PORT}")
    # Print where the SQLite database file is stored.
    print(f"Database file: {os.fspath(DB_PATH)}")
    # Start the server and keep it running until manually stopped.
    server.serve_forever()
