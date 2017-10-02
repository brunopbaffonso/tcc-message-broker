#!/usr/bin/env python

from bottle import run, route, request, template, Bottle
from pymongo.connection import Connection
import json
import uuid
import pika


try:
	# Establishes the Connection with the MongoDB and Declares the Collation
	col = Connection("localhost") # Connection 'c'
	db = col['message_broker'] # Collection 'message_broker'

except Exception, e:
	print str(e)


# Set the class Bottle
app = Bottle()


# RabbitMQ Client
class RpcClient(object):
	# Estabelece a conexao, o canal e delara uma Fila de 'callback'
	def __init__(self):
		self.queue_name = 'message_broker'
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

		self.channel = self.connection.channel()

		result = self.channel.queue_declare(exclusive=True)
		self.callback_queue = result.method.queue

		# Inscricao para a fila 'callback', e assim receber retornos do RPC
		self.channel.basic_consume(self.on_response, no_ack=True,
								   queue=self.callback_queue)

	# For every response message, it checks if 'correlational_id' is being searched
	# If it's true, it saves the response in 'self.response' and exits the loop
	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	# Define the main function 'call' (it does the current RPC request)
	def call(self, s):
		self.response = None

		# Generate a unique 'correlation_id' number and save it
		# The callback function 'on_responde' will use this value to get the appropriate answer
		self.corr_id = str(uuid.uuid4())

		# Post the Request message
		# With Two Properties: 'reply_to' and 'cerrelation_id'
		self.channel.basic_publish(exchange='',
								   routing_key=self.queue_name,
								   properties=pika.BasicProperties(
									   reply_to=self.callback_queue,
									   correlation_id=self.corr_id,
								   ),
								   body=str(s))

		# Wait for the appropriate response to arrive
		while self.response is None:
			self.connection.process_data_events()

		# Returns the response to the user
		return str(self.response)


# Index
@app.route('/', method='GET')
def index():
	print "Hello World"

	return 0

# GET all data from MongoDB
@app.route('/lab/get/message_broker', method='GET')
def get_all_data():

	# col = db[queue]

	try:
		cursor = db.message_broker.find()
		for d in cursor:
			print d

	except Exception, e:
		print str(e)

	return 1


# GET data from MongoDB
@app.route('/lab/get/message_broker/<id>', method='GET')
def get_data(id):

	# col = db[queue]

	try:
		data = db.message_broker.find( { "_id": id } )
		print data

	except Exception, e:
		print str(e)

	return json.dumps(data)


# SET data to MongoDB
@app.route('/lab/set/<queue>', method='POST')
def set_data(queue):

	data = request.json

	# Create the RabbitMQ Client Object
	mq_client = RpcClient()
	mq_client.call(data)

	# Save the 'data' JSON in Collation
	col = db[queue]
	col.insert(data)

	return json.dumps(data)


run(app, host='localhost', port=8080, debug=True)
