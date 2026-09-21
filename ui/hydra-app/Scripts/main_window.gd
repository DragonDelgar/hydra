extends CanvasLayer
## The first window in Hydra (the Library view).

func _on_button_song_folders_pressed():
	StateManager.input(&"SongFoldersButton")

func _on_button_scan_issues_pressed():
	StateManager.input(&"ScanIssuesButton")

func _on_button_scan_songs_pressed():
	StateManager.input(&"ScanButton")
