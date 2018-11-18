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
from utils import use_db, get_ldap_connection, get_vals, check_user

app = Flask(__name__)
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)


@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)


@app.errorhandler(403)
def not_found(error):
	return make_response(jsonify( { 'status': 'Access Denied' } ), 403)


class Login(Resource):

	@use_db
	def post(self, cursor):

		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			req_params = parser.parse_args()
		except:
			abort(400)

		if session.get('username') == req_params['username']:
			response = {'status': 'success'}
			responseCode = 200
		else:
			if check_user(cursor, req_params['username']):
				try:
					ldapConnection = get_ldap_connection(req_params['username'], req_params['password'])
					ldapConnection.open()
					ldapConnection.start_tls()
					ldapConnection.bind()

					session['username'] = req_params['username']
					response = {'status': 'success' }
					responseCode = 201
				except LDAPException:
					abort(403)
				finally:
					ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	def get(self):
		response = {'status': 'fail'}
		responseCode = 400

		if session.get('username'):
			response = { 'status': 'success' }
			responseCode = 200

		return make_response(jsonify(response), responseCode)

	def delete(self):
		if 'username' in session:
			session.clear()
		return make_response(jsonify({"status": "success"}), 200)


class Users(Resource):

	@use_db
	def post(self, cursor):

		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('first_name', type=str, required=True)
			parser.add_argument('last_name', type=str, required=True)
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'User already registered' }
		responseCode = 400

		user = check_user(cursor, req_params['username'])
		if not user:
			try:
				ldapConnection = get_ldap_connection(req_params['username'], req_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()

				# at this point the user is logged in
				cursor.callproc('registerUser', get_vals(req_params, 'username', 'first_name', 'last_name'))
				cursor.connection.commit()

				response = { 'status': 'success' }
				responseCode = 200
			except LDAPException:
				abort(403)
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	@use_db
	def get(self, cursor):
		cursor.callproc('getUsers')
		users = cursor.fetchall()
		return make_response(jsonify({ 'users': users }), 200)


class User(Resource):
	@use_db
	def get(self, user_id, cursor):
		response = { 'status': 'User doesn\'t exist' }
		responseCode = 404

		user = check_user(cursor, user_id)
		if user:
			response = {'user': user}
			responseCode = 200

			return make_response(jsonify(response), responseCode)

	def put(self, user_id):
		print(session.get('username'))
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('first_name', type=str, required=True)
			parser.add_argument('last_name', type=str, required=True)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'Access Denied' }
		responseCode = 403

		# authorize user
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			cursor = dbConnection.cursor()
			cursor.callproc('updateUser', get_vals(req_params, 'username', 'first_name', 'last_name'))
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
			req_params = parser.parse_args()
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
			cursor.callproc(sql, (req_params['item_name'], req_params['price'], req_params['to'], user_id))
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
		response = { 'status': 'fail' }
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
			req_params = parser.parse_args()
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
			cursor.callproc(sql, (gift_id, req_params['item_name'], req_params['price'], req_params['to'], user_id))
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


class Test(Resource):
	@use_db
	def get(self, test_id, cursor):
		for i in session:
			print(i)
		return make_response(jsonify({'hello': 'world'}), 200)

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
api.add_resource(Test, '/test/<string:test_id>')


#############################################################################
if __name__ == "__main__":
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		debug=settings.APP_DEBUG)
