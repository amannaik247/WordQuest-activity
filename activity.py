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
from dictionary_manager import DictionaryManager

class WordQuestActivity(activity.Activity):
    def __init__(self, handle):
        super(WordQuestActivity, self).__init__(handle)
        
        # Initialize dictionary manager
        self.dict_manager = DictionaryManager()
        
        # Initialize dictionary file path
        self.dictionary_file = os.path.join(os.path.dirname(__file__), 'words/own_dictionary.txt')
        
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

        # Category selection screen
        self.title_label = Gtk.Label(label="Select a Category")
        self.title_label.set_name("title")
        self.title_label.set_markup("<b><big>Select a Category</big></b>")
        self.vbox.pack_start(self.title_label, False, False, 0)

        self.category_buttons = Gtk.Box(spacing=10)
        self.vbox.pack_start(self.category_buttons, False, False, 0)

        # List of categories and corresponding files
        self.categories = {
            "Animal": "words/animals.txt",
            "Country": "words/countries.txt",
            "Fruit": "words/fruits.txt",
            "AnyType": "words/allwords.txt" 
        }

        # Add category buttons
        for category, file_name in self.categories.items():
            button = Gtk.Button(label=category)
            button.connect("clicked", self.load_category, file_name)
            self.category_buttons.pack_start(button, True, True, 0)

        # Game UI (hidden initially)
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
        self.new_game_button.connect("clicked", self.show_category_screen)
        self.vbox.pack_start(self.new_game_button, False, False, 0)
        
        # Dictionary button
        self.dictionary_button = Gtk.Button(label="📖")
        self.dictionary_button.set_tooltip_text("Open Dictionary")
        self.dictionary_button.set_halign(Gtk.Align.END)
        self.dictionary_button.set_valign(Gtk.Align.END)
        self.dictionary_button.connect("clicked", self.open_dictionary)
        self.vbox.pack_end(self.dictionary_button, False, False, 0)

        self.show_category_screen()
        self.show_all()

    def show_category_screen(self, widget=None):
        """Show the category selection screen and reset game state."""
        # Reset game state
        self.guess_grid.foreach(lambda widget: self.guess_grid.remove(widget))
        self.input_entry.set_text("")
        self.status_label.set_text("")
        
        # Reset UI
        self.title_label.set_markup("<b><big>Select a Category</big></b>")
        self.category_buttons.show_all()
        self.guess_grid.hide()
        self.input_entry.hide()
        self.submit_button.hide()
        self.status_label.hide()
        self.new_game_button.hide()
        
        # Re-enable input controls
        self.input_entry.set_sensitive(True)
        self.submit_button.set_sensitive(True)

    def load_category(self, widget, file_name):
        """Load the selected category and start the game."""
        # Get the category name from the button label
        self.current_category = widget.get_label()
        
        word_list_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(word_list_path, 'r') as f:
            self.word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]

        self.start_game()

    def start_game(self):
        """Initialize the game UI."""
        self.target_word = random.choice(self.word_list)
        self.save_to_dictionary(self.target_word)
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

        self.title_label.set_text(f"Guess the {self.current_category}")
        self.category_buttons.hide()
        self.guess_grid.show()
        self.input_entry.show()
        self.submit_button.show()
        self.status_label.show()
        self.new_game_button.show()

    def on_submit_guess(self, widget):
        """Handle guess submission."""
        guess = self.input_entry.get_text().lower()

        if len(guess) != 5:
            self.status_label.set_text(f"{guess.upper()} is not a 5-letter word. Try again.")
            return

        self.input_entry.set_text("")

        # Create mutable lists to track matched positions and remaining letters
        target_word_counts = {}
        for letter in self.target_word:
            target_word_counts[letter] = target_word_counts.get(letter, 0) + 1

        # First pass: mark correct positions (green)
        feedback = [''] * 5
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
        
    def save_to_dictionary(self, word):
        """Save word to dictionary file with mastery tracking."""
        try:
            self.dict_manager.add_word(word.lower())
        except Exception as e:
            print(f"Error saving to dictionary: {e}")

    def open_dictionary(self, widget):
        """Open the dictionary window with mastery levels."""
        dictionary_window = Gtk.Window(title="My Word Dictionary")
        dictionary_window.set_default_size(300, 400)

        # Create main container
        main_box = Gtk.VBox(spacing=10)
        main_box.set_border_width(10)

        # Add header with legend
        header_box = Gtk.HBox(spacing=10)
        header_box.set_margin_bottom(10)
        
        # Add legend labels
        legend_labels = [
            ("New", "#787c7e"),
            ("Learnt", "#ff9933"),
            ("Mastered", "#0066cc")
        ]
        
        for text, color in legend_labels:
            label = Gtk.Label()
            label.set_markup(
                f'<span background="{color}" foreground="white" '
                f'weight="bold"> {text} </span>'
            )
            header_box.pack_start(label, False, False, 5)
        
        main_box.pack_start(header_box, False, False, 0)

        # Add word list
        words_box = Gtk.VBox(spacing=5)
        
        try:
            words = self.dict_manager.get_all_words()
            for word in words:
                # Create a horizontal box for each word and its tag
                hbox = Gtk.HBox(spacing=10)
                
                # Word label
                word_label = Gtk.Label(label=word.upper())
                word_label.set_halign(Gtk.Align.START)
                hbox.pack_start(word_label, True, True, 0)
                
                # Mastery level tag
                mastery_level = self.dict_manager.get_mastery_level(word)
                tag_label = Gtk.Label()
                tag_label.set_markup(
                    f'<span background="{self._get_tag_color(mastery_level)}" '
                    f'foreground="white" weight="bold"> {mastery_level} </span>'
                )
                hbox.pack_end(tag_label, False, False, 0)
                
                words_box.pack_start(hbox, False, False, 0)
        except Exception as e:
            error_label = Gtk.Label(label=f"Error loading dictionary: {e}")
            words_box.pack_start(error_label, False, False, 0)

        # Add scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.add(words_box)
        main_box.pack_start(scroll, True, True, 0)

        dictionary_window.add(main_box)
        dictionary_window.show_all()

    def _get_tag_color(self, mastery_level):
        """Get the color for mastery level tag."""
        colors = {
            "new": "#787c7e",      # Gray
            "learnt": "#ff9933",   # Orange
            "mastered": "#0066cc"  # Blue
        }
        return colors.get(mastery_level, "#787c7e")

# Styling using CSS
css = b'''
#title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}
.cell {
    font-size: 20px;
    font-weight: bold;
    border: 2px solid black;
    padding: 20px;
}
.correct {
    font-size: 18px;
    font-weight: bold;
    min-height: 34px;
    min-width: 34px;
    background-color: #0066cc;
    color: white;
    border-radius: 4px;
    border: 1px solid #0066cc;
    padding: 5px;
}

.present {
    font-size: 18px;
    font-weight: bold;
    min-height: 34px;
    min-width: 34px;
    background-color: #ff9933;
    color: white;
    border-radius: 4px;
    border: 1px solid #ff9933;
    padding: 5px;
}

.absent {
    font-size: 18px;
    font-weight: bold;
    min-height: 34px;
    min-width: 34px;
    background-color: #787c7e;
    color: white;
    border-radius: 4px;
    border: 1px solid #787c7e;
    padding: 5px;
}

GtkLabel {
    font-size: 16px;
    background-color: #d3d6da;
    color: black;
    border: 1px solid #d3d6da;
    padding: 10px;
    border-radius: 4px;
}
'''  

style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)