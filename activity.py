# Copyright 2009 Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Wordle Activity: A case study for developing an activity."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
import random
from constants import WORD_LIST


class WordleActivity(activity.Activity):
    """WordleActivity class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the Wordle activity."""
        activity.Activity.__init__(self, handle)

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

        # toolbar with the new toolbar redesign
        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        
        
        self.set_title("Wordle Game")
        self.set_default_size(600, 400)  # Set default window size

        # Initialize game variables
        self.word_to_guess = random.choice(WORD_LIST)  # Randomly select a word
        self.guesses = []
        self.max_attempts = 6
        self.current_guess = ""

        # Create the main VBox
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.vbox.set_halign(Gtk.Align.CENTER)
        self.vbox.set_valign(Gtk.Align.CENTER)
        self.set_canvas(self.vbox)

        # Create UI components
        self.create_ui()

        # Connect key press event
        self.connect("key-press-event", self.on_key_press)

    def create_ui(self):
        """Create the user interface for the game."""
        # Create a grid for guesses
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)
        self.vbox.pack_start(self.grid, True, True, 0)

        # Create labels for feedback (5 columns, 6 rows)
        self.feedback_labels = []
        for i in range(self.max_attempts):
            label_row = []
            for j in range(5):
                label = Gtk.Label("")
                label.set_size_request(50, 50)  # Set size for feedback labels
                label.set_halign(Gtk.Align.CENTER)
                label.set_valign(Gtk.Align.CENTER)
                label.set_markup("<span font='20'>{}</span>".format(""))  # Set larger font
                self.grid.attach(label, j, i, 1, 1)
                label_row.append(label)
            self.feedback_labels.append(label_row)

        # Show all widgets in the grid first
        self.grid.show_all()

        # Create a submit button
        submit_button = Gtk.Button(label="Submit")
        submit_button.connect("clicked", self.on_submit)
        self.vbox.pack_start(submit_button, False, False, 0)

        # Show all widgets in the vbox
        self.vbox.show_all()

    def on_key_press(self, widget, event):
        """Handle key press events."""
        keyval = Gdk.keysyms
        if event.keyval in [keyval.A, keyval.B, keyval.C, keyval.D, keyval.E,
                            keyval.F, keyval.G, keyval.H, keyval.I, keyval.J,
                            keyval.K, keyval.L, keyval.M, keyval.N, keyval.O,
                            keyval.P, keyval.Q, keyval.R, keyval.S, keyval.T,
                            keyval.U, keyval.V, keyval.W, keyval.X, keyval.Y,
                            keyval.Z]:
            if len(self.current_guess) < 5:
                self.current_guess += chr(event.keyval)
                self.update_grid()

        elif event.keyval == keyval.BackSpace:
            self.current_guess = self.current_guess[:-1]
            self.update_grid()

        elif event.keyval == keyval.Return:
            if len(self.current_guess) == 5:
                self.check_guess(self.current_guess)
                self.current_guess = ""

    def update_grid(self):
        """Update the grid with the current guess."""
        row_index = len(self.guesses)
        if row_index < self.max_attempts:
            for i in range(5):
                if i < len(self.current_guess):
                    self.feedback_labels[row_index][i].set_text(self.current_guess[i])
                else:
                    self.feedback_labels[row_index][i].set_text("")

    def on_submit(self, widget):
        """Handle the submit button click."""
        if len(self.current_guess) == 5:
            self.check_guess(self.current_guess)
            self.current_guess = ""

    def check_guess(self, guess):
        """Check the user's guess against the word to guess."""
        row_index = len(self.guesses)
        self.guesses.append(guess)
        for i, letter in enumerate(guess):
            self.feedback_labels[row_index][i].set_text(letter)
            if letter == self.word_to_guess[i]:
                self.feedback_labels[row_index][i].set_markup("<span foreground='green' font='20'>{}</span>".format(letter))
            elif letter in self.word_to_guess:
                self.feedback_labels[row_index][i].set_markup("<span foreground='yellow' font='20'>{}</span>".format(letter))
            else:
                self.feedback_labels[row_index][i].set_markup("<span foreground='red' font='20'>{}</span>".format(letter))

        if guess == self.word_to_guess:
            self.show_end_message("Congratulations! You've guessed the word!", True)
        elif len(self.guesses) >= self.max_attempts:
            self.show_end_message("Nice try! The word was: {}\n".format(self.word_to_guess), False)

    def show_end_message(self, message, won):
        """Display a message when the game ends."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.YES_NO,
                                   "{}\nDo you want to restart?".format(message))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.restart_game()

    def restart_game(self):
        """Restart the game."""
        self.word_to_guess = random.choice(WORD_LIST)
        self.guesses = []
        self.current_guess = ""
        for row in self.feedback_labels:
            for label in row:
                label.set_text("")

    def show_error_message(self, message):
        """Display an error message."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
        dialog.run()
        dialog.destroy()