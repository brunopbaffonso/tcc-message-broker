#!/usr/bin/env python
import pika
import json

# Estabelece conexao com MongoDB
from pymongo.connection import Connection
connection = Connection("localhost")
 
db = connection.foo

# Estabelece a conexao e declara a Fila
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

# Declara a funcao de InputV
def inputV():
    return "1"

# Declara a funcao de OutputV
def outputV():
    return "2"

# Declara a funcao de Temperatura
def temp():
    return "3"

# Quando o Request e recebido, ele processa e manda o retorno
def on_request(ch, method, props, body):
    n = str(body)

    responseIn = inputV()
    db.foo.save=(responseIn) # Variavel salva no BD
    print(" [.] InputV: %s" % responseIn)

    responseOut = outputV()
    db.foo.save=(responseOut)
    print(" [.] OutputV: %s" % responseOut)

    responseTemp = temp()
    db.foo.save=(responseTemp)
    print(" [.] Temperatura: %s" % responseTemp)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="-".join([responseIn, responseOut, responseTemp]))
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Rodar mais que um processo do servidor, e equilibrar o carga igualmente
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()
