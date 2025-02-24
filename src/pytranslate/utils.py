def add_carriage_return(original_text: str, max_line_length: int = 37) -> str:
    cleaned_text = " ".join(original_text.split())  # Remove extra spaces
    should_insert_break = False
    current_index = 0
    last_hyphen_break_index = 0
    punctuation_separators = [" ", ",", ";", ".", "!", "?"]

    for character in cleaned_text:
        # Check if a soft hyphenation point should be inserted
        if (
            character == "-"
            and current_index > 0
            and current_index + 1 < len(cleaned_text)
            and cleaned_text[current_index + 1] != "-"
            and cleaned_text[current_index - 1] in punctuation_separators
        ):
            cleaned_text = (
                cleaned_text[:current_index] + "\\N" + cleaned_text[current_index:]
            )
            current_index += 2
            last_hyphen_break_index = current_index

        # Determine if the text has exceeded the line limit
        if current_index - last_hyphen_break_index > max_line_length:
            should_insert_break = True

        # Insert a break if conditions are met
        if (
            should_insert_break
            and current_index + 1 < len(cleaned_text)
            and len(cleaned_text[current_index + 1 :]) > 0
            and cleaned_text[current_index + 1] not in punctuation_separators
            and character in punctuation_separators
        ):
            cleaned_text = (
                cleaned_text[: current_index + 1]
                + "\\N"
                + cleaned_text[current_index + 1 :]
            )
            current_index += 2
            last_hyphen_break_index = current_index
            should_insert_break = False

        current_index += 1

    return cleaned_text
