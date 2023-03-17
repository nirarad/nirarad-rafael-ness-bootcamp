import time

from utils.rabbitmq.rabbitmq_send import RabbitMQ


def clear_all_queues_msg():
    queues = ["BackgroundTasks", "Basket", "Catalog", "Ordering", "Ordering.signalrhub", "Payment", "Webhooks"]
    rbtMQ = RabbitMQ()
    for i in queues:
        rbtMQ.delete_msg_on_queue(i)
    time.sleep(3)
