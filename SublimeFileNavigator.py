import os
import re
import shutil
import sublime
import sublime_plugin

import pprint
class FileNavigatorCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.doCommand()

    def doCommand(self):
        if not self.find_root():
            return

        self.construct_excluded_pattern()
        self.build_dir_paths()
        self.build_file_paths()
        self.move_current_directory_to_top()
        self.select_dir()

    def find_root(self):
        folders = self.window.folders()
        if len(folders) == 0:
            sublime.error_message('Could not find project root')
            return False

        self.root = folders[0]
        self.rel_path_start = len(self.root) + 1
        return True

    def construct_excluded_pattern(self):
        patterns = [pat.replace('|', '\\') for pat in self.get_setting('excluded_dir_patterns')]
        self.excluded = re.compile('^(?:' + '|'.join(patterns) + ')$')

    def get_setting(self, key):
        settings = None
        view = self.window.active_view()

        if view:
            settings = self.window.active_view().settings()

        if settings and settings.has('SublimeFileNavigator') and key in settings.get('SublimeFileNavigator'):
            # Get project-specific setting
            results =settings.get('SublimeFileNavigator')[key]
        else:
            # Get user-specific or default setting
            settings = sublime.load_settings('SublimeFileNavigator.sublime-settings')
            results = settings.get(key)
        return results

    def build_dir_paths(self):
        self.dir_paths = [["Project Root Folder", "go to projects root folder"]]
        self.selected_dir = ""
        for base, dirs, files in os.walk(self.root):
            dirs_copy = dirs[:]
            [dirs.remove(dir) for dir in dirs_copy if self.excluded.search(dir)]

            for dir in dirs:
                dir_path = os.path.join(base, dir)[self.rel_path_start:]
                self.dir_paths.append(dir_path)


    def build_file_paths(self):
        self.directory_files = []
        directory = self.root + "/" + self.selected_dir
        for base, dirs, files in os.walk(directory):
            files_copy = files[:]

            for file in files:
               self.directory_files.append(file)

    def move_current_directory_to_top(self):
        view = self.window.active_view()

        if view:
            cur_dir = os.path.dirname(view.file_name())[self.rel_path_start:]
            for path in self.dir_paths:
                if path == cur_dir:
                    i = self.dir_paths.index(path)
                    self.dir_paths.insert(1, self.dir_paths.pop(i))
                    break

    def select_dir(self):
        self.window.show_quick_panel(self.dir_paths, self.dir_selected, sublime.MONOSPACE_FONT)


    def dir_selected(self, selected_index):
        if selected_index != -1:
            if selected_index == 0:
                self.selected_dir = ""
            else:
                self.selected_dir = self.dir_paths[selected_index]

            self.build_file_paths()

            # Add aditional menu options
            self.directory_files.insert(0, ["Browse Directories", "go back to browsing directories"])
            self.directory_files.insert(1, ["New file", "new file in the current directory"])
            self.directory_files.insert(2, ["New directory", "new sub-directory in the current directory"])

            # Open window to choose desired action
            self.window.show_quick_panel(self.directory_files, self.file_selected, sublime.MONOSPACE_FONT)

    def file_selected(self, selected_index):
        if selected_index != -1:
            if selected_index == 0:
                self.select_dir()
            elif selected_index == 1:
                self.new_file()
            elif selected_index == 2:
                self.new_dir()
            else:
                # Add options for file manipulation
                options = []
                options.insert(0, ["Open " + self.directory_files[selected_index]])
                options.insert(1, ["Rename " + self.directory_files[selected_index]])
                options.insert(2, ["Copy " + self.directory_files[selected_index]])
                options.insert(3, ["Move " + self.directory_files[selected_index]])
                options.insert(4, ["Delete " + self.directory_files[selected_index]])
                self.selected_file_index = selected_index 

                # Open window to choose desired action
                self.window.show_quick_panel(options, self.file_selected_option, sublime.MONOSPACE_FONT)

    def file_selected_option(self, selected_index):

        file_name = self.directory_files[self.selected_file_index]
        full_path = os.path.join(self.root, self.selected_dir, file_name)

        if selected_index == 0: 
            self.open_file(full_path)
        elif selected_index == 1:
            self.rename_file(file_name)
        elif selected_index == 2:
            self.copy_file(full_path)
        elif selected_index == 3:
            self.move_file(full_path)
        elif selected_index == 4:
            self.delete_file(full_path)
        else:
            print "No action found"

    # File operations methods
    def open_file(self, full_path):
        self.window.open_file(full_path)

    def new_file(self):
        self.window.show_input_panel("New file name:", '', self.new_file_action, None, None)

    def new_file_action(self, file_name):
        full_path = os.path.join(self.root, self.selected_dir, file_name)
        if os.path.lexists(full_path):
            sublime.error_message('File already exists:\n%s' % full_path)
            return
        else:
            open(full_path, 'w')
            self.open_file(full_path)

    def delete_file(self, file_path):
        os.remove(file_path)
        sublime.status_message("File deleted")

    def copy_file(self, file_path):
        self.window.show_quick_panel(self.dir_paths, lambda directory_index: self.copy_file_dir_selected(directory_index, file_path), sublime.MONOSPACE_FONT)

    def copy_file_dir_selected(self, selected_index, file_path):
        if selected_index != -1:
            if selected_index == 0:
                self.selected_dir = ""
            else:
                self.selected_dir = self.dir_paths[selected_index]

            selected_dir = os.path.join(self.root, self.selected_dir)
            shutil.move(file_path, selected_dir)
            sublime.status_message("File copied to %s" % (selected_dir))

    def move_file(self, file_path):
        self.window.show_quick_panel(self.dir_paths, lambda directory_index: self.move_file_dir_selected(directory_index, file_path), sublime.MONOSPACE_FONT)

    def move_file_dir_selected(self, selected_index, file_path):
        if selected_index != -1:
            if selected_index == 0:
                self.selected_dir = ""
            else:
                self.selected_dir = self.dir_paths[selected_index]

            selected_dir = os.path.join(self.root, self.selected_dir)
            shutil.move(file_path, selected_dir)
            sublime.status_message("File moved to %s" % (selected_dir))

    def rename_file(self, file_name):
        self.window.show_input_panel("Rename:", file_name, lambda user_input: self.rename_file_action(file_name, user_input), None, None)

    def rename_file_action(self, old_filename, new_filename):
        sublime.status_message("File renamed to %s" % (new_filename))
        old_filename = os.path.join(self.root, self.selected_dir, old_filename)
        new_filename = os.path.join(self.root, self.selected_dir, new_filename)
        shutil.move(old_filename, new_filename)


    def new_dir(self):
        self.window.show_input_panel("New directory name:", '', self.new_dir_action, None, None)

    def new_dir_action(self, dir_name): 
        full_path = os.path.join(self.root, self.selected_dir, dir_name)
        if os.path.lexists(full_path):
            sublime.error_message('Directory already exists:\n%s' % full_path)
            return
        else:
            os.mkdir(full_path)
