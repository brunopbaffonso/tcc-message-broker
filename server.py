#!/usr/bin/env python

from bottle import run, route, request, template, Bottle
from pymongo.connection import Connection
import json

# Establishes the Connection and Declares the queue
c = Connection("localhost")
db = c['message_broker']

app = Bottle()

@app.route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id": 0}):
		d.update(u)

	return json.dumps(d)

@app.route('/lab/<queue>/<id>', method='GET')
def get_data(queue, id):
	####
	query = {"_id" : id}
	col = db[queue]
	cursor = col.find(query)

	data = []

	for d in cursor:
		data.append(d)

	return json.dumps(data)

@app.route('/lab/add/<queue>', method='POST')
def save_data(queue=False):

	data = request.json

	col = db[queue]

	col.insert(data)

run(app, host='localhost', port=8080, debug=True)
