# GameVault API

REST API for a hand-crafted video game catalog. Built with **Flask** and **SQLite** for the ITCC 14 Build Your Own API Server challenge.

No frontend. Test with curl, PowerShell, or the included Postman collection.

## Stack

- Python 3.13
- Flask
- SQLite (`games.db` is created automatically on first run)

## Setup

```bash
cd gamevault-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The server starts at `http://127.0.0.1:5000`.

The database is seeded with **16 original catalog entries** (title, year, genre, platform, developer, rating, description). This data was written by hand and was not copied from a public games API.

## Resource

Base path: `/games`

Required fields on `POST` and `PUT`: `title`, `year`, `genre`

Optional fields: `platform`, `developer`, `rating` (0–10), `description`

## Endpoints

| Method | Path | Success | Error |
| --- | --- | --- | --- |
| GET | `/games` | 200 list of games | — |
| GET | `/games/<id>` | 200 one game | 404 if missing |
| POST | `/games` | 201 created game | 400 missing/invalid fields |
| PUT | `/games/<id>` | 200 updated game | 400 invalid body, 404 if missing |
| DELETE | `/games/<id>` | 200 deleted game | 404 if missing |

`GET /` returns a short index of these routes.

## Sample requests and responses

Use a second terminal while `python app.py` is running. On Windows, `curl.exe` is the curl client.

### GET `/games`

```bash
curl.exe -i http://127.0.0.1:5000/games
```

Sample response (`200`):

```json
[
  {
    "id": 1,
    "title": "Hades",
    "year": 2020,
    "genre": "Roguelike",
    "platform": "PC",
    "developer": "Supergiant Games",
    "rating": 9.3,
    "description": "Escape the Underworld as Zagreus in fast, story-rich runs."
  }
]
```

### GET `/games/1`

```bash
curl.exe -i http://127.0.0.1:5000/games/1
```

Sample response (`200`):

```json
{
  "id": 1,
  "title": "Hades",
  "year": 2020,
  "genre": "Roguelike",
  "platform": "PC",
  "developer": "Supergiant Games",
  "rating": 9.3,
  "description": "Escape the Underworld as Zagreus in fast, story-rich runs."
}
```

Missing id (`404`):

```bash
curl.exe -i http://127.0.0.1:5000/games/999
```

```json
{ "error": "Game with id 999 was not found." }
```

### POST `/games`

```bash
curl.exe -i -X POST http://127.0.0.1:5000/games -H "Content-Type: application/json" -d "{\"title\":\"Sea of Stars\",\"year\":2023,\"genre\":\"RPG\",\"platform\":\"PC\",\"developer\":\"Sabotage Studio\",\"rating\":8.8,\"description\":\"A throwback turn-based RPG with modern craft.\"}"
```

Sample response (`201`):

```json
{
  "id": 17,
  "title": "Sea of Stars",
  "year": 2023,
  "genre": "RPG",
  "platform": "PC",
  "developer": "Sabotage Studio",
  "rating": 8.8,
  "description": "A throwback turn-based RPG with modern craft."
}
```

Bad request (`400`) when a required field is missing:

```bash
curl.exe -i -X POST http://127.0.0.1:5000/games -H "Content-Type: application/json" -d "{\"title\":\"Incomplete Game\"}"
```

```json
{
  "error": "Missing required field(s): year, genre.",
  "required": ["title", "year", "genre"]
}
```

### PUT `/games/2`

```bash
curl.exe -i -X PUT http://127.0.0.1:5000/games/2 -H "Content-Type: application/json" -d "{\"title\":\"Celeste\",\"year\":2018,\"genre\":\"Precision Platformer\",\"platform\":\"Nintendo Switch\",\"developer\":\"Maddy Makes Games\",\"rating\":9.2,\"description\":\"Updated catalog copy.\"}"
```

Sample response (`200`):

```json
{
  "id": 2,
  "title": "Celeste",
  "year": 2018,
  "genre": "Precision Platformer",
  "platform": "Nintendo Switch",
  "developer": "Maddy Makes Games",
  "rating": 9.2,
  "description": "Updated catalog copy."
}
```

### DELETE `/games/16`

```bash
curl.exe -i -X DELETE http://127.0.0.1:5000/games/16
```

Sample response (`200`):

```json
{
  "message": "Game deleted.",
  "game": {
    "id": 16,
    "title": "Outer Wilds",
    "year": 2019,
    "genre": "Adventure",
    "platform": "PC",
    "developer": "Mobius Digital",
    "rating": 9.3,
    "description": "Pilot a tiny ship through a solar system that resets every 22 minutes."
  }
}
```

## Postman

Import `postman_collection.json`. The `baseUrl` variable defaults to `http://127.0.0.1:5000`.

For Canvas, capture one screenshot per method (GET, POST, PUT, DELETE) with the request and response visible.

## Tests

```bash
python -m unittest test_api.py
```

## Optional bonus: deploy on Render

This is extra credit. A live URL is not required for the main submission.

1. Push this repo to GitHub (public).
2. Create a [Render](https://render.com) Web Service from the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add the live URL here after deploy, then test:

```bash
curl.exe -i https://YOUR-SERVICE.onrender.com/games
```

SQLite on a free host is wiped on restart. That is fine for a class demo. For a durable bonus deploy, switch the database to a hosted Postgres or MongoDB instance.

## GitHub

Create a public repository and push:

```bash
git add .
git commit -m "Add GameVault REST API with Flask and SQLite"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gamevault-api.git
git push -u origin main
```
