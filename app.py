#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import ssl
import settings
import pymysql.cursors

app = Flask(__name__)
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)


@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

class User(Resource):
	def post(self):

		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('first_name', type=str, required=True)
			parser.add_argument('last_name', type=str, required=True)
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getSchools'
			cursor = dbConnection.cursor()
			cursor.callproc(sql)
			rows = cursor.fetchall()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'schools': rows}), 200)


class Login(Resource):

	def post(self):

		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				response = {'status': 'success' }
				responseCode = 201
			except LDAPException:
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

	def delete(self):
		if 'username' in session:
			session.clear()
		return make_response(jsonify({"status": "success"}), 200)



class User(Resource):

	def post(self):

		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('first_name', type=str, required=True)
			parser.add_argument('last_name', type=str, required=True)
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUser'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, request_params['username'])
			user = cursor.fetchone()

			# check if user is already registered
			if user:
				response = { 'message': 'user already exists' }
				responseCode = 300
			else:
				try:
					ldapServer = Server(host=settings.LDAP_HOST)
					ldapConnection = Connection(ldapServer,
						raise_exceptions=True,
						user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
						password = request_params['password'])
					ldapConnection.open()
					ldapConnection.start_tls()
					ldapConnection.bind()
					# At this point we have sucessfully authenticated.
					# register user in database
					session['username'] = request_params['username']
					response = {'status': 'success' }
					responseCode = 201
				except LDAPException:
					response = {'status': 'Access denied'}
					responseCode = 403
				finally:
					ldapConnection.unbind()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Login, '/login')
api.add_resource(User, '/users')


#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	#
	# You need to generate your own certificates. To do this:
	#	1. cd to the directory of this app
	#	2. run the makeCert.sh script and answer the questions.
	#	   It will by default generate the files with the same names specified below.
	#
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
