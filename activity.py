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
from sprites import Sprites, Sprite 
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

        # Create the sprite collection
        self.sprite_list = Sprites(self.vbox)  # Pass the main vbox to Sprites

        # Create UI components
        self.create_ui()

    def create_ui(self):
        """Create the user interface for the game."""
        # Create input field for guesses
        self.entry = Gtk.Entry()
        self.entry.set_max_length(5)  # Limit input to 5 characters
        self.vbox.pack_start(self.entry, True, True, 0)

        # Create a submit button
        submit_button = Gtk.Button(label="Submit")
        submit_button.connect("clicked", self.on_submit)
        self.vbox.pack_start(submit_button, True, True, 0)

        # Initialize the graphical boxes for feedback
        self.sprites = []
        for i in range(self.max_attempts):
            for j in range(5):
                # Create a sprite for each box
                sprite = Sprite(self.sprite_list, j * 60, i * 60, None)  # Adjust position as needed
                self.sprites.append(sprite)

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
            # Update the corresponding sprite with the guessed letter
            sprite = self.sprites[len(self.guesses) - 1 * 5 + i]
            sprite.set_label(letter)  # Set the label for the sprite

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
        for sprite in self.sprites:
            sprite.set_label("")  # Clear the labels on the sprites
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