#!/usr/bin/env python

from bottle import run, route, request
from pymongo import MongoClient
import json

c = MongoClient('localhost', 27017)

db = c.message_broker

col = db.queue_name

@route('/', method='GET')
def index():
	print request.query.id
	d = dict()
	for u in col.find({}, {"_id" : 0}):
		d.update(u)

	return json.dumps(d) 

run(host='localhost', port=8080, debug=True)
