extends Node

# Responsible for reacting to state changes mostly of the
# following two flavors:
# - UX inputs caused by the user
# - Updates from RemoteManager
#
# Any instance of the app changing windows, layout, etc. should be an
# input going through StateManager.
# Some inputs are specific, like a particular connection type
#	failing, while others are generic, like "Back".

signal on_state(prev_state: StringName, state: StringName)

# Value changes that don't change screen layout
#signal on_state_progress(value)

# Change this state by calling input
var _state: StringName

# key-value data that is state but optional / doesn't drive the main state
# TO DO: Possibly can live on RemoteManager
#var data = {}

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	_set_state(&"Main")

func _set_state(newstate: StringName):
	var old: StringName = _state
	_state = newstate
	on_state.emit(old, _state)

func is_state(in_state: StringName):
	return in_state == _state

func input(input_name: StringName):
	match _state:
		&"Main":
			match input_name:
				&"ScanButton":
					_set_state(&"ScanStep1")
					data.erase('success_count')
					data.erase('errorstr')
					data.erase('scanfailed')
				&"ScanIssuesButton":
					_set_state(&"ScanIssues")
				&"SongFoldersButton":
					_set_state(&"SongFolders")
		&"ScanStep1":
			match input_name:
				&"ConnectionInterrupt":
					DataSignalManager.scan_success.value = false
					add_data('scanfailed', true)
					add_data('errorstr', "Local connection error.")
					_set_state(&"Main")
		&"ScanStep2":
			match input_name:
				&"process_complete":
					_set_state(&"Main")
				&"ConnectionInterrupt":
					add_data('scanfailed', true)
					add_data('errorstr', "Local connection error.")
					_set_state(&"Main")
		&"ScanIssues":
			match input_name:
				&"Back":
					_set_state(&"Main")
		&"SongFolders":
			match input_name:
				&"Back":
					_set_state(&"Main")
		_:
			assert(false, "Unknown state (%s)" % _state)

#func input_value(input_name: StringName, value):
	#match _state:
		#&"ScanStep1":
			#match input_name:
				#&"scan_step1_progress":
					#on_state_progress.emit(value)
				#&"scan_step2_progress":
					#_set_state(&"ScanStep2")
					#input_value(input_name, value)
		#&"ScanStep2":
			#match input_name:
				#&"scan_step2_progress":
					#on_state_progress.emit(value)
		#_:
			#assert(false, "Unknown state (%s)" % _state)

#func add_data(key, value):
	#if key not in data:
		#data[key] = value
	#else:
		#if data[key] is Array:
			#data[key].append(value)
		#else:
			#data[key] = [data[key], value]
