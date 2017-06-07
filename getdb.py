# Estabelece conexao com MongoDB
from pymongo.connection import Connection
connection = Connection("localhost")
 
db = connection.foo

# Lista os dados
cursor = db.foo.find()
for d in cursor:
    print d
