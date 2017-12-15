import sys
from pymongo import *
import pika
import json
from flask import make_response, request, Response, abort, Flask, jsonify
from flask_discoverer import Discoverer, advertise

#flask initialization
app = Flask(__name__)
discoverer = Discoverer(app)

# MongoDB initialization
try:
	client = MongoClient('localhost', 27017)
	db = client.BlacksburgLockers
except:
	sys.exit("Error connecting to MongoDB")
# Collections
credentials = db.users
history = db.history
lockers = db.lockers

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
	channe.queue_purge(queue=locker['lockerID'])
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

# message = json.dumps(data)
def master_callback(ch, method, properties, body):
	data = json.loads(body)
	if data['lockerID'] == method.routing_key: # should always be true
		the_user = users.find( {'lockerID':data['lockerID']} )
		# Check if user exists with specified lockerID
		if the_user['username'] == data['username'] and the_user['password'] == data['password']:
			# publish success back to rabbitExchange with method.routing_key
		else:
			# publish failure back to rabbitExchange with method.routing_key

for locker in lockers.find():
	def (ch)

channel.basic_consume(master_callback, queue="masterQ", no_ack=True)
for locker in lockers.find():
	
	channel.basic_consume(, queue=locker['lockerID'], no_ack=True)

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
	
@app.route("/add_tag_user", methods =['POST'])
@requires_auth
def add_tag_user():
	usr = request.get_json()['user']
	tag = request.get_json()['tag']
	print("usr: {}tag: {}".format(usr, tag))
	#add tag to user here

@app.route("/remove_tag_user", methods =['DELETE'])
@requires_auth
def remove_tag_user():
	usr = request.get_json()['user']
	tag = request.get_json()['tag']
	#remove tag from user here
	
@app.route("/add_locker_user", methods =['POST'])
@advertise()
@requires_auth
def add_locker_user():
	usr = request.get_json()['user']
	lock = request.get_json()['locker']
	#add locker to user here

@app.route("/remove_locker_user", methods =['DELETE'])
@advertise()
@requires_auth
def remove_locker_user():
	usr = request.get_json()['user']
	lock = request.get_json()['locker']
	#remove locker from user here

