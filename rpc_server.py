#!/usr/bin/env python
import pika
import json

# Estabelece conexao com MongoDB
from pymongo import MongoClient
db_connection = MongoClient("localhost", 27017)
 
db = db_connection.message_broker

# Estabelece a conexao e declara a Fila
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

queue_name = "lab_test_01"

collection = db.queue_name

channel.queue_declare(queue=queue_name)

# Declara a funcao de InputV
def inputV():
    return {"valA" : 1, "valB" : 2, "valC" : 3}

# Declara a funcao de OutputV
def outputV():
    return "2"

# Declara a funcao de Temperatura
def temp():
    return "3"

# Quando o Request e recebido, ele processa e manda o retorno
def on_request(ch, method, props, body):
    n = str(body)

    responseIn = { "input_v" : inputV(), "output_v" : outputV(), "temp" : temp() }
    print(" [.] InputV: %s" % responseIn['input_v'])

    print(" [.] OutputV: %s" % responseIn['output_v'])

    print(" [.] Temperatura: %s" % responseIn['temp'])

    #responseIn['_id'] = random_gen()

    print collection.save(responseIn)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="-".join(responseIn['input_v']))
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Rodar mais que um processo do servidor, e equilibrar o carga igualmente
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
