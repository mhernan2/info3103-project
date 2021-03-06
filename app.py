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
from utils import use_db, get_ldap_connection, get_vals, get_user, uri, query_params, filter_user

app = Flask(__name__, static_url_path="")
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


class IndexPage(Resource):
	def get(self):
		return app.send_static_file('index.html')


class Login(Resource):

	@use_db
	def post(self, cursor):

		response = { 'status': 'fail' }
		responseCode = 403

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
			responseCode = 200
			response = { 'user': { 'user_id': session.get('username') } }
		else:
			user = get_user(cursor, req_params['username'])
			if user:
				try:
					ldapConnection = get_ldap_connection(req_params['username'], req_params['password'])
					ldapConnection.open()
					ldapConnection.start_tls()
					ldapConnection.bind()

					session['username'] = req_params['username']
					response = { 'user': user }
					responseCode = 201
				except LDAPException:
					abort(403)
				finally:
					ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	@use_db
	def get(self, cursor):
		response = {'status': 'fail'}
		responseCode = 400

		if session.get('username'):
			response = { 'user': get_user(cursor, session['username']) }
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

		user = get_user(cursor, req_params['username'])
		if not user:
			try:
				ldapConnection = get_ldap_connection(req_params['username'], req_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()

				# at this point the user is logged in
				cursor.callproc('registerUser', get_vals(req_params, 'username', 'first_name', 'last_name'))
				cursor.connection.commit()
				user = cursor.fetchone()
				user['uri'] = uri(request.url, user['user_id'])

				response = { 'user': user }
				responseCode = 200
			except LDAPException:
				abort(403)
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	@use_db
	def get(self, cursor):
		cursor.callproc('getUsers')
		users = cursor.fetchall() or []
		users = list(filter(filter_user, users))
		for user in users:
			user['uri'] = uri(request.url, user['user_id'])
		return make_response(jsonify({ 'users': users }), 200)


class User(Resource):
	@use_db
	def get(self, user_id, cursor):
		response = { 'status': 'User doesn\'t exist' }
		responseCode = 404

		user = get_user(cursor, user_id)
		if user:
			user['uri'] = request.url
			response = {'user': user}
			responseCode = 200

			return make_response(jsonify(response), responseCode)

	@use_db
	def put(self, user_id, cursor):
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
		if session.get('username') == user_id:
			cursor.callproc('updateUser', get_vals(req_params, 'username', 'first_name', 'last_name'))
			user = cursor.fetchone()
			cursor.connection.commit()
			user['uri'] = request.url
			response = { 'user': user }
			responseCode = 200

		return make_response(jsonify(response), responseCode)


class Gifts(Resource):
	@use_db
	def post(self, user_id, cursor):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('item_name', type=str, required=True)
			parser.add_argument('price', type=int, required=True)
			parser.add_argument('to', type=str, required=True)
			parser.add_argument('from', type=str, required=False, default=None)
			parser.add_argument('wishlisted', type=str, required=False, default=0)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'Access Denied' }
		responseCode = 403

		if session.get('username') == user_id:
			if session['username'] != req_params['to']:
				req_params['from'] =  user_id
			cursor.callproc('registerGift', get_vals(req_params, 'item_name', 'price', 'to', 'from', 'wishlisted'))
			cursor.connection.commit()
			gift = cursor.fetchone()
			gift['uri'] = uri(request.url, gift['gift_id'])
			response = { 'gift': gift }
			responseCode = 200

		return make_response(jsonify(response), responseCode)

	@use_db
	@query_params
	def get(self, user_id, cursor, **kwargs):
		response = { 'status': 'fail' }
		responseCode = 400

		if kwargs.get('sent'):
			cursor.callproc('getGiftsSent', (user_id,))
		else:
			cursor.callproc('getGiftsReceived', (user_id,))
		gifts = cursor.fetchall()
		for gift in gifts:
			gift['uri'] = uri(request.url, gift['gift_id'])
		response = { 'gifts': gifts }
		responseCode = 200

		return make_response(jsonify(response), responseCode)


class Gift(Resource):

	@use_db
	def get(self, user_id, gift_id, cursor):
		response = { 'status': 'Resource Not Found' }
		responseCode = 404

		cursor.callproc('getGiftById', (user_id, gift_id))
		gift = cursor.fetchone()
		if gift:
			gift['uri'] = request.url
			response = {'gift': gift }
			responseCode = 200

		return make_response(jsonify(response), responseCode)

	@use_db
	def put(self, user_id, gift_id, cursor):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('item_name', type=str, required=True)
			parser.add_argument('price', type=int, required=True)
			parser.add_argument('to', type=str, required=True)
			parser.add_argument('from', type=str, required=False, default=None)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = { 'status': 'fail' }
		responseCode = 400

		cursor.callproc('updateGift', (gift_id,)+get_vals(req_params, 'item_name', 'price', 'to', 'from'))
		gift = cursor.fetchone()
		cursor.connection.commit()
		if gift:
			gift['uri'] = request.url
			response = { 'gift': gift }
			responseCode = 200

		return make_response(jsonify(response), responseCode)

	@use_db
	def delete(self, user_id, gift_id, cursor):
		cursor.callproc('deleteGift', (user_id, gift_id))
		cursor.connection.commit()
		return make_response('', 204)


class Wishlist(Resource):

	@use_db
	@query_params
	def get(self, cursor, **kwargs):
		response = { 'status': 'Resource Not Found' }
		responseCode = 404

		if kwargs.get('user_id'):
			cursor.callproc('getUserWishlist', (kwargs['user_id'],))
		else:
			cursor.callproc('getWishlist')

		wishlist = cursor.fetchall() or []
		response = {'wishlist': wishlist}
		responseCode = 200

		return make_response(jsonify(response), responseCode)


class SendGift(Resource):

	@use_db
	def post(self, cursor):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('gift_id', type=int, required=True)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = {'status': 'Access Denied'}
		responseCode = 403

		if session.get('username'):
			cursor.callproc('sendGift', (req_params['gift_id'], session['username']))
			gift = cursor.fetchone()
			response = {'gift': gift}
			responseCode = 200
			cursor.connection.commit()

		return make_response(jsonify(response), responseCode)


class ReceiveGift(Resource):
	@use_db
	def post(self, cursor):
		if not request.json:
			abort(400)

		parser = reqparse.RequestParser()
		try:
			parser.add_argument('gift_id', type=int, required=True)
			req_params = parser.parse_args()
		except:
			abort(400)

		response = {'status': 'Access Denied'}
		responseCode = 403

		if session.get('username'):
			cursor.callproc('receiveGift', (req_params['gift_id'], session['username']))
			gift = cursor.fetchone()
			if gift:
				response = {'gift': gift}
				responseCode = 200
				cursor.connection.commit()

		return make_response(jsonify(response), responseCode)


####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(IndexPage, '/')
api.add_resource(Login, '/login')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(Gifts, '/users/<string:user_id>/gifts')
api.add_resource(Gift, '/users/<string:user_id>/gifts/<int:gift_id>')
api.add_resource(Wishlist, '/wishlist')
api.add_resource(SendGift, '/wishlist/actions/send')
api.add_resource(ReceiveGift, '/gifts/actions/receive')

#############################################################################
if __name__ == "__main__":
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		debug=settings.APP_DEBUG)
