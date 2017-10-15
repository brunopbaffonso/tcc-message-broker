# tcc-message-broker

With Python 2.7.6 and the MongoDB 3.4 installed

Follow de commands below: 

$ sudo apt-get update

$ sudo apt-get install rabbitmq-server

$ sudo rabbitmq-plugins enable rabbitmq_management

$ sudo apt-get install python-pip

$ sudo pip install pika

$ sudo pip install bottle

$ sudo pip install pymongo==2.8

$ sudo pip install pyfirmata


### Curl Calls

- GET Call: `curl -sG http://localhost:8080/lab/get/<queue>/<id>`

- POST Call: `curl -s -X POST "http://localhost:8080/lab/set/<queue>" --data '{}' -H "Content-Type: application/json"`
