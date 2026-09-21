extends Control

@onready var label: Label = $PanelContainer/MarginContainer/VBoxContainer/Label
@onready var discovered_label: Label = $PanelContainer/MarginContainer/VBoxContainer/DiscoveredLabel
@onready var dismiss_button: Button = $PanelContainer/MarginContainer/VBoxContainer/DismissButton
@onready var adding_songs_label: Label = $PanelContainer/MarginContainer/VBoxContainer/AddingSongsLabel
@onready var progress_bar: ProgressBar = $PanelContainer/MarginContainer/VBoxContainer/ProgressBar
@onready var progress_bar_label: Label = $PanelContainer/MarginContainer/VBoxContainer/ProgressBar/ProgressBarLabel

var discovery_count: int

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	StateManager.on_state.connect(_on_state)
	DataSignalManager.scan_step1_progress.changed.connect(_on_step1_progress)
	DataSignalManager.scan_step2_progress.changed.connect(_on_step2_progress)

func _on_state(prev_state: StringName, state: StringName):
	match state:
		&"ScanStep1":
			self.show()
			discovered_label.show()
			dismiss_button.hide()
			adding_songs_label.hide()
			progress_bar.hide()
			_on_step1_progress(0)
		&"ScanStep2":
			discovered_label.text = "Discovered %d songs." % discovery_count
			adding_songs_label.show()
			progress_bar.max_value = discovery_count
			progress_bar.show()
			_on_step2_progress(0)
		_:
			self.hide()

func _on_step1_progress(value):
	if value == 0:
			discovered_label.text = "Starting song scan..."
	else:
		var trail = '.'.repeat(1 + value/200 % 6)
		discovered_label.text = "Discovered %d songs%s" % [value, trail]
	discovery_count = value

func _on_step2_progress(value):
	progress_bar.value = value
	progress_bar_label.text = "%d/%d" % [value, discovery_count]
