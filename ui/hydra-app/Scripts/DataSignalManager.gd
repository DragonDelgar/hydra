extends Node
## Global data, each with a unique changed signal.

const DataSignal = preload("uid://cxrv6kji5tpuc")

var scan_step1_progress = DataSignal.new()
var scan_step2_progress = DataSignal.new()

var scan_failed = DataSignal.new()
var scan_success_count = DataSignal.new()
var scan_error_string = DataSignal.new()
