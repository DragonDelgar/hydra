extends Button


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	DataSignalManager.scan_error_string.changed.connect(_on_error_changed)

func _on_error_changed(error):
	if error != null:
		self.show()
	else:
		self.hide()
