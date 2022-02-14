from locust import HttpUser, task, between
import random
class GetObjectUser(HttpUser):
    wait_time = between(20, 30)

    @task
    def get_object(self):
        obj_hash = random.randint(0, 130)
        self.client.get(f'/get_object?obj_hash={obj_hash}&obj_size_mb=1&obj_ttl_sec=1')

    #@task
    def health(self):
        self.client.get('/health')