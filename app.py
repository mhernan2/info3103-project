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
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserById'
				cursor = dbConnection.cursor()
				cursor.callproc(sql, (request_params['username'], ))
				user = cursor.fetchone()

				# check if user is already registered
				if user:
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
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()

			return make_response(jsonify(response), responseCode)


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



class Users(Resource):

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
			sql = 'getUserById'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (request_params['username'], ))
			user = cursor.fetchone()

			# check if user is already registered
			if user:
				response = { 'message': 'user already exists' }
				responseCode = 400
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
					sql = 'registerUser'
					cursor.callproc(sql, (request_params['username'], request_params['first_name'], request_params['last_name']))
					dbConnection.commit()
					response = {'status': 'success' }
					responseCode = 200
				except LDAPException:
					response = {'status': 'Access denied'}
					responseCode = 403
				finally:
					ldapConnection.unbind()
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

	def get(self):
		response = {
			'status': 'fail'
		}
		responseCode = 404
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUsers'
			cursor = dbConnection.cursor()
			cursor.callproc(sql)
			users = cursor.fetchall()
			response = {'users': users}
			responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)


class User(Resource):
	def get(self, user_id):
		response = {
			'status': 'fail'
		}
		responseCode = 404
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserById'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (user_id,))
			user = cursor.fetchone()
			response = {'user': user}
			responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

	def put(self, user_id):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('first_name', type=str, required=True)
			parser.add_argument('last_name', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		# authorize user
		if request_params['username'] in session:
			abort(403, 'You can\'t modify this user')

		response = { 'status': 'fail' }
		responseCode = 400

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'updateUser'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (user_id, request_params['first_name'], request_params['last_name']))
			user = cursor.fetchone()
			dbConnection.commit()
			response = { 'user': user }
			responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

class Gifts(Resource):
	def post(self, user_id):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('item_name', type=str, required=True)
			parser.add_argument('price', type=int, required=True)
			parser.add_argument('to', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'fail' }
		responseCode = 400

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'registerGift'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (request_params['item_name'], request_params['price'], request_params['to'], user_id))
			gift = cursor.fetchone()
			dbConnection.commit()
			response = { 'gift': gift }
			responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

	def get(self, user_id):
		response = {
			'status': 'fail'
		}
		responseCode = 404
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getGiftsSent'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (user_id,))
			gifts = cursor.fetchall()
			response = {'gifts': gifts}
			responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)


class Gift(Resource):

	def get(self, user_id, gift_id):
		response = {
			'status': 'fail'
		}
		responseCode = 404

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getGiftById'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (user_id, gift_id))
			gift = cursor.fetchone()
			if gift:
				response = {'gift': gift }
				responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

	def put(self, user_id, gift_id):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('item_name', type=str, required=True)
			parser.add_argument('price', type=int, required=True)
			parser.add_argument('to', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'fail' }
		responseCode = 400

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'updateGift'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (gift_id, request_params['item_name'], request_params['price'], request_params['to'], user_id))
			gift = cursor.fetchone()
			dbConnection.commit()
			if gift:
				response = { 'gift': gift }
				responseCode = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)

	def delete(self, user_id, gift_id):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'deleteGift'
			cursor = dbConnection.cursor()
			cursor.callproc(sql, (user_id, gift_id))
			dbConnection.commit()
			gift = cursor.fetchone()
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response('', 204)

####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Login, '/login')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(Gifts, '/users/<string:user_id>/gifts')
api.add_resource(Gift, '/users/<string:user_id>/gifts/<int:gift_id>')


#############################################################################
if __name__ == "__main__":
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		debug=settings.APP_DEBUG)
