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

# Declares the class Bottle
app = Bottle()

# RabbitMQ Client
class RpcClient(object):
	# Estabelece a conexao, o canal e delara uma Fila de 'callback'
	def __init__(self):
		self.queue_name = 'lab_test_01'
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

		self.channel = self.connection.channel()

		result = self.channel.queue_declare(exclusive=True)
		self.callback_queue = result.method.queue

		# Inscricao para a fila 'callback', e assim receber retornos do RPC
		self.channel.basic_consume(self.on_response, no_ack=True,
								   queue=self.callback_queue)

	# Para toda mensagem de resposta, ele checa se a 'correlation_id' e o qual esta sendo procurado
	# Se for, ele salva a resposta em 'self.response' e sai do loop
	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	# Define-se a funcao principal 'call' (ele faz a requisicao RPC atual)
	def call(self, s):
		self.response = None

		# Geracao um unico numero 'correlation_id' e salva-o
		# A funcao de callback 'on_responde' ira usar este valor para pegar a resposta apropriada
		self.corr_id = str(uuid.uuid4())

		# Publica-se a mensagem de Request
		# Com duas propriedades: 'reply_to' e 'cerrelation_id'
		self.channel.basic_publish(exchange='',
								   routing_key=self.queue_name,
								   properties=pika.BasicProperties(
									   reply_to=self.callback_queue,
									   correlation_id=self.corr_id,
								   ),
								   body=str(s))
		# Aguarda a resposta apropriada chegar
		while self.response is None:
			self.connection.process_data_events()

		# Retorna a resposta para o usuario
		return str(self.response)

#
@app.route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id": 0}):
		d.update(u)

	return json.dumps(d)

# GET data from MongoDB
@app.route('/lab/get/<queue>/<id>', method='GET')
def get_data(queue, id):

	# Validar se ID existe no Banco, se nao existir, criar Excecao

	query = { "_id" : id }

	col = db[queue]

	try:
		cursor = col.find(query)

		data = []

		for d in cursor:
			data.append(d)

	except Exception, e:
		print str(e)

	mq_client = RpcClient()

	response = mq_client.call(data)


	return json.dumps(data)

# SET data to MongoDB
@app.route('/lab/set/<queue>', method='POST')
def set_data(queue):

	# Validar se o dado e um JSON, se nao for, tentar transforma-lo em um JSON
    # Implementar o parametro STATUS

	# status = "new"  # new, ready, run, wait, finish

	data = request.json

	col = db[queue]

	col.insert(data)

	mq_client = RpcClient()

	response = mq_client.call(data)

run(app, host='localhost', port=8080, debug=True)
