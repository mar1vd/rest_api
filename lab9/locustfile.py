from locust import HttpUser, task, between


class BooksApiUser(HttpUser):
    wait_time = between(1, 2)
    username = "admin"
    password = "secret"
    token = None

    def on_start(self):
        response = self.client.post(
            "/auth/token",
            data={"username": self.username, "password": self.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    @task
    def get_books(self):
        self.client.get(
            "/books",
            headers={"Authorization": f"Bearer {self.token}"},
            params={"skip": 0, "limit": 10},
            name="GET /books",
        )
