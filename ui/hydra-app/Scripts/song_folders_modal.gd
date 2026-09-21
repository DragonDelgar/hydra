extends Control

@onready var entry_container = $PanelContainer/MarginContainer/VBoxContainer/FolderListBg/ScrollContainer/MarginContainer/EntryContainer
@onready var file_dialog = $FileDialog

const SCN_ENTRY: PackedScene = preload("res://Scenes/song_folder_entry.tscn")

# Called when the node enters the scene tree for the first time.
func _ready():
	StateManager.on_state.connect(_handle_state)
	_handle_state(&"Null", StateManager._state)
	SettingsManager.updated_song_folders.connect(_on_settings_song_folders_changed)
	refresh()

func _handle_state(oldstate, state):
	match state:
		&"SongFolders":
			self.show()
		_:
			self.hide()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _on_settings_song_folders_changed():
	refresh()

func refresh():
	# Clear
	for n in entry_container.get_children():
		entry_container.remove_child(n)
		n.queue_free()
	
	# Populate
	var song_folders = SettingsManager.get_song_folders()
	for i in range(song_folders.size()):
		var new_entry = SCN_ENTRY.instantiate()
		new_entry.folder_index = i
		new_entry.folder_name = song_folders[i]
		entry_container.add_child(new_entry)

func _on_add_song_folder_button_pressed():
	file_dialog.popup_file_dialog()

func _on_file_dialog_dir_selected(dir):
	SettingsManager.add_song_folder(dir)
