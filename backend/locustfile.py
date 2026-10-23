from locust import HttpUser, between, task


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def health(self):
        self.client.get("/api/v1/health/")
