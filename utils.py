import settings
import pymysql
from flask import abort
from pymysql.cursors import DictCursor
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *

def use_db(func):
	def wrapper(*args, **kwargs):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass=DictCursor)
			cursor = dbConnection.cursor()
			kwargs['cursor'] = cursor
			return func(*args, **kwargs)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
	return wrapper


def get_ldap_connection(username, password):
	ldapServer = Server(host=settings.LDAP_HOST)
	ldapConnection = Connection(ldapServer,
		raise_exceptions=True,
		user='uid={username}, ou=People,ou=fcs,o=unb'.format(username=username),
		password=password)
	return ldapConnection


def get_vals(d, *args):
	return tuple(d[k] for k in args)


def check_user(cursor, user_id):
	cursor.callproc('getUserById', (user_id,))
	user = cursor.fetchone()
	return user
