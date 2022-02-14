from locust import HttpUser, task, between

class GetObjectAdversary(HttpUser):

    @task
    def get_object(self):
        for obj_hash in range(130):
            self.client.get(f'/get_object?obj_hash={obj_hash}&obj_size_mb=1&obj_ttl_sec=1')

    #@task
    def health(self):
        self.client.get('/health')