@tool

extends Control

@export var label = "Label":
	get:
		return label
	set(value):
		if value != label:
			label = value
			$HBoxContainer/Label.text = label

# Called when the node enters the scene tree for the first time.
func _ready():
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
