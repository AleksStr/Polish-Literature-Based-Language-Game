from book import Book
import os
import shutil

book_path = "pan-tadeusz.txt"

def read_generic_info(current_book):
    author = current_book.readline().strip()
    title_lines = [current_book.readline().strip()]
    translator = None
        
    next_line = current_book.readline().strip()
    lines_count = 0
    while "ISBN" not in next_line:
        if "tłum." in next_line:
            translator = next_line.strip()
            translator = translator[6:].strip()
        elif next_line:  
            title_lines.append(next_line)
        next_line = current_book.readline().strip()
        lines_count += 1
        if lines_count > 5:
            raise ValueError(f"Other formatting")
    if "ISBN" in next_line:
        isbn = next_line.strip() 
    else:
        raise ValueError(f"Other formatting")
    full_title = " ".join(title_lines).strip()
    
    new_book = Book(title=full_title, author=author, isbn=isbn, translator=translator)
    return new_book


def read_info(current_book):
    try:
        new_book = read_generic_info(current_book)
    except ValueError: 
        print("Formatting is other than expected, input manuall (press Enter to set to None)")
        new_book = custom_info(current_book)
    return new_book

def custom_info(current_book):
    while True:
        title = input("Title: ").strip()
        if not title:
            print("Title is required!")
            continue
        author = input("Author: ")
        break
        
    return Book(title, author)  
    

def make_directory(name):
    try:
        os.mkdir("books/"+name)
        print(f"Directory '{name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def divide_chapters(current_book, new_book, chapter_number = 1):
    line = current_book.readline()
    while line and line.strip() == "":
        line = current_book.readline()

    
    if not line: 
        return
    
    chapter_title = line.strip()
    try:
        chapter = open("books/" + new_book.title + "/" + chapter_title + ".txt", 'w', encoding='utf-8')

    except: 
        print("Formatting is other than expected, please solve the error manually")
    line = current_book.readline()
    new_book.chapters.update({chapter_number: chapter_title})

    empty_counter = 0
    while line:
        temp = line
        if temp.strip() == "":  
            empty_counter += 1
            if empty_counter == 3:
                break
        else:  
            empty_counter = 0
            chapter.write(line)
        if temp.strip() == "*":
            empty_counter = -1
        line = current_book.readline()

    chapter.close()
    if line:
        divide_chapters(current_book, new_book, chapter_number+1)

def remove_editor_note(new_book):
    if os.path.exists(f"books/{new_book.title}/-----.txt"):
        os.remove(f"books/{new_book.title}/-----.txt")
        new_book.chapters.popitem()
    else:
        print("The file does not exist")

def get_number_of_chapters(book):
    for path in os.listdir("books/"+book.title):
        if os.path.isfile(os.path.join("books/"+book.title, path)):
            book.chapter_count += 1
    return book.chapter_count

def handle_one_chapter_book(current_book, new_book): 
    current_book.seek(0)
    new_book.chapters.popitem()
    new_book.chapters.update({1:new_book.title})
    line = current_book.readline()
    empty_counter = 0
    while line:
        temp = line
        if temp.strip() == "":  
            empty_counter += 1
            if empty_counter == 3:
                break
        else:  
            empty_counter = 0
        line = current_book.readline()
    
    chapter_filename = os.path.join("books", new_book.title, new_book.title + ".txt")
    with open(chapter_filename, 'w', encoding='utf-8') as chapter:
        empty_counter = 0
        line = current_book.readline()
        while line:
            temp = line
            if temp.strip() == "":  
                empty_counter += 1
                if empty_counter == 3:
                    break
            else:  
                empty_counter = 0              
                chapter.write(line)
            
            line = current_book.readline()

def delete_folder(book):
    try:
        if hasattr(book, 'title'):
            folder_path = os.path.join("books", book.title)
        else:
            folder_path = os.path.join("books", book)
        
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' does not exist")
            return False
        
        if not os.path.isdir(folder_path):
            print(f"'{folder_path}' is not a directory")
            return False
        
        shutil.rmtree(folder_path)
        print(f"Successfully deleted folder: {folder_path}")
        return True
        
    except Exception as e:
        print(f"Error deleting folder: {e}")
        return False

if __name__ == "__main__":
    new_book=""
    try:
        with open(book_path, 'r', encoding='utf-8') as current_book:
            new_book = read_info(current_book)
            
            make_directory(new_book.title)
            divide_chapters(current_book, new_book)
            remove_editor_note(new_book)
            chapter_count = get_number_of_chapters(new_book)
            print(f"Found {chapter_count} chapter(s).")
            
            if chapter_count == 1:
                print("One-chapter book detected.")
                book_dir = f"books/{new_book.title}"
                for item in os.listdir(book_dir):
                    item_path = os.path.join(book_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)               
                current_book.seek(0) 
                handle_one_chapter_book(current_book, new_book)
            new_book.display()
            correct = input("Is that correct (y/n): ")
            if correct == "n":
                print("Correct the file manually by removing/adding empty lines and try again")
                delete_folder(new_book)
                

    except FileNotFoundError:
        print(f"File {book_path} not found!")        
        exit(1)  
