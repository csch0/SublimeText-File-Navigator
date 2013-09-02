import sublime, sublime_plugin

import datetime, fnmatch, os

if sublime.platform() == "windows":
	import ctypes

class FileNavigator(object):

	__shared = {}
	__settings = {}

	def __new__(cls, *args, **kwargs):
		inst = object.__new__(cls)
		inst.__dict__ = cls.__shared
		return inst

	def get(self, key, fallback = None):
		return self.__settings[key] if key in self.__settings else fallback

	def set(self, key, value):
		self.__settings[key] = value

	def reset(self):
		self.__settings = {}


def list_items(path, dirs_only = False):
	s = sublime.load_settings("File Navigator.sublime-settings")
	file_exclude_patterns = s.get("file_exclude_patterns", [])
	folder_exclude_patterns = s.get("folder_exclude_patterns", [])
	show_hidden_files = FileNavigator().get("show_hidden_files", s.get("show_hidden_files", False))
	#
	items = []
	for item in os.listdir(path):
		# Build path of file
		item_path = os.path.join(path, item)

		# Check file_exclude_patterns and folder_exclude_patterns
		if any([fnmatch.fnmatch(item.lower(), p.lower()) for p in file_exclude_patterns]):
			continue

		# Check hidden files
		if not show_hidden_files:
			if sublime.platform() in ["osx", "linux"] and item[0] == ".":
				continue
			elif sublime.platform() == "windows":
				attrs = ctypes.windll.kernel32.GetFileAttributesW(item)
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
	try:
		# Load settings
		s = sublime.load_settings("File Navigator.sublime-settings")
		cache_timeout = s.get("cache_timeout", 24)

		# open History.join
		with open(os.path.join(sublime.cache_path(), "File Navigator", "History.json"), "r", encoding = "utf-8") as f:
			items = []

			# Check for cache_timeout
			today = datetime.datetime.today()
			items = [item for item in sublime.decode_value(f.read()) if ((today - datetime.datetime.strptime(item["rtime"], "%d.%m.%YT%H:%M:%S")).total_seconds() < cache_timeout * 3600)]
			print(items)

	except Exception as e:
		items = []

	return items