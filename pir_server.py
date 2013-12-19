import socket
from threading import Thread
from sqlite3 import connect, Error
from sys import exit, argv
from re import match
from struct import unpack

PAYLOAD_LEN	= 17
LOCAL_PORT	= 40000

def db_init():
	try:
		con_db = connect('presence.db')
		cur = con_db.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS pir_reads(id INTEGER \
			PRIMARY" + " KEY AUTOINCREMENT, id_sensor TEXT       \
			NOT NULL, time TEXT)")
		con_db.commit()
		con_db.close()
	except Error, e:
		print "Database error: " + str(e)
		exit(1)

	finally:
		if con_db:
 			con_db.close()

def db_insert(data):
	try:
		con_db = connect('presence.db')
		cur = con_db.cursor()
		cur.execute("INSERT INTO pir_reads(id_sensor, time) VALUES(\"" +
			str(data) + "\", strftime('%d-%m-%Y %H:%M:%S', "       +
				"'now','localtime'))")
		con_db.commit()
	except Error, e:
		con_db.rollback()
		print "Database error: " + str(e)

	con_db.close()

def server_init(sockaddr):
	try:
		sk = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sk.bind(sockaddr)
	except socket.error, e:
		if sk:
			sk.close()
		print "Socket error: " + str(e)
		exit(1)

	db_init()

	print ("Server listening on addr: " + str(sockaddr[0]) + " port: " +
		str(sockaddr[1]))

	while True:
		try:
			payload, cliaddr = sk.recvfrom(PAYLOAD_LEN)
		except socket.error, e:
			print "Recvfrom error: " + str(e)
			sk.close()
			exit(1)

	        print "Received \"" + payload + "\" from " + str(cliaddr)

		t = Thread(target = db_insert,
			args =(payload,))
		t.start()

if __name__ == '__main__':
	if not socket.has_ipv6:
		raise Exception("Socket error: IPV6 Address not configured")
		exit(1)

	sockaddr = ('', LOCAL_PORT)
	t = Thread(target=server_init, args=(sockaddr,))
	t.start()