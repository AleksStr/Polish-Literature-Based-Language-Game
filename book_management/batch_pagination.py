import os
import book_management.pages_divider as pages_divider

def process_all_books(base_dir="books"):
    
    if not os.path.exists(base_dir):
        return

    for root, dirs, files in os.walk(base_dir):
        
        for file_name in files:
            if file_name.endswith('.txt'):
                chapter_path = os.path.join(root, file_name)
                pages_divider.process_chapter_file(chapter_path)

if __name__ == "__main__":
    process_all_books()