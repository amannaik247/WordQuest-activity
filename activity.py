import gi
import random

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WordleGame(Gtk.Window):
    def __init__(self):
        super().__init__(title="Wordle Clone")
        self.set_default_size(300, 400)
        
        self.word_list = self.load_words("constants.txt")
        self.secret_word = random.choice(self.word_list).upper()
        self.attempts = 6
        self.current_attempt = 0
        
        self.grid = Gtk.Grid()
        self.add(self.grid)
        
        self.entry = Gtk.Entry()
        self.grid.attach(self.entry, 0, 0, 1, 1)
        
        self.submit_button = Gtk.Button(label="Submit")
        self.submit_button.connect("clicked", self.check_guess)
        self.grid.attach(self.submit_button, 1, 0, 1, 1)
        
        self.result_label = Gtk.Label()
        self.grid.attach(self.result_label, 0, 1, 2, 1)
        
        self.guess_labels = []
        for i in range(self.attempts):
            label = Gtk.Label()
            self.guess_labels.append(label)
            self.grid.attach(label, 0, i + 2, 2, 1)

        self.show_all()

    def load_words(self, filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]

    def check_guess(self, widget):
        guess = self.entry.get_text().upper()
        if len(guess) != len(self.secret_word):
            self.result_label.set_text("Invalid guess length!")
            return
        
        self.current_attempt += 1
        self.update_guesses(guess)
        
        if guess == self.secret_word:
            self.result_label.set_text("Congratulations! You've guessed the word!")
            self.submit_button.set_sensitive(False)
        elif self.current_attempt >= self.attempts:
            self.result_label.set_text(f"Game Over! The word was: {self.secret_word}")
            self.submit_button.set_sensitive(False)
        else:
            self.result_label.set_text("Try again!")

    def update_guesses(self, guess):
        self.guess_labels[self.current_attempt - 1].set_text(guess)

if __name__ == "__main__":
    win = WordleGame()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

