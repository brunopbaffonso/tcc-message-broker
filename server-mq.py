#!/usr/bin/env python
from pyfirmata import Arduino, util
import pika


try:
    # Establishes the Connection with the RabbitMQ and Declares the Channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))  # RabbitMQ Connection
    channel = connection.channel()  # RabbitMQ Channel in Connection
except Exception, e:
	print str(e)


# Set the Queue Name
queue_name = "message_broker"

# Set the Queue in the Channel
channel.queue_declare(queue=queue_name)

# Set the Arduino Board
board = Arduino('/dev/ttyUSB0')
# Set the Digital GPIO 13 to Output
pin_d13 = board.get_pin('d:13:o')


# Define the SET 1 (one) function to MongoDB
def setD13_on():
    try:
        pin_d13.write(1)

    except Exception, e:
        print str(e)

    return { "GPIO" : { "D13" : "On" } }


# Define the SET 0 (zero) function to MongoDB
def setD13_off():
    try:
        pin_d13.write(0)

    except Exception, e:
        print str(e)

    return { "GPIO" : { "D13" : "Off" } }


# The Request is Received, it is Processed and Send the Response
def on_request(ch, method, props, body):
    json_string = str(body)

    if json_string == "{u'status': u'new', u'state': u'on'}":
        responseIn = {"setD13_on": setD13_on()}

        print(" [.] Set D13: %s " % responseIn['setD13_on'])

    else:
        responseIn = {"setD13_off": setD13_off()}

        print(" [.] Set D13: %s " % responseIn['setD13_off'])


    # responseIn['_id'] = random_gen()

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="; ".join(responseIn))
    ch.basic_ack(delivery_tag = method.delivery_tag)


# Run more than one Process in Server and Load Balancing
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)


print(" [x] Awaiting RPC requests")
channel.start_consuming()
