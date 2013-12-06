from sys import argv, exit
import socket

def client_test(sockaddr, payload):
	try:
		sk = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	except socket.error, e:
		print "Socket error: " + str(e)
		exit(1)
	
	try:
		sk.sendto(payload, (sockaddr[0], sockaddr[1]))
	except socket.error, e:
		print "Sendto error: " + str(e)
		sk.close()
		exit(1)

	print "Client sent " + str(payload)
	sk.close()

if __name__ == '__main__':
	if not socket.has_ipv6:
		raise Exception("Socket error: IPV6 Address not configured")
		exit(1)
	
	remote_ipaddr6 = argv[1]
	remote_port = int(argv[2])
	local_mac = argv[3]
	sockaddr = (remote_ipaddr6, remote_port)
	client_test(sockaddr, local_mac)
