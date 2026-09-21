extends ColorRect


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	StateManager.on_state.connect(_handle_state)

func _handle_state(oldstate, state):
	match state:
		&"ScanStep1":
			self.show()
		&"ScanIssues":
			self.show()
		&"SongFolders":
			self.show()
		_:
			self.hide()

func _on_pressed() -> void:
	StateManager.input(&"Back")
