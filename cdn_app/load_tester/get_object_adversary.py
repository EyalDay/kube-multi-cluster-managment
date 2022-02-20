from locust import HttpUser, task, between

import time

class GetObjectAdversary(HttpUser):

    @task
    def get_object(self):
        for movie in range(2):
            for segment in range(10):
                obj_hash = f'{movie}_{segment}'
                self.client.get(f'/get_object?obj_hash={obj_hash}&obj_size_mb=100&obj_ttl_sec=60')
                time.sleep(2)

    #@task
    def health(self):
        self.client.get('/health')