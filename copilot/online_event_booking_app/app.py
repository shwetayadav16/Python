from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "event_booking.db"

app = Flask(__name__)
app.config["DATABASE"] = DATABASE


SAMPLE_EVENTS = [
    (
        "Tech Future Summit",
        "A one-day conference on AI, cloud, and modern product building.",
        "2026-05-10",
        "09:30",
        "Bengaluru Convention Center",
        180,
        1499,
        "Technology",
    ),
    (
        "Startup Networking Night",
        "Meet founders, investors, and early-stage builders in one place.",
        "2026-05-18",
        "18:00",
        "Hyderabad Hub Arena",
        120,
        899,
        "Networking",
    ),
    (
        "Live Music Carnival",
        "An evening of indie bands, food stalls, and open-air performances.",
        "2026-06-02",
        "19:00",
        "Mumbai Seaside Grounds",
        250,
        1299,
        "Music",
    ),
    (
        "Design Masterclass",
        "Hands-on product design workshop covering UX, UI systems, and prototyping.",
        "2026-06-14",
        "11:00",
        "Pune Creative Studio",
        80,
        999,
        "Workshop",
    ),
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL,
            venue TEXT NOT NULL,
            seats_available INTEGER NOT NULL,
            price INTEGER NOT NULL,
            category TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            tickets INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
        """
    )

    existing_events = cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if existing_events == 0:
        cursor.executemany(
            """
            INSERT INTO events (
                title, description, event_date, event_time, venue,
                seats_available, price, category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            SAMPLE_EVENTS,
        )

    db.commit()
    db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/events")
def get_events():
    db = get_db()
    events = db.execute(
        """
        SELECT id, title, description, event_date, event_time, venue,
               seats_available, price, category
        FROM events
        ORDER BY event_date, event_time
        """
    ).fetchall()
    return jsonify([dict(event) for event in events])


@app.get("/api/bookings")
def get_bookings():
    db = get_db()
    bookings = db.execute(
        """
        SELECT bookings.id, bookings.customer_name, bookings.email, bookings.tickets,
               bookings.total_price, bookings.created_at, events.title AS event_title
        FROM bookings
        JOIN events ON events.id = bookings.event_id
        ORDER BY bookings.created_at DESC, bookings.id DESC
        LIMIT 10
        """
    ).fetchall()
    return jsonify([dict(booking) for booking in bookings])


@app.post("/api/book")
def create_booking():
    data = request.get_json(silent=True) or {}

    event_id = data.get("event_id")
    customer_name = str(data.get("customer_name", "")).strip()
    email = str(data.get("email", "")).strip()
    tickets = data.get("tickets")

    if not event_id or not customer_name or not email or not tickets:
        return jsonify({"error": "All booking fields are required."}), 400

    try:
        event_id = int(event_id)
        tickets = int(tickets)
    except (TypeError, ValueError):
        return jsonify({"error": "Event and tickets must be valid numbers."}), 400

    if tickets < 1:
        return jsonify({"error": "Please book at least one ticket."}), 400

    db = get_db()
    event = db.execute(
        "SELECT id, title, seats_available, price FROM events WHERE id = ?",
        (event_id,),
    ).fetchone()

    if event is None:
        return jsonify({"error": "Selected event was not found."}), 404

    if tickets > event["seats_available"]:
        return jsonify({"error": "Not enough seats available for this event."}), 400

    total_price = tickets * event["price"]

    db.execute(
        """
        INSERT INTO bookings (event_id, customer_name, email, tickets, total_price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_id, customer_name, email, tickets, total_price),
    )
    db.execute(
        "UPDATE events SET seats_available = seats_available - ? WHERE id = ?",
        (tickets, event_id),
    )
    db.commit()

    return jsonify(
        {
            "message": f"Booking confirmed for {event['title']}.",
            "total_price": total_price,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
