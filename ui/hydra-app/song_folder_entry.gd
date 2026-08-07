extends HBoxContainer

@onready var label = $Label

var folder_index: int = -1
var folder_name: String = "(Song Folder)":
	get:
		return folder_name
	set(value):
		folder_name = value
		if is_instance_valid(label):
			label.text = folder_name


# Called when the node enters the scene tree for the first time.
func _ready():
	label.text = folder_name

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _on_remove_button_pressed():
	# Remove entry from config, then ask parent to refresh.
	assert(folder_index != -1)
	SettingsManager.remove_song_folder(folder_index)
