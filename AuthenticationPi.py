import sys
from pymongo import *
import pika
import json
from flask import make_response, request, Response, abort, Flask, jsonify
from flask_discoverer import Discoverer, advertise

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
    
    
'''
------------------------------Flask section-------------------------------------
'''

def check_auth(username, password):
	"""
	This function is called to check if a username /
	password combination is valid.
	"""
	return True if username == "Apple" and password == "Pie" else False
	
def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated
	
@app.route("/add_tag_locker", methods =['POST'])
@requires_auth
def add_tag_locker():
	lock = request.get_json()['locker']
	tag = request.get_json()['tag']
	print("lock: {} tag: {}".format(lock, tag))
	return "tag {} has been added to locker {}".format(tag, lock)
	#add tag to user here
	lockers.find({'lockerID' : lock})['lockerTag'].append(tag)
	return "tag {} has been added to locker {}".format(tag, lock)
	
@app.route("/remove_tag_locker", methods =['DELETE'])
@requires_auth
def remove_tag_locker():
	lock = request.get_json()['locker']
	tag = request.get_json()['tag']
	print("lock: {} tag: {}".format(lock, tag))
	lockers.find({'lockerID' : lock})['lockerTag'].remove(tag)
	return "tag {} has been deleted from locker {}".format(tag, lock)

@app.route("/add_tag_locker", methods =['GET'])
@requires_auth
def get_history():
    return dumps(history)
	
if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
	app.run(host = str(ip), port=5000, debug=True) #IP is based of current pi being used, 5000 is Flask DP