"get this from RFID sensor"
lockerID = ''
auth_key = ''

import pika

credentials = pika.PlainCredentials('Apple', 'Pie')
parameters = pika.ConnectionParameters(sys.argv[1], virtual_host='team_13_host', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.basic_publish(exchange='rabbitExchange', routing_key = lockerID, body = auth_key)