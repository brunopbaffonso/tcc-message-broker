# Estabelece conexao com MongoDB
from pymongo.connection import Connection
connection = Connection("localhost")
 
db = connection.message_broker

# Lista os dados
cursor = db.message_broker.find()
for d in cursor:
    print d
