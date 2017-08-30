# tcc-message-broker

With Python 2.7.6 and the MongoDB 3.2 installed

Follow de commands below: 

$ sudo apt-get update

$ sudo apt-get install python-pip

$ sudo pip install pika

$ sudo pip install bottle

$ sudo pip install pymongo==2.8

### Curl Calls

- GET Call:
 - `curl -sG http://localhost:8080/lab/<queue>/<id>`

- POST Call:
 - `curl -s -X POST "http://localhost:8080/lab/add/<queue>" --data '{}' -H "Content-Type: application/json"`
