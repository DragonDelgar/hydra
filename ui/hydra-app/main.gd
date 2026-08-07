extends CanvasLayer

# Connection to Hydra (python)
@onready var hydra_client = $HydraClient
@onready var file_dialog = $FileDialog
@onready var modal_cover = $ModalCover
@onready var song_folders_modal = $SongFoldersModal

var song_paths = []

# Called when the node enters the scene tree for the first time.
func _ready():
	print("Main _ready()")

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _on_button_song_folders_pressed():
	modal_cover.show()
	song_folders_modal.show()

func _on_button_scan_songs_pressed():
	pass # Replace with function body.

func _on_sfm_back():
	modal_cover.hide()
	song_folders_modal.hide()
