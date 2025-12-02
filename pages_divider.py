import os
import math

prefered_lines_page = 15
max_lines_page = 20
min_lines_page = 5
symbol_per_line = 60
short_word_max_len = 2
max_number_of_pages = 10

def divide_text_into_lines(full_text, max_len=symbol_per_line):
    formatted_lines = []
    paragraphs = full_text.splitlines()

    for paragraph in paragraphs:
        if not paragraph.strip():
            formatted_lines.append("")
            continue

        words = paragraph.split()
        current_line_words = []
        
        i = 0
        while i < len(words):
            word = words[i]

            proposed_line_words = current_line_words + [word]
            proposed_line = " ".join(proposed_line_words)
            proposed_len = len(proposed_line)

            if proposed_len <= max_len:
                
                is_current_word_short = len(word) <= short_word_max_len
                next_word_index = i + 1

                line_must_break = False
                if next_word_index < len(words):
                    next_word = words[next_word_index]
                    test_len_with_next = proposed_len + 1 + len(next_word)

                    if test_len_with_next > max_len:
                        line_must_break = True

                if line_must_break and is_current_word_short:
                    
                    k = len(current_line_words) - 1
                    while k >= 0:
                        prev_word = current_line_words[k]
                        if len(prev_word) <= short_word_max_len:
                            k -= 1
                        else:
                            break
                    
                    final_line_segment = current_line_words[:k + 1]
                    formatted_lines.append(" ".join(final_line_segment))
                    
                    num_carried_from_current = len(current_line_words) - (k + 1)
                    i = i - num_carried_from_current
                    
                    current_line_words = []
                    
                else:
                    current_line_words = proposed_line_words
                    i += 1
            
            else:
                formatted_lines.append(" ".join(current_line_words))
                
                current_line_words = [word]
                i += 1


        if current_line_words:
            formatted_lines.append(" ".join(current_line_words))

    return formatted_lines

def is_sentence_end(line):
    if not line.strip():
        return True
    last_char = line.strip()[-1]
    return last_char in ['.', '!', '?', '"', "'", ')', '”']

def paginate_lines(lines):
    pages = []
    total_lines = len(lines)

    current_line_index = 0

    while current_line_index < total_lines:
        start_index = current_line_index

        search_max_hard = min(start_index + max_lines_page, total_lines)
        search_min = start_index + min_lines_page
        search_min = min(search_min, total_lines)
        
        search_start_preferred = start_index + prefered_lines_page
        search_start = max(search_min, search_start_preferred)
        search_start = min(search_start, total_lines)
        
        best_break_index = search_max_hard
        
        if total_lines - start_index < prefered_lines_page:
            best_break_index = total_lines
        else:
            
            for j in range(search_start, search_max_hard + 1):
                
                if is_sentence_end(lines[j - 1]):
                    best_break_index = j
                    break 
                
                if j == total_lines:
                    best_break_index = total_lines
                    break
        
            if not is_sentence_end(lines[best_break_index - 1]):
                
                for j in range(search_start - 1, search_min - 1, -1):
                    if is_sentence_end(lines[j - 1]):
                        best_break_index = j
                        break
        
        if not is_sentence_end(lines[best_break_index - 1]) and best_break_index != total_lines:
            best_break_index = search_max_hard


        page_content = lines[start_index:best_break_index]
        pages.append(page_content)
        current_line_index = best_break_index

    if pages and len(pages[-1]) < min_lines_page:
        short_page = pages.pop()
        if pages and len(pages[-1]) + len(short_page) <= max_lines_page:
            pages[-1].extend(short_page)
        else:
            pages.append(short_page)

    return pages


def process_chapter_file(book_path):
    
    try:
        with open(book_path, 'r', encoding='utf-8') as current_book:
            full_text = current_book.read()
    except FileNotFoundError:
        return

    formatted_lines = divide_text_into_lines(full_text)
    pages = paginate_lines(formatted_lines)
    total_pages = len(pages)

    chapter_file = os.path.basename(book_path)
    book_title = os.path.basename(os.path.dirname(book_path))
    chapter_title_base = os.path.splitext(chapter_file)[0]

    if total_pages > max_number_of_pages:
        num_parts = math.ceil(total_pages / max_number_of_pages)
        pages_per_part = math.ceil(total_pages / num_parts)
    else:
        num_parts = 1
        pages_per_part = total_pages

    output_dir = os.path.join("extracts", book_title)
    os.makedirs(output_dir, exist_ok=True)
    
    part_end_indices = []
    
    current_page = 0
    for part_index in range(num_parts):
        
        end_page_global_ideal = min((part_index + 1) * pages_per_part, total_pages)
        
        end_page_global = end_page_global_ideal
        
        if end_page_global < total_pages:
            last_page_index = end_page_global - 1
            last_line_of_page = pages[last_page_index][-1]
            
            if not is_sentence_end(last_line_of_page):
                
                new_end_index = end_page_global
                while new_end_index < total_pages:
                    next_page_index = new_end_index
                    last_line_of_next_page = pages[next_page_index][-1]
                    
                    if is_sentence_end(last_line_of_next_page):
                        end_page_global = new_end_index + 1
                        break
                    
                    new_end_index += 1
                
                if new_end_index == total_pages:
                    end_page_global = total_pages
            
        part_end_indices.append(end_page_global)

    current_start = 0
    for part_index in range(num_parts):
        start_page_global = current_start
        end_page_global = part_end_indices[part_index]

        part_pages = pages[start_page_global:end_page_global]

        if num_parts > 1:
            output_filename = f"{chapter_title_base}_part_{part_index + 1}.txt"
        else:
            output_filename = f"{chapter_title_base}.txt"

        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, page in enumerate(part_pages):

                page_in_part = start_page_global + i + 1 

                f.write(f"\n| Page {page_in_part} |\n\n")

                for line in page:
                    f.write(f"{line.strip()}\n")

            f.write("\n")
        
        current_start = end_page_global


if __name__ == "__main__":
    book_path = "books/Zwierciadlana zagadka/Zwierciadlana zagadka.txt"
    process_chapter_file(book_path)