import os
import math

prefered_lines_page = 4
max_lines_page = 4
min_lines_page = 4
symbol_per_line = 60
short_word_max_len = 2
max_number_of_pages = 10

current_chapter = 1

def divide_text_into_lines(full_text, max_len=symbol_per_line):
    formatted_lines = []
    paragraphs = full_text.splitlines()

    for paragraph in paragraphs:
        if not paragraph.strip():
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
    if not line or not line.strip():
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
        search_min = min(start_index + min_lines_page, total_lines)
        search_start = min(start_index + prefered_lines_page, total_lines)
        
        best_break_index = search_max_hard
        

        if total_lines - start_index > prefered_lines_page:
            found = False
            for j in range(search_start, search_max_hard + 1):
                if is_sentence_end(lines[j - 1]):
                    best_break_index = j
                    found = True
                    break
            
            if not found:
                for j in range(search_start - 1, search_min - 1, -1):
                    if is_sentence_end(lines[j - 1]):
                        best_break_index = j
                        break
        else:
            best_break_index = total_lines

        pages.append(lines[start_index:best_break_index])
        current_line_index = best_break_index

    return pages

def process_chapter_file(chapter_path, book_title=None):
    global current_chapter
    
    try:
        with open(chapter_path, 'r', encoding='utf-8') as f:
            full_text = f.read().strip()
        if not full_text:
            return
    except:
        return

    if book_title is None:
        book_title = os.path.basename(os.path.dirname(chapter_path))
    
    formatted_lines = divide_text_into_lines(full_text)
    pages = paginate_lines(formatted_lines)
    total_pages = len(pages)
    
    output_dir = os.path.join("extracts", book_title)
    os.makedirs(output_dir, exist_ok=True)


    num_parts = math.ceil(total_pages / max_number_of_pages)
    pages_per_part = math.ceil(total_pages / num_parts)
    
    part_end_indices = []
    for part_index in range(num_parts):
        end_page_ideal = min((part_index + 1) * pages_per_part, total_pages)
        end_page = end_page_ideal

        if end_page < total_pages:
            while end_page < total_pages:
                if is_sentence_end(pages[end_page - 1][-1]):
                    break
                end_page += 1
        

        if part_end_indices and end_page <= part_end_indices[-1]:
            continue
            
        part_end_indices.append(end_page)
        if end_page == total_pages:
            break

    current_start = 0
    for end_page in part_end_indices:
        chunk_pages = pages[current_start:end_page]
        if not chunk_pages:
            continue
            
        output_path = os.path.join(output_dir, f"chapter_{current_chapter}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, page in enumerate(chunk_pages):
                f.write(f"\n| Page {i + 1} |\n\n")
                for line in page:
                    f.write(f"{line.strip()}\n")
            f.write("\n")
        
        current_chapter += 1
        current_start = end_page