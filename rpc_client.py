#!/usr/bin/env python
import pika
import uuid
import json

class LabRpcClient(object):
    # Estabelece a conexao, o canal e delara uma Fila de 'callback'
    def __init__(self):
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
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(s))
	# Aguarda a resposta apropriada chegar
        while self.response is None:
            self.connection.process_data_events()

	# Retorna a resposta para o usuario
        return str(self.response)

lab_rpc = LabRpcClient()

amp = raw_input("Amplitude[DBL]: ")
offset = raw_input("Offset[DBL]: ")
dutyCycle = raw_input("DutyCycle[DBL]: ")
freq = raw_input("Freq[DBL]: ")
tipo = raw_input("Type[STRING]: ")
xPos = raw_input("Xpos[DBL]: ")
yPos = raw_input("Ypos[DBL]: ")
stream = raw_input("Stream[STRING]: ")
lista = [amp, offset, dutyCycle, freq, tipo, xPos, yPos, stream]
s = json.dumps(lista)
response = lab_rpc.call(s)
print(" [.] Got %r" % response)
