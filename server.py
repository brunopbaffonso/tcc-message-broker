#!/usr/bin/env python

from bottle import run, route, request, template
import pika
import bottle_pika
from pymongo import MongoClient
import json

# Estabelece a conexao e declara a Fila
queue_name = "lab_test_01"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue=queue_name)

# Estabelece conexao com o MongoDB
c = MongoClient('localhost', 27017)

db = c.message_broker

# Declara a 'Collection' para armazenamento dos documentos (arquivos JSON) no banco NoSQL
col = db.queue_name


# bottle_pika
app = bottle.Bottle()
pika_plugin = bottle_pika.Plugin(pika.URLParameters('amqp://localhost/'))
app.install(pika_plugin)


@app.route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id": 0}):
		d.update(u)

	return json.dumps(d)

@app.route('/hello', method='GET')
def hello(mq):
	# Metodo de Comunicacao para interacao com RabbitMQ (Channel)
	mq.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="; ".join(responseIn))
	return HTTPResponse(status=200)


@app.route('lab/<amp>/<offset>/<dutyCycle>/<freq>/<tipo>/<xPos>/<yPos>/<stream>', method='GET')
def lab(amp, offset, dutyCycle, freq, tipo, xPos, yPos, stream):

	# Declara a funcao de InputV
	def inputV():
		return {"valInputV" : 1}

	# Declara a funcao de OutputV
	def outputV():
		return {"valOutputV": 2}

	# Declara a funcao de Temperatura
	def temp():
		return {"valTemp": 3}

	# Quando o Request e recebido, ele processa e manda o retorno
	def on_request(ch, method, props, body):
		n = str(body)

		responseIn = { "input_v" : inputV(), "output_v" : outputV(), "temp" : temp() }
		print(" [.] InputV: %s " % responseIn['input_v'])

		print(" [.] OutputV: %s " % responseIn['output_v'])

		print(" [.] Temperatura: %s " % responseIn['temp'])

		# responseIn['_id'] = random_gen()

		print col.save(responseIn)

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

run(host='localhost', port=8080, debug=True)
