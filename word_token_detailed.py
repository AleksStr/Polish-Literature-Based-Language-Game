from word_token import Word_Token
class Word_Token_Detailed(Word_Token):
    def __init__(self, original_text, start, finish, i, morph, pos):
        super().__init__(original_text, start, finish, i)
        self.morph = morph
        self.pos = pos