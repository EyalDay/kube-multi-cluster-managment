from locust import HttpUser, task, between
import random
import time

class GetObjectUser(HttpUser):
    wait_time = between(20, 30)

    @task
    def get_object(self):
        movie = random.randint(0, 2)
        for movie_segment in range(10):
            obj_hash = f'{movie}_{movie_segment}'
            self.client.get(f'/get_object?obj_hash={obj_hash}&obj_size_mb=100&obj_ttl_sec=60')
            time.sleep(2)

    #@task
    def health(self):
        self.client.get('/health')