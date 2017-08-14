#!/usr/bin/env python

from bottle import run, route, request
from pymongo import MongoClient
import json
import pika


c = MongoClient('localhost', 27017)

db = c.message_broker

col = db.queue_name

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

queue_name = "lab_test_01"

channel.queue_declare(queue=queue_name)

@route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id" : 0}):
		d.update(u)

	return json.dumps(d)

	run(host='localhost', port=8080, debug=True)


@route('/hello', method='GET')
def index():
	app = Bottle()

	@app.route('/hello')
	def hello():
		return "Hello World!"

	run(host='localhost', port=8080, debug=True)


@route('/lab', method='GET')
def index():
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

	run(host='localhost', port=8080, debug=True)
