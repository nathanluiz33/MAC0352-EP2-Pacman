run_server:
	cd server && python3 main.py 1234

run_client_udp:
	cd client && python3 client.py 127.0.0.1 1234 UDP

run_client_tcp:
	cd client && python3 client.py 127.0.0.1 1234 TCP