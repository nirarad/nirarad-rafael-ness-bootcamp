
routingkey = ''


def callback(ch, method, properties, body):
    global routingkey
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")

    # routingkey = ''
    # Saves the routing key of the message that entered to consume
    routingkey = method.routing_key
    # Close the listening
    ch.close()
    # if routingkey != '':
    #     ch.stop_consuming()




def check_routing_key(routing_key):
    """
    A function that compares the routing key that was CONSUME
    and the routing key sent to it
    :param routing_key:
    :return:
    """
    if routingkey == routing_key:
        return True
    return False


if __name__ == '__main__':
    pass

