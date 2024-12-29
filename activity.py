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

        """Set up the Wordle activity."""
        activity.Activity.__init__(self, handle)
        
        # Initialize game variables
        self.word_to_guess = "APPLE"  # Example word
        self.guesses = []
        self.max_attempts = 6
        
        # Create UI components
        self.create_ui()

    def create_ui(self):
        """Create the user interface for the game."""
        # Create a grid for guesses
        self.grid = Gtk.Grid()
        self.add(self.grid)
        
        # Create input field for guesses
        self.entry = Gtk.Entry()
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
                self.grid.attach(label, j, i, 1, 1)
                label_row.append(label)
            self.feedback_labels.append(label_row)

    def on_submit(self, widget):
        """Handle the submit button click."""
        guess = self.entry.get_text().upper()
        if len(guess) == 5 and guess not in self.guesses:
            self.guesses.append(guess)
            self.check_guess(guess)
            self.entry.set_text("")

    def check_guess(self, guess):
        """Check the user's guess against the word to guess."""
        # Logic to check the guess and update feedback labels
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
        
        if guess == self.word_to_guess:
            self.show_winner_message()

    def show_winner_message(self):
        """Display a message when the user wins."""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Congratulations! You've guessed the word!")
        dialog.run()
        dialog.destroy()
