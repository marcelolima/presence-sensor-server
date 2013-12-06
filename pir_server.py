import socket
from threading import Thread
from sqlite3 import connect, Error
from sys import exit
from re import match

LOCAL_ADDR6	= 'fe80::7271:bcff:fe19:13c2'
LOCAL_PORT	= 40000
PAYLOAD_LEN	= 17

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

def connection_handler(payload, cliaddr):
	print "Server: Connected by " + str(cliaddr[:2])
	
	# Check if the payload content matches a valid MAC address #
	if not match("^([0-9A-F]{2}[-:]){5}[0-9A-F]{2}$", 
		payload.upper()):
		print ("Received invalid mac-address: \""+ str(payload) + 
			"\" , from sensor " + str(cliaddr[:2]))
		return None

	print "Received \"" + str(payload) + "\" from " + str(cliaddr)
	db_insert(payload)

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
		
		t = Thread(target = connection_handler,
			args =(payload, cliaddr,))
		t.start()

if __name__ == '__main__':
	if not socket.has_ipv6:
		raise Exception("Socket error: IPV6 Address not configured")
		exit(1)

	sockaddr = (LOCAL_ADDR6, LOCAL_PORT, 0, 2)
	t = Thread(target=server_init, args=(sockaddr,))
	t.start()