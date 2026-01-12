import os
import pages_divider as pages_divider

def get_creation_time(file_path):
    return os.path.getctime(file_path)

def process_all_books(base_dir="books"):
    if not os.path.exists(base_dir):
        return

    book_folders = [f for f in os.listdir(base_dir) 
                   if os.path.isdir(os.path.join(base_dir, f))]
    
    for book_folder in book_folders:
        book_path = os.path.join(base_dir, book_folder)
        
        chapter_files = []
        for root, dirs, files in os.walk(book_path):
            for file_name in files:
                if file_name.endswith('.txt'):
                    file_path = os.path.join(root, file_name)
                    creation_time = get_creation_time(file_path)
                    chapter_files.append((creation_time, file_path))
        
        chapter_files.sort(key=lambda x: x[0])
        
        pages_divider.current_chapter = 1
        
        for creation_time, chapter_path in chapter_files:
            pages_divider.process_chapter_file(chapter_path, book_folder)

if __name__ == "__main__":
    process_all_books()