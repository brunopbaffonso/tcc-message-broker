#!/usr/bin/env python

from pymongo.connection import Connection
from pyfirmata import Arduino, util
import pika
import json

try:
    # Establishes the Connection with the MongoDB and Declares the Collation
    col = Connection("localhost")  # Connection 'c'
    db = col['message_broker']  # Collection 'message_broker'

except Exception, e:
	print str(e)

# Este arquivo sera utilizado para verificar o MongoDB e inserir as mensagens (JSON) com o status de NOVO e inserir na Fila caso ela exista, se nao existir, criar uma nova fila

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

queue_name = "message_broker"

collection = db.queue_name

channel.queue_declare(queue=queue_name)

board = Arduino('/dev/ttyUSB0')
pin_d13 = board.get_pin('d:13:o')
pin_trig = board.get_pin('d:12:i')
pin_echo = board.get_pin('d:11:o')

def getDB():

    query = { "status" : "new" }

    col = db[queue_name]

    try:
        cursor = col.find(query)

        data = []

        for d in cursor:
            data.append(d)

    except Exception, e:
        print str(e)

    return json.dumps(data)


# Declara a funcao de InputV
def setD13():
    try:
        pin_d13.write(1)

    except Exception, e:
        print str(e)

    return { "GPIO" : { "D13" : 1 } }

# Declara a funcao de OutputV
def getDistance():
    try:
        pin_trig.write(0)
        sleep(0.001)
        pin_trig.write(1)
        sleep(0.001)
        pin_trig.write(0)

        # #Read the signal from the sensor: a HIGH pulse whose
        # #duration is the time (in microseconds) from the sending
        # #of the ping to the reception of its echo off of an object.\
        # pinMode(echoPin, INPUT);
        # duration = pulseIn(echoPin, HIGH);

        # #convert the time into a distance
        # (duration/2) / 29.1;

    except Exception, e:
        print str(e)

    return { "GPIO" : { "D12" : "Trigger" , "D11" : "Echo" } }


# Quando o Request e recebido, ele processa e manda o retorno
def on_request(ch, method, props, body):
    n = str(body)

    responseIn = { "set_d13" : setD13(), "get_distance" : getDistance() }
    print(" [.] Set D13: %s " % responseIn['set_d13'])

    print(" [.] Distance: %s " % responseIn['get_distance'])

    # responseIn['_id'] = random_gen()

    print collection.save(responseIn)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="; ".join(responseIn))
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Rodar mais que um processo do servidor, e equilibrar o carga igualmente
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
