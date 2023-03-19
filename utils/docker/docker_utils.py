import json
import docker
import time
import dotenv


class DockerManager:
    def __init__(self):
        # pprint(docker.from_env().containers.list(all=True))
        self.cli = docker.from_env()
        self.containers = self.cli.containers.list(all=True)
        self.containers_dict = {c.image.tags[0]: c for c in self.containers}
        self.config = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../../.env"))
        self.containers = json.load(open(self.config["CONTAINERS"]))

    def start(self, container_name):
        self.containers_dict[container_name].start()
        time.sleep(5)

    def stop(self, container_name):
        self.containers_dict[container_name].stop()
        time.sleep(5)

    def restart(self, container_name):
        self.containers_dict[container_name].restart()

    def pause(self, container_name):
        self.containers_dict[container_name].pause()

    def unpause(self, container_name):
        self.containers_dict[container_name].unpause()

    def start_for_tests(self):
        for container in self.containers_dict:
            self.containers_dict[container].stop()

        time.sleep(5)

        for container in self.containers_dict:
            self.containers_dict[container].start()

        time.sleep(5)

        self.stop(self.containers["basket"])
        self.stop(self.containers["payment"])
        self.stop(self.containers["catalog"])
        self.stop(self.containers["env"])
        self.stop(self.containers["webhook_api"])
        self.stop(self.containers["mvc"])
        self.stop(self.containers["web_status"])
        self.stop(self.containers["redis"])
        self.stop(self.containers["mobile"])
        self.stop(self.containers["web"])
        self.stop(self.containers["webspa"])
        self.stop(self.containers["webhook_client"])
        self.stop(self.containers["mongodb"])
        self.stop(self.containers["seq"])
        self.stop(self.containers["env"])
        self.stop(self.containers["identity"])
        time.sleep(5)


if __name__ == '__main__':
    dm = DockerManager()
    dm.start_for_tests()

