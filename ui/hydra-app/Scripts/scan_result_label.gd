extends Label
## A label that displays a scan result summary.

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	DataSignalManager.scan_failed.changed.connect(_data_changed)
	DataSignalManager.scan_success_count.changed.connect(_data_changed)

func _data_changed(_value):
	refresh()

func refresh():
	if DataSignalManager.scan_failed.has_value():
		self.text = "Scan failed."
		self.show()
	elif DataSignalManager.scan_success_count.has_value():
		self.text = "Scan complete: %d songs." % DataSignalManager.scan_success_count.value
		self.show()
	else:
		self.hide()
