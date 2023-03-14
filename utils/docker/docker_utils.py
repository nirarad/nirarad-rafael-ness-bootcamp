from time import sleep

import docker


class DockerManager:
    def __init__(self):
        self.cli = docker.from_env()
        self.containers = self.cli.containers.list(all=True)
        self.running_containers = self.cli.containers.list()
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

    def get_container_status(self, container_name):
        return self.cli.containers.get(container_name).status()

    def start_all_containers(self):
        running_containers_amount = len(self.cli.containers.list())
        all_containers_amount = len(self.cli.containers.list(all=True))
        while running_containers_amount != all_containers_amount:
            for container in self.containers:
                current_container = self.cli.containers.get(container.id)
                if current_container.status != "running":
                    current_container.start()
            sleep(5)
            running_containers_amount = len(self.cli.containers.list())
            all_containers_amount = len(self.cli.containers.list(all=True))


if __name__ == '__main__':
    dm = DockerManager()
    dm.start_all_containers()
    # dm.stop('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.start('eshop/ordering.api:linux-latest')
    #
    # dm.pause('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.unpause('eshop/ordering.api:linux-latest')
    #
    # dm.restart('eshop/ordering.api:linux-latest')
