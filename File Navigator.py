import sublime, sublime_plugin

import time, os.path, shutil, subprocess

try:
	from Default.send2trash import send2trash
	from .file_navigator.tools import history_items, list_items, show_input_panel, show_quick_panel
except (ImportError, ValueError):
	from file_navigator.tools import history_items, list_items, show_input_panel, show_quick_panel

	import sys
	package_dir = sublime.packages_path() + os.sep + "Default"
	if package_dir not in sys.path:
		sys.path += [package_dir]
	from send2trash import send2trash

CHOOSE_ROOT = 0
NAVIGATOR = 1
NAVIGATOR_PASTE = 2
DO_FILE = 3
DO_DIR = 4

class FileNavigatorListener(sublime_plugin.EventListener):

	def on_activated(self, view):

		if FileNavigatorCommand.active and view.window() and view.window().id() != FileNavigatorCommand.window_id:
			FileNavigatorCommand.reset()

		if FileNavigatorCommand.active and FileNavigatorCommand.view_id != view.id():
			FileNavigatorCommand.view_id = view.id()

	def on_query_context(self, view, key, operator, operand, match_all):
		
		# Check if file navigator is active
		if FileNavigatorCommand.active and FileNavigatorCommand.view_id == view.id():
			if key in ["file_navigator_do_directory", "file_navigator_toggel_hidden_files"]:
				return True


class FileNavigatorCommand(sublime_plugin.WindowCommand):

	active = False
	cwd = None
	view_id = None
	window_id = None

	navigator_status = None
	
	block_do_directory = False
	keep_settings = False
	show_hidden_files = False

	@classmethod
	def reset(self):
		self.active = False
		cwd = None
		view_id = None
		window_id = None

	def run(self, path = None, do_dir = None):

		# Hide overlay before the next run
		self.window.run_command("hide_overlay")

		self.cls = FileNavigatorCommand
		self.cls.active = True
		self.cls.window_id = self.window.id()

		self.item_buffer = []

		if not path:
			self.choose_root()
		elif do_dir:
			self.do_dictionary(path)
		else:
			self.navigator(path)

	def choose_root(self, roots = None):

		# Set navigator status
		self.cls.navigator_status = CHOOSE_ROOT

		# Find roots
		roots = roots if roots else self.find_root()

		# Sort roots
		roots = sorted(roots)

		# Find command prefix
		prefix = os.path.commonprefix(roots).rpartition(os.sep)[0]
		items =  [[item[len(prefix)+1:], os.path.dirname(item)] for item in roots]
		# items =  [[os.path.basename(item), os.path.dirname(item)] for item in roots]

		def on_done(i):
			if i < 0:
				self.cls.reset()
			else:
				self.navigator(roots[i])

		if not items:
			sublime.status_message("No Root Elements")
		elif len(items) == 1:
			on_done(0)
		else:
			show_quick_panel(self.window, items, on_done)

	def find_root(self):
		items = []

		# Search for root of the different views
		for view in self.window.views():
			if view.file_name():
				item = os.path.dirname(view.file_name())
				if os.path.isdir(item) and item not in items:
					items += [item]

		# Search for the root for the window
		for item in self.window.folders():
			if item and os.path.isdir(item) and item not in items:
				items += [item]

		return items

	def navigator(self, path):

		items = [{"name": ".."}]
		if self.item_buffer:
			items += [{"name": "Paste"}]
		if len(self.item_buffer) == 1:
			items += [{"name": "Paste As ..."}]

		# List items in folder
		items += list_items(path, len(self.item_buffer) > 0, self.cls.show_hidden_files)

		# block_do_directory on paste
		if self.item_buffer:
			self.cls.navigator_status = NAVIGATOR_PASTE
		else:
			self.cls.navigator_status = NAVIGATOR

		# Set current working directory
		self.cls.cwd = path

		def on_done(i):
			if i < 0:
				if not self.cls.keep_settings:
					self.cls.reset()
				self.cls.keep_settings = False
			# Enclosing Directory
			elif i == 0:
				self.navigator(os.path.dirname(path))
			# Paste item if item buffer
			elif i == 1 and self.item_buffer:
				self.do_paste(path);
			elif i == 2 and len(self.item_buffer) == 1:
				self.do_paste_as(path);
			# Restart navigator if the selected item is a dir, or file action on selecting a file
			elif items[i]["is_dir"]:
				self.navigator(items[i]["path"])
			else:
				self.do_file(items[i]["path"])

		if items:
			show_quick_panel(self.window, [item["name"] for item in items], on_done)
		else:
			sublime.status_message("No Items in %s!!!" % path)

	def do_dictionary(self, path):

		# Set navigator status
		self.cls.navigator_status = DO_DIR

		def on_done(i):
			if i < 0:
				if not self.cls.keep_settings:
					self.cls.reset()
				self.cls.keep_settings = False
			# Go back to directory
			elif i == 0:
				self.navigator(path)
			elif i == 1:
				self.do_new_directory(path)
			elif i == 2:
				self.do_new_file(path)
			elif i == 3:
				self.do_open_folder(path)
			elif i == 4:
				self.do_rename(path)
			elif i == 5:
				self.do_copy(path)
			elif i == 6:
				self.do_move(path)
			elif i == 7:
				self.do_delete(path)

		# Save dir_name
		dir_name = os.path.basename(path)

		items = [["Back", "Go back to Directory content"]]
		items += [["New Directory", "Create a new Directory in \"%s\"" % dir_name]]

		items += [["New File", "Create a new File in \"%s\"" % dir_name]]
		items += [["Open", "Open \"%s\" outside of Sublime Text" % dir_name]]
		items += [["Rename", "Rename \"%s\"" % dir_name]]
		items += [["Copy To ...", "Copy \"%s\" to a different location" % dir_name]]
		items += [["Move To ...", "Move \"%s\" to a different location" % dir_name]]
		items += [["Delete", "Delete \"%s\"" % dir_name]]
		show_quick_panel(self.window, items, on_done)

	def do_new_file(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		def on_done(file_name):
			file_path = os.path.join(path, file_name)
			if os.path.exists(file_path):
					sublime.error_message('File already exists:\n%s' % file_path)
			else:
				with open(file_path, 'w') as f:
					pass
				self.window.open_file(file_path)

		show_input_panel(self.window, "New file name:", '', on_done)

	def do_new_directory(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		def on_done(dir_name):
			# Reset FileNavigatorCommand
			FileNavigatorCommand.reset()
			
			dir_path = os.path.join(path, dir_name)
			if os.path.exists(dir_path):
					sublime.error_message('Directory already exists:\n%s' % dir_path)
			else:
				os.mkdir(dir_path)

		show_input_panel(self.window, "New directory name:", '', on_done)

	def do_file(self, path):

		# Set navigator status
		self.cls.navigator_status = DO_FILE

		def on_done(i):
			if i < 0:
				if not self.cls.keep_settings:
					self.cls.reset()
				self.cls.keep_settings = False
			# Go back to directory
			elif i == 0:
				self.navigator(os.path.dirname(path))
			elif i == 1:
				self.do_open(path)
			elif i == 2:
				self.do_rename(path)
			elif i == 3:
				self.do_copy(path)
			elif i == 4:
				self.do_move(path)
			elif i == 5:
				self.do_delete(path)

		# Save dir_name
		file_name = os.path.basename(path)

		items = [["..", "Enclosing Folder"]]

		items += [["Open", "Open \"%s\" in Sublime Text" % file_name]]
		items += [["Rename", "Rename \"%s\"" % file_name]]
		items += [["Copy To ...", "Copy \"%s\" to a different location" % file_name]]
		items += [["Move To ...", "Move \"%s\" to a different location" % file_name]]
		items += [["Delete", "Delete \"%s\"" % file_name]]

		show_quick_panel(self.window, items, on_done)

	def do_open(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		self.window.open_file(path)

	def do_open_folder(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		if sublime.platform() == "windows":
			subprocess.call(["explorer", path])
		elif sublime.platform() == "osx":
			subprocess.call(["open", path])
		elif sublime.platform() == "linux":
			subprocess.call(["xdg-open", path])

	def do_rename(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		# Save source name
		source_name = os.path.basename(path)

		def on_done(target_name):
			target_path = path[:-len(source_name)] + target_name
			shutil.move(path, target_path)
			sublime.status_message("%s renamed to %s" % (source_name, target_name))

		show_input_panel(self.window, "Rename:", source_name, on_done)

	def do_delete(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		# Save source name
		source_name = os.path.basename(path)

		if sublime.ok_cancel_dialog("Delete %s?" % source_name, "Delete"):
			send2trash(path)
			sublime.status_message("%s deleted" % source_name)


	def do_move(self, path):
		roots = self.find_root()

		# add history_items
		roots += [item["path"] for item in history_items()]

		self.item_buffer = [{"file_path": path, "file_name": os.path.basename(path), "type": "move"}]
		self.choose_root(list(set(roots)))

	def do_copy(self, path):
		roots = self.find_root()

		# add history_items
		roots += [item["path"] for item in history_items()]

		self.item_buffer = [{"file_path": path, "file_name": os.path.basename(path), "type": "copy"}]
		self.choose_root(list(set(roots)))

	def do_paste_as(self, path):

		# Save source name
		source_name = self.item_buffer[0]["file_name"]

		def on_done(target_name):
			self.item_buffer[0]["file_name"] = target_name
			self.do_paste(path)

		show_input_panel(self.window, "Paste As:", source_name, on_done)

	def do_paste(self, path):

		# Reset FileNavigatorCommand
		self.cls.reset()

		# Load settings
		s = sublime.load_settings("File Navigator.sublime-settings")
		cache_timeout = s.get("cache_timeout", 24)

		# add history_items
		items = history_items()
		items += [{"path": path, "rtime": int(time.time())}]

		# Add history items
		s = sublime.load_settings("File Navigator.history")
		s.set("items", items)
		sublime.save_settings("File Navigator.history")

		for item in self.item_buffer:
			try:
				if item["type"] == "move":
					shutil.move(item["file_path"], os.path.join(path, item["file_name"]))
				elif item["type"] == "copy":
					if os.path.isdir(item["file_path"]):
						shutil.copytree(item["file_path"], os.path.join(path, item["file_name"]))
					else:
						shutil.copy(item["file_path"], os.path.join(path, item["file_name"]))
			except Exception as e:
				pass

		sublime.status_message("%d paste in %s" % (len(self.item_buffer), path))


class FileNavigatorToggelHiddenFilesCommand(sublime_plugin.WindowCommand):

	def run(self):

		if FileNavigatorCommand.navigator_status == NAVIGATOR:
			# Set show_hidden_files for the next run
			FileNavigatorCommand.show_hidden_files = not FileNavigatorCommand.show_hidden_files
			sublime.status_message("Show all available files" if FileNavigatorCommand.show_hidden_files else "Hide system/hidden files")

			FileNavigatorCommand.keep_settings = True
			self.window.run_command("file_navigator", {"path": FileNavigatorCommand.cwd})


class FileNavigatorDoDirectory(sublime_plugin.WindowCommand):

	def run(self):
		
		if FileNavigatorCommand.navigator_status == CHOOSE_ROOT:
			pass

		elif FileNavigatorCommand.navigator_status == NAVIGATOR:
			FileNavigatorCommand.keep_settings = True
			self.window.run_command("file_navigator", {"do_dir": True, "path": FileNavigatorCommand.cwd})
		
		elif FileNavigatorCommand.navigator_status in [DO_DIR, DO_FILE]:
			FileNavigatorCommand.keep_settings = True
			self.window.run_command("file_navigator", {"path": FileNavigatorCommand.cwd})

class FileNavigatorResetHistory(sublime_plugin.WindowCommand):

	def is_enabled(self):
		try:
			return os.path.isfile(os.path.join(os.path.join(sublime.cache_path(), "File Navigator", "History.json")))
		except Exception as e:
			return False

	def run(self):
		try:
			if sublime.ok_cancel_dialog("Delete File Navigator History?", "Delete"):
				os.remove(os.path.join(sublime.cache_path(), "FileNavigator", "History.json"))
		except Exception as e:
			pass
