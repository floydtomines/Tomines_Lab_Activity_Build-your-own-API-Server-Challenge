import os
import tempfile
import unittest

import app as gamevault


class GameVaultApiTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp.close()
        gamevault.DATABASE = self.temp.name
        gamevault.init_db()
        self.client = gamevault.app.test_client()

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_list_games(self):
        response = self.client.get("/games")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload), 16)
        self.assertEqual(payload[0]["title"], "Hades")

    def test_get_one_game(self):
        response = self.client.get("/games/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Hades")

    def test_get_missing_game(self):
        response = self.client.get("/games/999")
        self.assertEqual(response.status_code, 404)

    def test_create_game(self):
        response = self.client.post(
            "/games",
            json={
                "title": "Sea of Stars",
                "year": 2023,
                "genre": "RPG",
                "platform": "PC",
                "developer": "Sabotage Studio",
                "rating": 8.8,
                "description": "A throwback turn-based RPG with modern craft.",
            },
        )
        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body["title"], "Sea of Stars")
        self.assertTrue(body["id"] > 16)

    def test_create_missing_field(self):
        response = self.client.post("/games", json={"title": "No Year"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("year", response.get_json()["error"])

    def test_update_game(self):
        response = self.client.put(
            "/games/2",
            json={
                "title": "Celeste",
                "year": 2018,
                "genre": "Precision Platformer",
                "platform": "Nintendo Switch",
                "developer": "Maddy Makes Games",
                "rating": 9.2,
                "description": "Updated catalog copy.",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["genre"], "Precision Platformer")

    def test_update_missing_game(self):
        response = self.client.put(
            "/games/999",
            json={"title": "Ghost", "year": 2020, "genre": "Action"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_game(self):
        response = self.client.delete("/games/16")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Game deleted.")
        follow = self.client.get("/games/16")
        self.assertEqual(follow.status_code, 404)


if __name__ == "__main__":
    unittest.main()
