import gi
import random
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.alert import NotifyAlert

class WordleActivity(activity.Activity):
    def __init__(self, handle):
        super().__init__(handle)  # Call the parent constructor with the handle
        self.set_title("Wordle Clone")
        self.set_default_size(400, 500)

        self.word_list = self.load_words("words.txt")
        self.secret_word = random.choice(self.word_list).upper()
        self.attempts = 6
        self.current_attempt = 0

        # Main game layout using Gtk.Grid
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # Set up the toolbar
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

        # Entry for user input
        self.entry = Gtk.Entry()
        self.entry.set_max_length(5)  # Assuming the secret word is 5 letters
        self.grid.attach(self.entry, 0, 0, 2, 1)

        # Submit button
        self.submit_button = Gtk.Button(label="Submit")
        self.submit_button.connect("clicked", self.check_guess)
        self.grid.attach(self.submit_button, 2, 0, 1, 1)

        # Result label
        self.result_label = Gtk.Label()
        self.grid.attach(self.result_label, 0, 1, 3, 1)

        # Labels for guesses
        self.guess_labels = []
        for i in range(self.attempts):
            label = Gtk.Label()
            label.set_size_request(350, 40)  # Set size for guess labels
            label.set_justify(Gtk.Justification.CENTER)
            self.guess_labels.append(label)
            self.grid.attach(label, 0, i + 2, 3, 1)

        self.show_all()

    def load_words(self, filename):
        """Load words from a specified file."""
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Word list file '{filename}' not found.")
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]

    def check_guess(self, widget):
        """Check the user's guess against the secret word."""
        guess = self.entry.get_text().upper()
        if len(guess) != len(self.secret_word):
            self.result_label.set_text("Invalid guess length!")
            return

        self.current_attempt += 1
        self.update_guesses(guess)

        if guess == self.secret_word:
            self.result_label.set_text("Congratulations! You've guessed the word!")
            self.submit_button.set_sensitive(False)
            self.show_alert("Congratulations!", "You've guessed the word!")
        elif self.current_attempt >= self.attempts:
            self.result_label.set_text(f"Game Over! The word was: {self.secret_word}")
            self.submit_button.set_sensitive(False)
            self.show_alert("Game Over", f"The word was: {self.secret_word}")
        else:
            self.result_label.set_text("Try again!")

        self.entry.set_text("")  # Clear the entry after submission

    def update_guesses(self, guess):
        """Update the displayed guesses and color code them."""
        guess_label = self.guess_labels[self.current_attempt - 1]
        guess_label.set_text(guess)

        # Color coding logic
        for i, letter in enumerate(guess):
            if letter == self.secret_word[i]:
                guess_label.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 1, 0, 1))  # Green
            elif letter in self.secret_word:
                guess_label.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 0, 1))  # Yellow
            else:
                guess_label.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 0, 0, 1))  # Red

    def show_alert(self, title, message):
        """Show an alert dialog."""
        alert = NotifyAlert()
        alert.props.title = title
        alert.props.msg = message
        alert.connect('response', lambda x, y: self.remove_alert(x))
        self.add_alert(alert)

if __name__ == "__main__":
    activity_instance = WordleActivity()  # This line may need to be adjusted based on your Sugar Activity setup
    activity_instance.connect("destroy", Gtk.main_quit)
    activity_instance.show_all()
    Gtk.main()