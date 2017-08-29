#!/usr/bin/env python

from bottle import run, route, request, template, Bottle
import pika
import bottle_pika
from pymongo import MongoClient
import json

# Establishes the Connection and Declares the queue
queue_name = "lab_test_01"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue=queue_name)

# Establish connection with MongoDB
c = MongoClient('localhost', 27017)

db = c.message_broker

# Declare the 'Collection' for the document server (JSON files) in the NoSQL database
col = db.queue_name


# 'bottle_pika' library
app = Bottle()
#pika_plugin = bottle_pika.Plugin(pika.URLParameters('amqp://localhost:8080/'))
#app.install(pika_plugin)


@app.route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id": 0}):
		d.update(u)

	return json.dumps(d)


# Example by 'bottle_pika' library on GitHub
@app.route('/bottle/<item>', method='GET')
def bottle(item, mq):
	# Communication Method for RabbitMQ Interaction (Channel)
	mq.basic_publish(exchange='',
					routing_key=props.reply_to,
					properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body="; ".join(responseIn))
	return HTTPResponse(status=200)


@app.route('/hello/<name>', method='GET')
def hello(name='Stranger'):
	return template('Hello {{name}}, how are you?', name=name)


@app.route('lab/<amp>/<offset>/<dutyCycle>/<freq>/<tipo>/<xPos>/<yPos>/<stream>', method='GET')
def lab(amp, offset, dutyCycle, freq, tipo, xPos, yPos, stream):
	# Declares the function of InputVolt
	def inputV():
		return {"valInputV" : 1}

	# Declares the function of OutputVolt
	def outputV():
		return {"valOutputV": 2}

	# Declares the function of Temperature
	def temp():
		return {"valTemp": 3}

	# When the Request is received, it processes and sends the return
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

	# Run more than one server process and Load Balance
	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(on_request, queue=queue_name)

	print(" [x] Awaiting RPC requests")
	channel.start_consuming()

run(app, host='localhost', port=8080, debug=True)
