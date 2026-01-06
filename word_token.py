class Word_Token:
    def __init__(self, original_text, start, finish, i):
        self.original_text = original_text
        self.finish = finish
        self.start = start
        self.i = i
        self.display_word = original_text.lower()


