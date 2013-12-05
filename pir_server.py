import socket
import threading
import time
import sqlite3
import struct
from sys import exit

LOCAL_ADDR6 = 'fe80::7271:bcff:fe19:13c2'
LOCAL_PORT = 40000

def db_init():
	con_db = sqlite3.connect('presence.db')
	cur = con_db.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS pir_reads(id INTEGER PRIMARY" +
		" KEY AUTOINCREMENT, id_sensor INT NOT NULL, time TEXT)")
	con_db.commit()
	con_db.close()

def db_insert(data):
	try:
		con_db = sqlite3.connect('presence.db')
		cur = con_db.cursor()
		cur.execute("INSERT INTO pir_reads(id_sensor, time) VALUES(" + 
			str(data)+ ", strftime('%d-%m-%Y %H:%M:%S', " +
				"'now','localtime'))")  
		con_db.commit()
	except sqlite3.Error, e:
		con_db.rollback()
		print "Database error: " + str(e)

	con_db.close()

def connection_handler(payload, cliaddr):
	print "Server: Connected by " + str(cliaddr)
	data = struct.unpack("!I",payload)[0]
	print "Received \"" + str(data) + "\" from " + str(cliaddr)
	db_insert(data)

def server_init(sockaddr):
	try:
		sk = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sk.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
		sk.bind(sockaddr)
	except socket.error, e:
		if sk:
			sk.close()
		print "Socket error: " + str(e)
		exit(1)
	
	print ("Server listening on addr: " + str(sockaddr[0]) + " port: " +
		str(sockaddr[1]))
	
	while True:
		try:
			payload, cliaddr = sk.recvfrom(1024)
		except socket.error, e:
			print "Recvfrom error: " + str(e)
		
		time.sleep(1)
		t = threading.Thread(target = connection_handler,
			args =(payload, cliaddr,))
		t.start()

def client_test(sockaddr, data):
	try:
		sk = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	except socket.error, e:
		print "Socket error: " + str(e)
		exit(1)

	payload = struct.pack('!I', data)
	
	try:
		sk.sendto(payload, (sockaddr[0], sockaddr[1]))
	except socket.error, e:
		print "Sendto error: " + str(e)
		sk.close()
		exit(1)

	print "Client sent " + str(data)
	sk.close()

if __name__ == '__main__':
	if not socket.has_ipv6:
		raise Exception("IPV6 Address not configured")
		exit(1)

	db_init()

	sockaddr = (LOCAL_ADDR6, LOCAL_PORT)
	t = threading.Thread(target=server_init, args=(sockaddr,))
	t.start()
	
	time.sleep(2)
	
	client_test(sockaddr, 512)
	client_test(sockaddr, 2)
	client_test(sockaddr, 3)