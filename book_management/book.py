class Book:
    def __init__(self, title = "", author = "", isbn = "", translator = None):
            self.title = title
            self.author = author
            self.isbn = isbn
            self.translator = translator
            self.chapters = {}
            self.chapter_count = 0
    def __str__(self):
        if self.translator:
            return f'"{self.title}" trans. {self.translator}  by {self.author} {self.isbn}'
        return f'"{self.title}" {self.author} {self.isbn}'

    def display(self):
        print(self)
        for key, value in self.chapters.items():
            print(key, value)
