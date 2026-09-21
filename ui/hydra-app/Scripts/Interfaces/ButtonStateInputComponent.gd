extends Node
## Attach to a button to automatically call StateManager.input() when that button is pressed.

## Input Name
@export var input_name = &"InputName"

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# try to connect to parent.pressed
	pass

func _parent_pressed():
	StateManager.input(input_name)
