import sys
from pymongo import *
import pika
import json

# MongoDB initialization
try:
	client = MongoClient('localhost', 27017)
	db = client.team_13
except:
	sys.exit("Error connecting to MongoDB")
# Collections
lockers = db.lockers
history = db.history

# RabbitMQ initialization
rabbitUname = 'Apple'
rabbitPword = 'Pie'
rabbitVhost = 'team_13_host'
rabbitExchange = 'team_13'
try:
	credentials = pika.PlainCredentials(rabbitUname, rabbitPword)
	parameters = pika.ConnectionParameters('localhost', 5672, rabbitVhost, credentials)
	rmqConnection = pika.BlockingConnection(parameters)
	channel = rmqConnection.channel()
	channel.exchange_declare(exchange=rabbitExchange, exchange_type="direct")
except:
	sys.exit("Unable to connect to RabbitMQ Server")
print("[x] Connected to vhost '" + rabbitVhost + "' on RMQ server at 'localhost' as user '" + rabbitUname + "'")
# Set up queues
channel.queue_declare(queue="masterQ")
channel.queue_purge(queue="masterQ")
# Create queue for each locker to post
for locker in lockers.find():
	channel.queue.declare(queue=locker['lockerID'])
	channel.queue_purge(queue=locker['lockerID'])
	channel.queue_unbind(queue=locker['lockerID'], 
				exchange=rabbitExchange, 
				routing_key=locker['lockerID'])
	channel.queue_bind(exchange=rabbitExchange, 
				queue=locker['lockerID'], 
				routing_key=locker['lockerID'])
	channel.queue_unbind(queue="masterQ", 
				exchange=rabbitExchange, 
				routing_key=locker['lockerID'])
	channel.queue_bind(exchange=rabbitExchange,
				queue="masterQ",
				routing_key=locker['lockerID'])

def master_callback(ch, method, properties, body):
	# Check if user exists with specified lockerID
	if body in lockers['lockerTag']:
		channel.basic_publish(exchange='team_13', routing_key=method.routing_key, body='success')
	else:
		channel.basic_publish(exchange='team_13', routing_key=method.routing_key, body='failure')
	channel.stop_consuming()

channel.basic_consume(master_callback, queue="masterQ", no_ack=True)
channel.start_consuming()

for locker in lockers.find():
	channel.basic_consume(master_callback, queue=locker['lockerID'], no_ack=True)
	channel.start_consuming()