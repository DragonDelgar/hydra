extends Control
## Label that displays the current StateManager state.

func _ready() -> void:
	StateManager.on_state.connect(_on_state)
	_on_state(StateManager._state)

func _on_state(state: StringName):
	$DebugLabel.text = state
