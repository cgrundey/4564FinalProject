from flask import make_response, request, Response, abort, Flask, jsonify
from functools import wraps
from pymongo import *
import socket
import sys
from pprint import pprint
import json
from bson import BSON
from bson import json_util

#flask initialization
app = Flask(__name__)

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
	lockerID = request.get_json()['locker']
	tag = request.get_json()['tag']
	print("lock: {} tag: {}".format(lockerID, tag))
	#add tag to user here
	print(lockers)
	pprint(lockers.find_one({}))
	lockers.update({"lockerID": lockerID}, {"$push": {"lockerTags": tag}})
	
	'''
	if db.lockers.find({"lockerID": str(lockerID)}).count() > 0:
		print('here')
		db.lockers.update({"lockerID": lockerID}, {"$push": {"tags": tag}})
	else:
		print('here2')
	'''
	return "tag {} has been added to locker {}".format(tag, lockerID)
	
@app.route("/remove_tag_locker", methods =['DELETE'])
@requires_auth
def remove_tag_locker():
	lockerID = request.get_json()['locker']
	tag = request.get_json()['tag']
	print("lock: {} tag: {}".format(lockerID, tag))
	if db.lockers.find({"lockerID": lockerID}).count() > 0:
		db.lockers.update({"lockerID": lockerID}, {"$pull": {"lockerTags": tag}})
	return "tag {} has been deleted from locker {}".format(tag, lockerID)

@app.route("/history", methods =['GET'])
@requires_auth
def get_history():
	return json_util.dumps(history.find({}), sort_keys=True, indent=4, default=json_util.default)
	
#add to auth time.asctime( time.localtime(time.time()) )    ?
# MongoDB initialization
try:
	client = MongoClient('localhost', 27017)
	db = client.team_13
except:
	sys.exit("Error connecting to MongoDB")
# Collections
history = db.history
lockers = db.lockers
	
if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
	app.run(host = str(ip), port=5000, debug=True) #IP is based of current pi being used, 5000 is Flask DP