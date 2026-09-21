extends Node

# Responsible for asking remote Hydra to do things and receiving the result.
# Note: UI elements will probably always listen to StateManager
# for updates.

var client_sock: StreamPeerTCP
var HOST = '127.0.0.1'
var PORT = 4477

var current_status = null

# Called when the node enters the scene tree for the first time.
func _ready():
	client_sock = StreamPeerTCP.new()
	#_connect()
	StateManager.on_state.connect(_on_state)
	_on_state(&"Null", StateManager._state)

func _on_state(prev_state: StringName, state: StringName):
	match state:
		&"Main":
			client_sock.disconnect_from_host()
		&"ScanStep1":
			_connect()

func _connect():
	#client_sock.disconnect_from_host()
	#if current_status != client_sock.STATUS_CONNECTED and current_status != client_sock.STATUS_CONNECTING:
		#client_sock.connect_to_host(HOST, PORT)
	client_sock.connect_to_host(HOST, PORT)

func _on_connected():
	match StateManager._state:
		&"ScanStep1":
			_send("scansongs|" + "|".join(SettingsManager.get_song_folders()))

func _on_connection_error():
	StateManager.input(&"ConnectionInterrupt")

func _on_connection_exit():
	StateManager.input(&"ConnectionInterrupt")

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	client_sock.poll()
	if current_status != client_sock.get_status():
		current_status = client_sock.get_status()
		match current_status:
			client_sock.STATUS_CONNECTED:
				print("Connection update: Connected.")
				_on_connected()
			client_sock.STATUS_CONNECTING:
				print("Connection update: Connecting.")
			client_sock.STATUS_ERROR:
				print("Connection update: Error.")
				_on_connection_error()
			client_sock.STATUS_NONE:
				print("Connection update: None.")
				_on_connection_exit()
	_receive()

func _receive():
	if current_status == client_sock.STATUS_CONNECTED and client_sock.get_available_bytes() > 0:
		var msg = client_sock.get_utf8_string()
		var tokens = msg.split('|')
		var reply = tokens[0]
		var replyargs = tokens.slice(1, tokens.size())
		match reply:
			&"scan_step1_progress":
				StateManager.input_value(&"scan_step1_progress", int(replyargs[0]))
			&"scan_step2_progress":
				StateManager.input_value(&"scan_step2_progress", int(replyargs[0]))
			&"end":
				StateManager.input(&"process_complete")
			&"kv":
				StateManager.add_data(replyargs[0], replyargs[1])
			_:
				assert(false, "Unknown reply (%s)" % reply)

func _send(message):
	if current_status == client_sock.STATUS_CONNECTED:
		client_sock.put_utf8_string(message)

func request_songscan():
	assert(false, "Obsolete function")
	_send("scansongs|" + "|".join(SettingsManager.get_song_folders()))
	
	
	
