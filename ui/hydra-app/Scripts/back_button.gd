extends Button
## A button that sends a "Back" input to StateManager.

func _on_pressed() -> void:
	StateManager.input(&"Back")
