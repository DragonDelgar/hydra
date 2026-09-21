extends Control


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	StateManager.on_state.connect(_on_state)

func _on_state(state: StringName):
	match state:
		&"ScanIssues":
			self.show()
		&"Main":
			self.hide()
