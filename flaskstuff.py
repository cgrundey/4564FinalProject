from flask import make_response, request, Response, abort, Flask, jsonify
from flask_discoverer import Discoverer, advertise
from functools import wraps
import socket

#flask initialization
app = Flask(__name__)
discoverer = Discoverer(app)

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
	print("usr: {} tag: {}".format(usr, tag))
	return "tag {} has been added to user {}".format(usr, tag)
	#add tag to user here

@app.route("/remove_tag_user", methods =['DELETE'])
@requires_auth
def remove_tag_user():
	usr = request.get_json()['user']
	tag = request.get_json()['tag']
	print("usr: {} tag: {}".format(usr, tag))
	return "tag {} has been deleted from user {}".format(usr, tag)
	#remove tag from user here
	
@app.route("/add_locker_user", methods =['POST'])
@requires_auth
def add_locker_user():
	usr = request.get_json()['user']
	lock = request.get_json()['locker']
	print("usr: {} locker: {}".format(usr, lock))
	return "locker {} has been added to user {}".format(usr, lock)
	#add locker to user here

@app.route("/remove_locker_user", methods =['DELETE'])
@requires_auth
def remove_locker_user():
	usr = request.get_json()['user']
	lock = request.get_json()['locker']
	print("usr: {} locker: {}".format(usr, lock))
	return "locker {} has been deleted from user {}".format(usr, lock)
	#remove locker from user here

if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
	app.run(host = str(ip), port=5000, debug=True) #IP is based of current pi being used, 5000 is Flask DP