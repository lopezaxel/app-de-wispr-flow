from .. import dictionary, storage


class Api:
    """Puente entre el JS del panel y el backend Python (pywebview lo expone
    como window.pywebview.api.<metodo> en la pagina)."""

    def get_stats(self):
        return storage.get_stats()

    def get_history(self):
        return storage.get_history()

    def get_corrections(self):
        return storage.get_correction_summary()

    def get_dictionary(self):
        return dictionary.load_words()

    def add_dictionary_word(self, word):
        dictionary.add_word(word)
        return dictionary.load_words()

    def remove_dictionary_word(self, word):
        dictionary.remove_word(word)
        return dictionary.load_words()
