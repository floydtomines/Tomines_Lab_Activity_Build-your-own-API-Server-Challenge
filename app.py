import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request

from seed import GAMES

DATABASE = Path(__file__).resolve().parent / "games.db"
REQUIRED_FIELDS = ("title", "year", "genre")

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            platform TEXT,
            developer TEXT,
            rating REAL,
            description TEXT
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    if count == 0:
        db.executemany(
            """
            INSERT INTO games (title, year, genre, platform, developer, rating, description)
            VALUES (:title, :year, :genre, :platform, :developer, :rating, :description)
            """,
            GAMES,
        )
    db.commit()
    db.close()


def row_to_game(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "year": row["year"],
        "genre": row["genre"],
        "platform": row["platform"],
        "developer": row["developer"],
        "rating": row["rating"],
        "description": row["description"],
    }


def parse_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
    return data, None


def validate_payload(data, partial=False):
    if not partial:
        missing = [field for field in REQUIRED_FIELDS if field not in data or data[field] in (None, "")]
        if missing:
            return (
                jsonify(
                    {
                        "error": f"Missing required field(s): {', '.join(missing)}.",
                        "required": list(REQUIRED_FIELDS),
                    }
                ),
                400,
            )

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "title must be a non-empty string."}), 400
        data["title"] = data["title"].strip()

    if "year" in data:
        try:
            year = int(data["year"])
        except (TypeError, ValueError):
            return jsonify({"error": "year must be an integer."}), 400
        if year < 1970 or year > 2035:
            return jsonify({"error": "year must be between 1970 and 2035."}), 400
        data["year"] = year

    if "genre" in data:
        if not isinstance(data["genre"], str) or not data["genre"].strip():
            return jsonify({"error": "genre must be a non-empty string."}), 400
        data["genre"] = data["genre"].strip()

    if "rating" in data and data["rating"] is not None:
        try:
            rating = float(data["rating"])
        except (TypeError, ValueError):
            return jsonify({"error": "rating must be a number."}), 400
        if rating < 0 or rating > 10:
            return jsonify({"error": "rating must be between 0 and 10."}), 400
        data["rating"] = rating

    for field in ("platform", "developer", "description"):
        if field in data and data[field] is not None:
            if not isinstance(data[field], str):
                return jsonify({"error": f"{field} must be a string."}), 400
            data[field] = data[field].strip()

    return None


def get_game_or_404(game_id):
    row = get_db().execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    if row is None:
        return None, (jsonify({"error": f"Game with id {game_id} was not found."}), 404)
    return row, None


@app.get("/")
def index():
    return jsonify(
        {
            "name": "GameVault API",
            "version": "1.0",
            "endpoints": {
                "GET /games": "List all games",
                "GET /games/<id>": "Get one game",
                "POST /games": "Create a game",
                "PUT /games/<id>": "Update a game",
                "DELETE /games/<id>": "Delete a game",
            },
        }
    )


@app.get("/games")
def list_games():
    rows = get_db().execute("SELECT * FROM games ORDER BY id").fetchall()
    return jsonify([row_to_game(row) for row in rows]), 200


@app.get("/games/<int:game_id>")
def get_game(game_id):
    row, error = get_game_or_404(game_id)
    if error:
        return error
    return jsonify(row_to_game(row)), 200


@app.post("/games")
def create_game():
    data, error = parse_json()
    if error:
        return error
    invalid = validate_payload(data, partial=False)
    if invalid:
        return invalid

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO games (title, year, genre, platform, developer, rating, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            data["year"],
            data["genre"],
            data.get("platform"),
            data.get("developer"),
            data.get("rating"),
            data.get("description"),
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM games WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(row_to_game(row)), 201


@app.put("/games/<int:game_id>")
def update_game(game_id):
    row, error = get_game_or_404(game_id)
    if error:
        return error
    data, error = parse_json()
    if error:
        return error
    invalid = validate_payload(data, partial=False)
    if invalid:
        return invalid

    db = get_db()
    db.execute(
        """
        UPDATE games
        SET title = ?, year = ?, genre = ?, platform = ?, developer = ?, rating = ?, description = ?
        WHERE id = ?
        """,
        (
            data["title"],
            data["year"],
            data["genre"],
            data.get("platform", row["platform"]),
            data.get("developer", row["developer"]),
            data.get("rating", row["rating"]),
            data.get("description", row["description"]),
            game_id,
        ),
    )
    db.commit()
    updated = db.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    return jsonify(row_to_game(updated)), 200


@app.delete("/games/<int:game_id>")
def delete_game(game_id):
    row, error = get_game_or_404(game_id)
    if error:
        return error
    db = get_db()
    db.execute("DELETE FROM games WHERE id = ?", (game_id,))
    db.commit()
    return jsonify({"message": "Game deleted.", "game": row_to_game(row)}), 200


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
