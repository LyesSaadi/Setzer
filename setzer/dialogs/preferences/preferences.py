#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


from setzer.dialogs.dialog import Dialog
import setzer.dialogs.preferences.preferences_viewgtk as view
from setzer.app.service_locator import ServiceLocator

import subprocess


class PreferencesDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = ServiceLocator.get_settings()

        self.latex_interpreters = list()
        self.latexmk_available = False

    def run(self):
        self.setup()
        self.view.run()
        del(self.view)

    def setup(self):
        self.view = view.Preferences(self.main_window)

        self.view.option_cleanup_build_files.set_active(self.settings.get_value('preferences', 'cleanup_build_files'))
        self.view.option_cleanup_build_files.connect('toggled', self.on_check_button_toggle, 'cleanup_build_files')

        self.view.option_autoshow_build_log_errors.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors')
        self.view.option_autoshow_build_log_errors_warnings.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors_warnings')
        self.view.option_autoshow_build_log_all.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'all')

        self.view.option_autoshow_build_log_errors.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'errors')
        self.view.option_autoshow_build_log_errors_warnings.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'errors_warnings')
        self.view.option_autoshow_build_log_all.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'all')

        self.view.option_system_commands_disable.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'disable')
        self.view.option_system_commands_restricted.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'restricted')
        self.view.option_system_commands_full.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'enable')

        self.view.option_system_commands_disable.connect('toggled', self.on_radio_button_toggle, 'build_option_system_commands', 'disable')
        self.view.option_system_commands_restricted.connect('toggled', self.on_radio_button_toggle, 'build_option_system_commands', 'restricted')
        self.view.option_system_commands_full.connect('toggled', self.on_radio_button_toggle, 'build_option_system_commands', 'enable')

        self.view.option_spaces_instead_of_tabs.set_active(self.settings.get_value('preferences', 'spaces_instead_of_tabs'))
        self.view.option_spaces_instead_of_tabs.connect('toggled', self.on_check_button_toggle, 'spaces_instead_of_tabs')

        self.view.tab_width_spinbutton.set_value(self.settings.get_value('preferences', 'tab_width'))
        self.view.tab_width_spinbutton.connect('value-changed', self.spin_button_changed, 'tab_width')

        self.view.option_show_line_numbers.set_active(self.settings.get_value('preferences', 'show_line_numbers'))
        self.view.option_show_line_numbers.connect('toggled', self.on_check_button_toggle, 'show_line_numbers')

        self.view.option_line_wrapping.set_active(self.settings.get_value('preferences', 'enable_line_wrapping'))
        self.view.option_line_wrapping.connect('toggled', self.on_check_button_toggle, 'enable_line_wrapping')

        self.view.option_code_folding.set_active(self.settings.get_value('preferences', 'enable_code_folding'))
        self.view.option_code_folding.connect('toggled', self.on_check_button_toggle, 'enable_code_folding')

        self.view.option_highlight_current_line.set_active(self.settings.get_value('preferences', 'highlight_current_line'))
        self.view.option_highlight_current_line.connect('toggled', self.on_check_button_toggle, 'highlight_current_line')

        self.view.option_highlight_matching_brackets.set_active(self.settings.get_value('preferences', 'highlight_matching_brackets'))
        self.view.option_highlight_matching_brackets.connect('toggled', self.on_check_button_toggle, 'highlight_matching_brackets')

        self.setup_latex_interpreters()

    def setup_latex_interpreters(self):
        self.latex_interpreters = list()
        for interpreter in ['xelatex', 'pdflatex', 'lualatex']:
            self.view.option_latex_interpreter[interpreter].hide()
            arguments = [interpreter, '--version']
            try:
                process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                pass
            else:
                process.wait()
                if process.returncode == 0:
                    self.latex_interpreters.append(interpreter)

        self.latexmk_available = False
        arguments = ['latexmk', '--version']
        try:
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            pass
        else:
            process.wait()
            if process.returncode == 0:
                self.latexmk_available = True

        if len(self.latex_interpreters) == 0:
            self.view.no_interpreter_label.show_all()
        else:
            self.view.no_interpreter_label.hide()
            if self.settings.get_value('preferences', 'latex_interpreter') not in self.latex_interpreters:
                self.settings.set_value('preferences', 'latex_interpreter', self.latex_interpreters[0])

            if self.latexmk_available:
                self.view.option_use_latexmk.show_all()
            else:
                self.view.option_use_latexmk.hide()
                self.settings.set_value('preferences', 'use_latexmk', False)
            self.view.option_use_latexmk.set_active(self.settings.get_value('preferences', 'use_latexmk'))
            self.view.option_use_latexmk.connect('toggled', self.on_check_button_toggle, 'use_latexmk')

            for interpreter in self.latex_interpreters:
                self.view.option_latex_interpreter[interpreter].show_all()
                self.view.option_latex_interpreter[interpreter].set_active(interpreter == self.settings.get_value('preferences', 'latex_interpreter'))
            for interpreter in self.latex_interpreters:
                self.view.option_latex_interpreter[interpreter].connect('toggled', self.on_interpreter_changed, 'latex_interpreter', interpreter)

    def on_check_button_toggle(self, button, preference_name):
        self.settings.set_value('preferences', preference_name, button.get_active())
        
    def on_radio_button_toggle(self, button, preference_name, value):
        self.settings.set_value('preferences', preference_name, value)

    def spin_button_changed(self, button, preference_name):
        self.settings.set_value('preferences', preference_name, button.get_value_as_int())

    def text_deleted(self, buffer, position, n_chars, preference_name):
        self.settings.set_value('preferences', preference_name, buffer.get_text())

    def text_inserted(self, buffer, position, chars, n_chars, preference_name):
        self.settings.set_value('preferences', preference_name, buffer.get_text())

    def on_interpreter_changed(self, button, preference_name, value):
        self.settings.set_value('preferences', preference_name, value)


