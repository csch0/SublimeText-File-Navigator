import sublime, sublime_plugin

import datetime, os.path, shutil

try:
	from Default.send2trash import send2trash
	from .Tools import FileNavigator, history_items, list_items, show_input_panel, show_quick_panel
except:
	from Tools import FileNavigator, history_items, list_items, show_input_panel, show_quick_panel

	import sys
	package_dir = sublime.packages_path() + os.sep + "Default"
	if package_dir not in sys.path:
		sys.path += [package_dir]
	from send2trash import send2trash

class FileNavigatorListener(sublime_plugin.EventListener):

	def on_activated(self, view):
		file_navigator = FileNavigator()

		if file_navigator.get("active") and view.window() and view.window().id() != file_navigator.get("window_id"):
			file_navigator.reset()

		if file_navigator.get("active") and file_navigator.get("view_id") != view.id():
			file_navigator.set("view_id", view.id())

	def on_query_context(self, view, key, operator, operand, match_all):
		file_navigator = FileNavigator()

		# Check if file navigator is active
		if file_navigator.get("active") and file_navigator.get("view_id") == view.id():
			if key == "file_navigator_do_directory" and not file_navigator.get("block_do_directory"):
				return True
			elif key in ["file_navigator_toggel_hidden_files"]:
				return True

class FileNavigatorCommand(sublime_plugin.WindowCommand):

	def run(self, path = None, do_dir = None):

		self.file_navigator = FileNavigator();
		self.file_navigator.set("active", True)
		self.file_navigator.set("window_id", self.window.id())

		self.item_buffer = []

		if not path:
			self.choose_root()
		elif do_dir:
			self.do_dictionary(path)
		else:
			self.navigator(path)

	def choose_root(self, roots = None):

		# Block file_navigator_do_directory
		self.file_navigator.set("block_do_directory", True)

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
				self.file_navigator.reset()
			else:
				self.file_navigator.set("block_do_directory", False)
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
			items += [{"name": "Paste here"}]
		items += list_items(path, len(self.item_buffer) > 0)

		# Set current working directory
		self.file_navigator.set("cwd", path)

		def on_done(i):
			if i < 0:
				self.file_navigator.reset()
			# Enclosing Directory
			elif i == 0:
				self.navigator(os.path.dirname(path))
			# Paste item if item buffer
			elif i == 1 and self.item_buffer:
				self.do_paste(path);
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

		# Block file_navigator_do_directory
		self.file_navigator.set("block_do_directory", True)

		def on_done(i):
			if i < 0:
				self.file_navigator.reset()
			# Go back to directory
			elif i == 0:
				self.file_navigator.set("block_do_directory", False)
				self.navigator(path)
			elif i == 1:
				self.file_navigator.set("block_do_directory", False)
				self.do_new_directory(path)
			elif i == 2:
				self.file_navigator.set("block_do_directory", False)
				self.do_new_file(path)
			elif i == 3:
				self.file_navigator.set("block_do_directory", False)
				self.do_rename(path)
			elif i == 4:
				self.do_copy(path)
			elif i == 5:
				self.do_move(path)
			elif i == 6:
				self.file_navigator.set("block_do_directory", False)
				self.do_delete(path)

		# Save dir_name
		dir_name = os.path.basename(path)

		items = [["Back", "Go back to Directory content"]]
		items += [["New Directory", "Create a new Directory in \"%s\"" % dir_name]]

		items += [["New File", "Create a new File in \"%s\"" % dir_name]]
		items += [["Rename", "Rename \"%s\"" % dir_name]]
		items += [["Copy To ...", "Copy \"%s\" to a different location" % dir_name]]
		items += [["Move To ...", "Move \"%s\" to a different location" % dir_name]]
		items += [["Delete", "Delete \"%s\"" % dir_name]]
		show_quick_panel(self.window, items, on_done)

	def do_new_file(self, path):

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

		def on_done(dir_name):
			# Reset file_navigator
			self.file_navigator.reset()
			dir_path = os.path.join(path, dir_name)
			if os.path.exists(dir_path):
					sublime.error_message('Directory already exists:\n%s' % dir_path)
			else:
				os.mkdir(dir_path)

		show_input_panel(self.window, "New directory name:", '', on_done)

	def do_file(self, path):

		def on_done(i):
			if i < 0:
				self.file_navigator.reset()
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
		# Reset file_navigator
		self.file_navigator.reset()

		self.window.open_file(path)

	def do_rename(self, path):

		# Save source name
		source_name = os.path.basename(path)

		def on_done(target_name):
			target_path = path[:-len(source_name)] + target_name
			shutil.move(path, target_path)
			sublime.status_message("%s renamed to %s" % (source_name, target_name))

		show_input_panel(self.window, "Rename:", source_name, on_done)

	def do_delete(self, path):

		# Reset file_navigator
		self.file_navigator.reset()

		# Save source name
		source_name = os.path.basename(path)

		if sublime.ok_cancel_dialog("Delete %s?" % source_name, "Delete"):
			send2trash(path)
			sublime.status_message("%s deleted" % source_name)


	def do_move(self, path):
		roots = self.find_root()

		# add history_items
		roots += [item["path"] for item in history_items()]

		self.item_buffer = [{"path": path, "type": "move"}]
		self.choose_root(list(set(roots)))

	def do_copy(self, path):
		roots = self.find_root()

		# add history_items
		roots += [item["path"] for item in history_items()]

		self.item_buffer = [{"path": path, "type": "copy"}]
		self.choose_root(list(set(roots)))

	def do_paste(self, path):

		# Reset file_navigator
		self.file_navigator.reset()

		# Load settings
		s = sublime.load_settings("File Navigator.sublime-settings")
		cache_timeout = s.get("cache_timeout", 24)

		# add history_items
		items = history_items()
		items += [{"path": path, "rtime": datetime.datetime.today().strftime("%d.%m.%YT%H:%M:%S")}]

		# Add history items
		dir_path = os.path.join(sublime.cache_path(), "File Navigator")
		if not os.path.isdir(dir_path):
			os.makedirs(dir_path)


		with open(os.path.join(dir_path, "History.json"), "w", encoding = "utf-8") as f:
			f.write(sublime.encode_value(items))

		for item in self.item_buffer:
			try:
				if item["type"] == "move":
					shutil.move(item["path"], path)
				elif item["type"] == "copy":
					if os.path.isdir(item["path"]):
						shutil.copytree(item["path"], os.path.join(path, os.path.basename(item["path"])))
					else:
						shutil.copy(item["path"], path)
			except Exception as e:
				print(e)

		sublime.status_message("%d paste in %s" % (len(self.item_buffer), path))


class FileNavigatorToggelHiddenFilesCommand(sublime_plugin.WindowCommand):

	def run(self):
		# Save show_hidden_files and current working dir for later usage
		show_hidden_files = FileNavigator().get("show_hidden_files", sublime.load_settings("File Navigator.sublime-settings").get("show_hidden_files", True))
		cwd = FileNavigator().get("cwd")

		# Hide overlay, this will reset FileNavigator()
		self.window.run_command("hide_overlay")

		# Set show_hidden_files for the next run
		FileNavigator().set("show_hidden_files", not show_hidden_files )
		sublime.status_message("Hide system/hidden files" if show_hidden_files else "Show all available files")
		self.window.run_command("file_navigator", {"path": cwd})


class FileNavigatorDoDirectory(sublime_plugin.WindowCommand):

	def run(self):
		# Save current working dir for later usage
		cwd = FileNavigator().get("cwd")

		# Hide overlay, this will reset FileNavigator()
		self.window.run_command("hide_overlay")
		self.window.run_command("file_navigator", {"do_dir": True, "path": cwd})


class FileNavigatorResetHistory(sublime_plugin.WindowCommand):

	def is_enabled(self):
		try:
			return os.path.isfile(os.path.join(os.path.join(sublime.cache_path(), "FileNavigator", "History.json")))
		except Exception as e:
			return False

	def run(self):
		try:
			if sublime.ok_cancel_dialog("Delete File Navigator History?", "Delete"):
				os.remove(os.path.join(sublime.cache_path(), "FileNavigator", "History.json"))
		except Exception as e:
			pass
