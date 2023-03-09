from pprint import pprint

import docker
import time


class DockerManager:
    def __init__(self):
        # pprint(docker.from_env().containers.list(all=True))
        self.cli = docker.from_env()
        self.containers = self.cli.containers.list(all=True)
        self.containers_dict = {c.image.tags[0]: c for c in self.containers}

    def start(self, container_name):
        self.containers_dict[container_name].start()

    def stop(self, container_name):
        self.containers_dict[container_name].stop()

    def restart(self, container_name):
        self.containers_dict[container_name].restart()

    def pause(self, container_name):
        self.containers_dict[container_name].pause()

    def unpause(self, container_name):
        self.containers_dict[container_name].unpause()


if __name__ == '__main__':
    dm = DockerManager()

    #dm.stop('eshop/ordering.api:linux-latest')
    #time.sleep(1)
    dm.start('eshop/ordering.api:linux-latest')
    dm.start('eshop/ordering.backgroundtasks:linux-latest')
    dm.start('eshop/identity.api:linux-latest')
    dm.start('mcr.microsoft.com/mssql/server:2019-latest')
    dm.start('rabbitmq:3-management-alpine')
    dm.start('eshop/basket.api:linux-latest')


    #dm.pause('eshop/ordering.api:linux-latest')
    #time.sleep(1)
    # dm.unpause('eshop/ordering.api:linux-latest')
    # dm.unpause('eshop/ordering.backgroundtasks:linux-latest')
    # dm.unpause('eshop/identity.api:linux-latest')
    # dm.unpause('mcr.microsoft.com/mssql/server:2019-latest')
    # dm.unpause('rabbitmq:3-management-alpine')

    # dm.restart('rabbitmq:3-management-alpine')
