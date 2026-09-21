extends Resource
## Basic custom resource tying a variable to a unique changed signal.

var value = null:
	set(new_value):
		if value != new_value:
			value = new_value
			changed.emit(value)

## Just makes access look better.
func has_value() -> bool:
	return value != null
