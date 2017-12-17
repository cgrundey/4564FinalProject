from flask import make_response, request, Response, abort, Flask, jsonify
from flask_discoverer import Discoverer, advertise
from functools import wraps
from pymongo import *
from bson.json_util import dumps
import socket
import sys

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
history = db.history
lockers = db.lockers

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