import docker
from pprint import pprint

class DockerManager:
    def __init__(self):
        self.cli = docker.from_env()
        self.containers = self.cli.containers.list()
        self.containers_dict = {c.image.tags[0]: c for c in self.containers}
        
    def start_app(self):
        for container in self.containers:
            container.start()
            
    def start(self, container_name):
        self.containers_dict[container_name].start()

    def stop(self, container_name):
        self.containers_dict[container_name].stop()
    
    def shutdown(self):
        for container in self.containers:
            container.stop()

    def restart(self, container_name):
        self.containers_dict[container_name].restart()

    def pause(self, container_name):
        self.containers_dict[container_name].pause()

    def unpause(self, container_name):
        self.containers_dict[container_name].unpause()
