from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from gi.repository import Gtk, Gdk

import gi
gi.require_version('Gtk', '3.0')
from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
import random
import os

class WordleActivity(activity.Activity):
    def __init__(self, handle):
        super(WordleActivity, self).__init__(handle)

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

        # Initialize UI components
        self.vbox = Gtk.VBox(spacing=10)
        self.vbox.set_border_width(20)
        self.set_canvas(self.vbox)

        self.title_label = Gtk.Label(label="Wordle Game")
        self.title_label.set_name("title")
        self.title_label.set_markup("<b><big>Wordle Game</big></b>")
        self.title_label.set_justify(Gtk.Justification.CENTER)
        self.vbox.pack_start(self.title_label, False, False, 0)

        self.guess_grid = Gtk.Grid()
        self.guess_grid.set_row_spacing(5)
        self.guess_grid.set_column_spacing(5)
        self.guess_grid.set_halign(Gtk.Align.CENTER)
        self.guess_grid.set_valign(Gtk.Align.CENTER)
        self.vbox.pack_start(self.guess_grid, True, True, 0)

        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Enter a 5-letter word")
        self.input_entry.set_max_length(5)
        self.input_entry.set_halign(Gtk.Align.CENTER)
        self.input_entry.connect("activate", self.on_submit_guess)
        self.vbox.pack_start(self.input_entry, False, False, 0)

        self.submit_button = Gtk.Button(label="Submit")
        self.submit_button.set_halign(Gtk.Align.CENTER)
        self.submit_button.connect("clicked", self.on_submit_guess)
        self.vbox.pack_start(self.submit_button, False, False, 0)

        self.status_label = Gtk.Label(label="")
        self.status_label.set_justify(Gtk.Justification.CENTER)
        self.vbox.pack_start(self.status_label, False, False, 0)

        self.new_game_button = Gtk.Button(label="New Game")
        self.new_game_button.set_halign(Gtk.Align.CENTER)
        self.new_game_button.connect("clicked", self.new_game)
        self.vbox.pack_start(self.new_game_button, False, False, 0)

        # Load the word list
        word_list_path = os.path.join(os.path.dirname(__file__), 'wordlist.txt')
        with open(word_list_path, 'r') as f:
            self.word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]

        self.new_game()
        self.show_all()

    def build_toolbar(self):
        """Set up the activity toolbar."""
        toolbox = ToolbarBox()

        # Stop button
        stop_button = ToolButton('activity-stop')
        stop_button.set_tooltip('Stop')
        stop_button.connect('clicked', self._on_stop_clicked)
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbox)
        toolbox.show()

    def _on_stop_clicked(self, widget):
        """Handle the Stop button event."""
        self.close()

    def new_game(self, widget=None):
        """Start a new game."""
        self.target_word = random.choice(self.word_list)
        self.current_row = 0
        self.max_guesses = 6
        self.guess_grid.foreach(lambda widget: self.guess_grid.remove(widget))
        self.status_label.set_text("")
        self.input_entry.set_text("")
        self.input_entry.set_sensitive(True)
        self.submit_button.set_sensitive(True)

        for row in range(self.max_guesses):
            for col in range(5):
                label = Gtk.Label(label="")
                label.set_name("cell")
                label.get_style_context().add_class("default")
                self.guess_grid.attach(label, col, row, 1, 1)
        self.guess_grid.show_all()



    def on_submit_guess(self, widget):
        """Handle guess submission."""
        guess = self.input_entry.get_text().lower()
        
        """ Add all 5 letter word dictionary in this section of the code to check if guess valid word"""
        # if len(guess) != 5 or guess not in self.word_list:
        #     self.status_label.set_text("Invalid word. Try again.")
        #     return

        self.input_entry.set_text("")

        # Create mutable lists to track matched positions and remaining letters
        target_word_counts = {}
        for letter in self.target_word:
            target_word_counts[letter] = target_word_counts.get(letter, 0) + 1

        # First pass: mark correct positions (green)
        feedback = [''] * 5  # Initialize feedback for each letter
        for col, letter in enumerate(guess):
            label = self.guess_grid.get_child_at(col, self.current_row)
            label.set_text(letter.upper())

            if letter == self.target_word[col]:
                feedback[col] = 'correct'
                target_word_counts[letter] -= 1

        # Second pass: mark present (yellow) and absent (gray)
        for col, letter in enumerate(guess):
            if feedback[col] == '':
                label = self.guess_grid.get_child_at(col, self.current_row)
                if letter in target_word_counts and target_word_counts[letter] > 0:
                    feedback[col] = 'present'
                    target_word_counts[letter] -= 1
                else:
                    feedback[col] = 'absent'

        # Apply feedback styles
        for col, status in enumerate(feedback):
            label = self.guess_grid.get_child_at(col, self.current_row)
            label.get_style_context().add_class(status)

        self.current_row += 1

        if guess == self.target_word:
            self.status_label.set_text("Congratulations! You guessed the word.")
            self.end_game()
        elif self.current_row == self.max_guesses:
            self.status_label.set_text(f"Game over! The word was: {self.target_word.upper()}")
            self.end_game()

    def end_game(self):
        """End the current game."""
        self.input_entry.set_sensitive(False)
        self.submit_button.set_sensitive(False)

# Styling using CSS
css = b'''
#title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
}
.cell {
    border: 2px solid black;
    padding: 20px;
    min-width: 50px;
    min-height: 50px;
    font-size: 18px;
    font-weight: bold;
    -gtk-icon-transform: center;
}
.correct {
    background-color: #6aaa64; /* Green for correct letters */
    color: white;
    border-radius: 4px;
    border: 1px solid #6aaa64;
    padding: 5px;
}

.present {
    background-color: #c9b458; /* Yellow for present letters */
    color: white;
    border-radius: 4px;
    border: 1px solid #c9b458;
    padding: 5px;
}

.absent {
    background-color: #787c7e; /* Gray for absent letters */
    color: white;
    border-radius: 4px;
    border: 1px solid #787c7e;
    padding: 5px;
}

GtkGrid {
    grid-row-spacing: 10px;
    grid-column-spacing: 10px;
    margin: 20px;
}

GtkLabel {
    font-size: 16px;
    background-color: #d3d6da; /* Default background color for boxes */
    color: black;
    border: 1px solid #d3d6da;
    padding: 10px;
    border-radius: 4px;
}
'''  

style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)