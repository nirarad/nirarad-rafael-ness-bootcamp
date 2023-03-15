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

    def start_for_tests(self):
        for container in self.containers_dict:
            self.containers_dict[container].stop()

        time.sleep(5)

        for container in self.containers_dict:
            self.containers_dict[container].start()

        time.sleep(5)

        self.stop('eshop/basket.api:linux-latest')
        self.stop('eshop/payment.api:linux-latest')
        self.stop('eshop/catalog.api:linux-latest')
        self.stop('envoyproxy/envoy:v1.11.1')
        self.stop('eshop/webhooks.api:linux-latest')
        self.stop('eshop/webmvc:linux-latest')
        self.stop('eshop/webstatus:linux-latest')
        self.stop('redis:alpine')
        self.stop('eshop/mobileshoppingagg:linux-latest')
        self.stop('eshop/webshoppingagg:linux-latest')
        self.stop('eshop/webspa:linux-latest')
        self.stop('eshop/webhooks.client:linux-latest')
        self.stop('mongo:latest')
        self.stop('datalust/seq:latest')
        self.stop('envoyproxy/envoy:v1.11.1')
        self.start('eshop/identity.api:linux-latest')
        time.sleep(5)

    def restart_to_test(self):
        self.restart('eshop/ordering.api:linux-latest')
        self.restart('eshop/ordering.backgroundtasks:linux-latest')
        self.restart('eshop/identity.api:linux-latest')
        self.restart('mcr.microsoft.com/mssql/server:2019-latest')
        self.restart('rabbitmq:3-management-alpine')
        self.restart('eshop/ordering.signalrhub:linux-latest')


    def stop_not_necceery(self):
        self.stop('eshop/basket.api:linux-latest')
        self.stop('eshop/payment.api:linux-latest')
        self.stop('eshop/catalog.api:linux-latest')
        self.stop('envoyproxy/envoy:v1.11.1')
        self.stop('eshop/webhooks.api:linux-latest')
        self.stop('eshop/webmvc:linux-latest')
        self.stop('eshop/webstatus:linux-latest')
        self.stop('redis:alpine')
        self.stop('eshop/mobileshoppingagg:linux-latest')
        self.stop('eshop/webshoppingagg:linux-latest')
        self.stop('eshop/webspa:linux-latest')
        self.stop('eshop/webhooks.client:linux-latest')
        self.stop('mongo:latest')
        self.stop('datalust/seq:latest')


if __name__ == '__main__':
    dm = DockerManager()
    dm.start_for_tests()
    # dm.stop_not_necceery()
    # dm.restart_to_test()
    # dm.stop('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.start('eshop/ordering.api:linux-latest')
    # dm.start('eshop/ordering.backgroundtasks:linux-latest')
    # dm.start('eshop/identity.api:linux-latest')
    # dm.start('mcr.microsoft.com/mssql/server:2019-latest')
    # dm.start('rabbitmq:3-management-alpine')

    # dm.pause('eshop/ordering.api:linux-latest')
    # time.sleep(1)
    # dm.unpause('eshop/ordering.api:linux-latest')
    # dm.unpause('eshop/ordering.backgroundtasks:linux-latest')
    # dm.unpause('eshop/identity.api:linux-latest')
    # dm.unpause('mcr.microsoft.com/mssql/server:2019-latest')
    # dm.unpause('rabbitmq:3-management-alpine')

    # dm.restart('rabbitmq:3-management-alpine')
