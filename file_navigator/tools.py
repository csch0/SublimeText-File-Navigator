import sublime, sublime_plugin

import time, fnmatch, os

if sublime.platform() == "windows":
	import ctypes

def list_items(path, dirs_only = False, show_hidden_files = False):
	s = sublime.load_settings("File Navigator.sublime-settings")
	exclude_patterns = s.get("exclude_patterns", [])
	hidden_patterns = s.get("hidden_patterns", [])
	show_hidden_files = show_hidden_files if show_hidden_files else s.get("show_hidden_files", False)
	#
	items = []
	for item in os.listdir(path):
		# Build path of file
		item_path = os.path.join(path, item)

		# Check file_exclude_patterns and folder_exclude_patterns
		if any([fnmatch.fnmatch(item.lower(), p.lower()) for p in exclude_patterns]):
			continue

		# Check hidden files
		if not show_hidden_files:

			if any([fnmatch.fnmatch(item.lower(), p.lower()) for p in hidden_patterns]):
				continue

			# Check for hidden attribute etc
			if sublime.platform() in ["osx", "linux"] and item[0] == ".":
				continue
			elif sublime.platform() == "windows":
				attrs = ctypes.windll.kernel32.GetFileAttributesW(item_path)
				if attrs != -1 and bool(attrs & 2):
					continue

		if os.path.isdir(item_path):
			items += [{"name":item + "/", "desciption": "Open Directory", "path": item_path, "is_dir": True}]
		else:
			items += [{"name":item, "desciption": "Rename/Delete/Copy/Move File", "path": item_path, "is_dir": False}]

	# Filter dirs, if required
	if dirs_only:
		items = [item for item in items if item["is_dir"]]
	return items


def show_input_panel(window, caption, initial_text, on_done, on_change = None, on_cancel = None):
  sublime.set_timeout(lambda: window.show_input_panel(caption, initial_text, on_done, on_change, on_cancel), 0)


def show_quick_panel(window, items, on_done, selected_index = -1):
  sublime.set_timeout(lambda: window.show_quick_panel(items, on_done, sublime.MONOSPACE_FONT, selected_index), 0)


def history_items():
	# Load settings
	s = sublime.load_settings("File Navigator.sublime-settings")
	cache_timeout = s.get("cache_timeout", 24)

	s = sublime.load_settings("File Navigator.history")

	# Check for cache_timeout
	now = time.time()
	items = []
	for item in s.get("items", []):
		try:
			if now - int(item["rtime"]) < cache_timeout * 3600:
				items += [item]
		except Exception:
			pass
	return items