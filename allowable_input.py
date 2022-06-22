def allowable_list() -> list:
    latin_letters_capital = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                             'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    latin_letters_lower = [letter.lower() for letter in latin_letters_capital]

    punctuation = [",", ".", ":", "?", "!", '"', "'", "-", "(", ")", " "]
    numbers = [str(x) for x in range(0, 10)]
    allowable = []
    allowable.extend(latin_letters_capital)
    allowable.extend(latin_letters_lower)
    allowable.extend(punctuation)
    allowable.extend(numbers)
    return allowable
