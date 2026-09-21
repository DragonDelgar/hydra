@tool
extends Control
## A horizontal line with a label inside.
## The label text is configurable in editor.

@export var labeltext = "Label":
	set(value):
		if value != labeltext:
			labeltext = value
			$HBoxContainer/Label.text = labeltext
