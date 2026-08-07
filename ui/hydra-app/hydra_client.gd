extends Node

var client_sock: StreamPeerTCP
var HOST = '127.0.0.1'
var PORT = 4477

var arbitrary_timer = 0
var current_status = null

# Called when the node enters the scene tree for the first time.
func _ready():
	client_sock = StreamPeerTCP.new()
	client_sock.connect_to_host(HOST, PORT)
	

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	client_sock.poll()
	
	if current_status != client_sock.get_status():
		current_status = client_sock.get_status()
		match current_status:
			client_sock.STATUS_CONNECTED:
				print("Connected.")
			client_sock.STATUS_CONNECTING:
				print("Connecting.")
			client_sock.STATUS_ERROR:
				print("Error.")
			client_sock.STATUS_NONE:
				print("None.")
		
	# Receive
	if current_status == client_sock.STATUS_CONNECTED and client_sock.get_available_bytes() > 0:
		var data = client_sock.get_utf8_string()
		print("Received message: %s" % [data])
	
	if arbitrary_timer % 100 == 0:
		if current_status == client_sock.STATUS_CONNECTED:
			print("Sending message: %s" % ["Reh!"])
			client_sock.put_utf8_string("Reh!")
	
	arbitrary_timer += 1
