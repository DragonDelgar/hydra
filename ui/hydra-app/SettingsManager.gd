extends Node

var _config = ConfigFile.new()
var CONFIG_PATH = "user://hyapp.cfg"
var DEFAULT_CONFIG_PATH = "res://default.cfg"

signal updated_song_folders()

# Called when the node enters the scene tree for the first time.
func _ready():
	_load_config()
	
func _load_config():
	# Will fill from default if this fails.
	_config.load(CONFIG_PATH)
	
	var default_config = ConfigFile.new()
	assert(default_config.load(DEFAULT_CONFIG_PATH) == OK)
	
	for section in default_config.get_sections():
		for s_key in default_config.get_section_keys(section):
			# Copy from default to current cfg if missing
			if not _config.has_section_key(section, s_key):
				_config.set_value(section, s_key, default_config.get_value(section, s_key))
	
	_config.save(CONFIG_PATH)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_song_folders():
	return _config.get_value("Scan", "song_folders")

func add_song_folder(folder):
	var fs: Array = get_song_folders()
	fs.append(folder)
	_config.set_value("Scan", "song_folders", fs)
	_config.save(CONFIG_PATH)
	updated_song_folders.emit()

func remove_song_folder(index):
	var fs: Array = get_song_folders()
	fs.remove_at(index)
	_config.save(CONFIG_PATH)
	updated_song_folders.emit()
