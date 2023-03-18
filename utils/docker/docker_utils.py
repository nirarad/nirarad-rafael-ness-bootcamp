import docker


class DockerManager:
    def __init__(self):
        self.cli = docker.from_env()
        self.containers = self.cli.containers.list(all=True)
        self.containers_dict = {c.image.tags[0]: c for c in self.containers}

    def start(self, container_name):
        """Starting one specific container"""
        self.containers_dict[container_name].start()

    def stop(self, container_name):
        """Stopping one specific container"""
        self.containers_dict[container_name].stop()

    def restart(self, container_name):
        """Restarting one specific container"""
        self.containers_dict[container_name].restart()

    def pause(self, container_name):
        """Pausing one specific container"""
        self.containers_dict[container_name].pause()

    def unpause(self, container_name):
        """Resuming one specific container"""
        self.containers_dict[container_name].unpause()

    def stop_all(self):
        """Stopping all containers"""
        for container in self.containers_dict.values():
            container.stop()


if __name__ == '__main__':
    dm = DockerManager()
    # dm.stop('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.start('eshop/ordering.backgroundtasks:linux-latest')
    #
    # dm.pause('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.unpause('eshop/ordering.api:linux-latest')
    #
    # dm.restart('eshop/ordering.api:linux-latest')
    # print(dm.containers)
    dm.stop_all()
