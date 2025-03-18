import os
import json
from enum import Enum

class WordMasteryLevel(Enum):
    NEW = "new"
    LEARNT = "learnt"
    MASTERED = "mastered"

class DictionaryManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dictionary_file = os.path.join(self.base_dir, 'words', 'own_dictionary.txt')
        # Store word usage counts in the same directory
        self.usage_file = os.path.join(self.base_dir, 'words', 'word_usage.txt')
        self.word_usage = self._load_usage_data()

    def _load_usage_data(self):
        """Load the word usage data from file."""
        usage_data = {}
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    for line in f:
                        word, count = line.strip().split(':')
                        usage_data[word.lower()] = int(count)
            except Exception:
                pass
        return usage_data

    def _save_usage_data(self):
        """Save the word usage data to file."""
        os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
        with open(self.usage_file, 'w') as f:
            for word, count in self.word_usage.items():
                f.write(f"{word}:{count}\n")

    def add_word(self, word):
        """Add a new word or update existing word's usage count."""
        word = word.lower()
        
        # Add word to dictionary file if not already present
        self._add_to_dictionary_file(word)
        
        # Update usage count
        if word not in self.word_usage:
            self.word_usage[word] = 1
        else:
            self.word_usage[word] += 1
        
        # Save updated usage data
        self._save_usage_data()

    def _add_to_dictionary_file(self, word):
        """Add word to the dictionary file if not already present."""
        os.makedirs(os.path.dirname(self.dictionary_file), exist_ok=True)
        
        existing_words = set()
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r') as f:
                existing_words = set(line.strip().lower() for line in f)
        
        if word not in existing_words:
            with open(self.dictionary_file, 'a') as f:
                f.write(word + '\n')

    def get_mastery_level(self, word):
        """Get the mastery level of a word based on its usage count."""
        usage_count = self.word_usage.get(word.lower(), 0)
        
        if usage_count >= 4:
            return WordMasteryLevel.MASTERED.value
        elif usage_count >= 2:
            return WordMasteryLevel.LEARNT.value
        else:
            return WordMasteryLevel.NEW.value

    def get_all_words(self):
        """Get all words from the dictionary file."""
        words = []
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r') as f:
                words = [line.strip().lower() for line in f if line.strip()]
        return sorted(words) 