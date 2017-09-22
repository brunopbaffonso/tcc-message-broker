#!/usr/bin/env python

from bottle import run, route, request, template, Bottle
from pymongo.connection import Connection
import json

try:
	# Establishes the Connection with the MongoDB and Declares the Collation
	col = Connection("localhost") # Connection 'c'
	db = col['message_broker'] # Collection 'message_broker'

except Exception, e:
	print str(e)

# Declares the class Bottle
app = Bottle()

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



run(app, host='localhost', port=8080, debug=True)
