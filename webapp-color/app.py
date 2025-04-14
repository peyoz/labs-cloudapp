import os
import random
import argparse
from datetime import datetime
import logging
import socket
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


app = Flask(__name__)

# Check if the application is running in stateful mode
STATEFUL = os.environ.get("STATEFUL", "false").lower() == "true"

if STATEFUL:
    # Configure the database connection
    DATABASE_URI = os.environ.get("uri")
    if not DATABASE_URI:
        logging.error("Environment variable 'uri' is not set. Exiting.")
        exit(1)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    # Define the Message model
    class Message(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        hostname = db.Column(db.String(255), nullable=False)
        content = db.Column(db.Text, nullable=False)
else:
    db = None  # No database connection in stateless mode

# Define color codes and supported colors
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "purple": "#8e44ad",
    "blue": "#2980b9",
    "dodgerblue": "#0984e3",
    "pink": "#be2edd",
    "gray": "#7f8c8d"
}

SUPPORTED_COLORS = ",".join(color_codes.keys())

# Setup logging
logging.basicConfig(level=logging.INFO)

def determine_color():
    """Determine the color based on environment variable or random choice."""
    if __name__ == "__main__":  # Only parse arguments when running the script directly
        color_from_arg = get_color_from_args()
        if color_from_arg:
            logging.info(f"Color from command line argument: {color_from_arg}")
            return validate_color(color_from_arg)

    COLOR_FROM_ENV = os.environ.get('APP_COLOR')
    if COLOR_FROM_ENV:
        logging.info(f"Color from environment variable: {COLOR_FROM_ENV}")
        return validate_color(COLOR_FROM_ENV)
    else:
        color = random.choice(list(color_codes.keys()))
        logging.info(f"No command line argument or environment variable. Picking a Random Color: {color}")
        return validate_color(color)

def validate_color(color):
    """Validate that the color is supported."""
    if color not in color_codes:
        logging.error(f"Invalid color: '{color}'. Supported colors are: {SUPPORTED_COLORS}")
        exit(1)
    return color

@app.route("/")
def main_route():
    """Render the main page with the determined color and messages."""
    name = socket.gethostname()
    COLOR = determine_color()

    if COLOR not in color_codes:
        logging.error(f"Color not supported. Received '{COLOR}', expected one of {SUPPORTED_COLORS}")
        exit(1)

    messages = ""
    if STATEFUL and Message:
        messages = "\n".join([f"{msg.timestamp} [{msg.hostname}] - {msg.content}" for msg in Message.query.all()])

    return render_template(
        'hello.html',
        name=name,
        color=color_codes[COLOR],
        messages=messages,
        STATEFUL_mode=STATEFUL
    )

@app.route("/message", methods=["POST"])
def add_message():
    """Store a message in the database and redirect to main."""
    message = request.form.get("message")
    if message:
        hostname = socket.gethostname()
        new_message = Message(hostname=hostname, content=message)
        db.session.add(new_message)
        db.session.commit()
    return redirect(url_for('main_route'))

@app.route("/health")
def health_check():
    """Simple health check endpoint."""
    try:
        if STATEFUL:
            # Run a simple query to test database connectivity
            db.session.execute(text("SELECT 1"))
        return "OK", 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return "Database connection error", 500

def get_color_from_args():
    """Parse command line arguments to get the color."""
    parser = argparse.ArgumentParser(description="A sample web application that displays a colored background.")
    parser.add_argument('--color', choices=color_codes.keys(), help=f"Color to display. Must be one of {SUPPORTED_COLORS}.")
    args = parser.parse_args()
    return args.color

if __name__ == "__main__":
    # Initialize the database
    with app.app_context():
        if STATEFUL:
            db.create_all()

    # Validate the color at startup
    color = determine_color()
    validate_color(color)

    # Print description of how the application works
    print("This is a sample web application that displays a colored background.")
    print("A color can be specified in two ways:")
    print("\n1. As a command line argument with --color as the argument. Accepts one of " + SUPPORTED_COLORS)
    print("2. As an Environment variable APP_COLOR. Accepts one of " + SUPPORTED_COLORS)
    print("3. If none of the above then a random color is picked from the above list.")
    print("Note: Command line argument takes precedence over the environment variable.\n")

    # Start the Flask application
    app.run(host="0.0.0.0", port=8080)