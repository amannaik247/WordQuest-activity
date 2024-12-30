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
        super().__init__(handle)

        # Set up the toolbar
        self.max_participants = 1
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

        # Create the main VBox
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.vbox.set_halign(Gtk.Align.CENTER)
        self.vbox.set_valign(Gtk.Align.CENTER)
        self.set_canvas(self.vbox)

        # Create UI components
        self.create_ui()

    def create_ui(self):
        """Create the user interface for the game."""
        # Create a grid for guesses
        self.grid = Gtk.Grid()
        self.vbox.pack_start(self.grid, True, True, 0)

        # Create input field for guesses
        self.entry = Gtk.Entry()
        self.entry.set_max_length(5)  # Limit input to 5 characters
        self.grid.attach(self.entry, 0, self.max_attempts, 5, 1)

        # Create a submit button
        submit_button = Gtk.Button(label="Submit")
        submit_button.connect("clicked", self.on_submit)
        self.grid.attach(submit_button, 5, self.max_attempts, 1, 1)

        # Create labels for feedback
        self.feedback_labels = []
        for i in range(self.max_attempts):
            label_row = []
            for j in range(5):
                label = Gtk.Label("")
                label.set_size_request(60, 60)  # Set size for feedback labels
                label.set_halign(Gtk.Align.CENTER)
                label.set_valign(Gtk.Align.CENTER)
                label.set_markup("<span font='24'>{}</span>".format(""))  # Set larger font
                self.grid.attach(label, j, i, 1, 1)  # Attach label to grid
                label_row.append(label)
            self.feedback_labels.append(label_row)

        # Show all widgets
        self.vbox.show_all()  # Ensure the vbox and its contents are visible

    def on_submit(self, widget):
        """Handle the submit button click."""
        guess = self.entry.get_text().upper()
        if len(guess) == 5 and guess not in self.guesses:
            self.guesses.append(guess)
            self.check_guess(guess)
            self.entry.set_text("")
        else:
            self.show_error_message("Please enter a valid 5-letter word.")

    def check_guess(self, guess):
        """Check the user's guess against the word to guess."""
        for i, letter in enumerate(guess):
            if letter == self.word_to_guess[i]:
                self.feedback_labels[len(self.guesses) - 1][i].set_text(letter)
                self.feedback_labels[len(self.guesses) - 1][i].set_markup("<span foreground='green'>{}</span>".format(letter))
            elif letter in self.word_to_guess:
                self.feedback_labels[len(self.guesses) - 1][i].set_text(letter)
                self.feedback_labels[len(self.guesses) - 1][i].set_markup("<span foreground='yellow'>{}</span>".format(letter))
            else:
                self.feedback_labels[len(self.guesses) - 1][i].set_text(letter)
                self.feedback_labels[len(self.guesses) - 1][i].set_markup("<span foreground='red'>{}</span>".format(letter))

        # Check for win or loss
        if guess == self.word_to_guess:
            self.show_congratulations_message()  # Show congratulations message
        elif len(self.guesses) >= self.max_attempts:
            self.show_end_message()  # Show game over message

    def show_end_message(self):
        """Display a message when the game ends."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.YES_NO,
                                   "Game Over! The word was: {}\nDo you want to restart?".format(self.word_to_guess))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.restart_game()

    def restart_game(self):
        """Restart the game."""
        self.word_to_guess = random.choice(WORD_LIST)
        self.guesses = []
        for row in self.feedback_labels:
            for label in row:
                label.set_text("")
        self.entry.set_text("")

    def show_error_message(self, message):
        """Display an error message."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
        dialog.run()
        dialog.destroy()

    def show_congratulations_message(self):
        """Display a congratulations message when the user wins."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                   "Congratulations! You've guessed the word: {}".format(self.word_to_guess))
        dialog.run()
        dialog.destroy()
        self.restart_game()  # Optionally restart the game after winning