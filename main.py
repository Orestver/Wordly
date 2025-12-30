import random, os
import json
# from google import genai
# import google.generativeai as genaii
# from google.genai import types
# from dotenv import load_dotenv

# load_dotenv()

# standart words
words_list = {
    'apple':    'яблуко', 
    'bread':    'хліб',
    'car':      'автомобіль',
    'dog':      'собака',
    'bed':      'ліжко',
    'sun':      'сонце',
    'computer': 'комп\'ютер',
    'ship':     'корабель',
    'tree':     'дерево',
    'cup':      'чашка',
    'house':    'будинок',
    'cat':      'кіт',
    'water':    'вода',
    'milk':     'молоко',
    'book':     'книга',
    'table':    'стіл',
    'chair':    'крісло',
    'window':   'вікно',
    'door':     'двері',
    'phone':    'телефон',
    'pen':      'ручка',
    'paper':    'папір',
    'bag':      'сумка',
    'shoe':     'взуття',
    'shirt':    'сорочка',
    'food':     'їжа',
    'city':     'місто',
    'road':     'дорога',
    'river':    'річка',
    'mountain': 'гора',
    'bird':     'птах',
    'fish':     'риба',
    'child':    'дитина',
    'friend':   'друг',
    'family':   'родина',
    'school':   'школа',
    'teacher':  'вчитель',
    'student':  'студент',
    'time':     'час',
    'money':    'гроші'
}

with open('words.json', 'r',encoding='utf-8') as f:
    words_list = json.load(f)

def check_translation_english(english_word: str, user_translation: str) -> bool:
    correct_translation = words_list.get(english_word, "")
    # Розділяємо на варіанти та очищаємо пробіли
    cor_translations = [t.strip().lower() for t in correct_translation.split(',')]
    return user_translation.strip().lower() in cor_translations



def check_translation_english_reverse(ukrainian_word: str, user_translation: str) -> bool:
    correct_translation = None
    for eng_word, ukr_word in words_list.items():
        if ukr_word == ukrainian_word:
            correct_translation = eng_word
            break
    return user_translation.strip().lower() == correct_translation.lower()


def give_hint(word: str) -> str:
    return word[0]



def run_test(number_of_words: int):
    keys = list(words_list.keys())
    values = list(words_list.values())
    number_of_asked = 0
    correct_answers = 0
    streak = 0
    while number_of_words == -1 or number_of_asked < number_of_words:
        print(f'({number_of_asked}/{number_of_words})')
        option = random.choice([1, 2]) # 1 - english to ukrainian 2 - ukrainian to english
        if option == 1:
            word = random.choice(keys)
            user_translation = str(input(f'What is the Ukrainian translation of "{word}"? (or enter "q" to quit or "h" to get a hint):')).strip().lower()
            if user_translation == 'q':
                break
            if user_translation == 'h':
                first_letter = give_hint(words_list[word])
                print(f'First letter is: "{first_letter}"')
                user_translation = str(input(f'What is the Ukrainian translation of "{word}"?')).strip().lower()
                if user_translation == 'q':
                    return
            if check_translation_english(word, user_translation):
                correct_answers += 1
                streak += 1
                print('Correct!')
                if streak == 20:
                    print('Unbeateble!!')
                elif streak == 10:
                    print('briliant!!')
                elif streak == 5:
                    print('excellent!!')
                elif streak == 3:
                    print('Well Done!!')
            else:
                streak = 0
                print(f'Incorrect. The correct translation is "{words_list[word]}"')
        else:
            word = random.choice(values)
            user_translation = str(input(f'What is "{word}" in english? (or press "q" to quit or "h" to get a hint):')).strip().lower()
            if user_translation == 'q':
                break
            if user_translation == 'h':
                index = values.index(word)
                first_letter = give_hint(keys[index])
                print(f'First letter is: "{first_letter}"')
                user_translation = str(input(f'What is "{word}" in english?')).strip().lower()
                if user_translation == 'q':
                    return
            if check_translation_english_reverse(word, user_translation):
                correct_answers += 1
                streak += 1
                print('Correct!')
                if streak == 20:
                    print('Unbeateble!!')
                elif streak == 10:
                    print('briliant!!')
                elif streak == 5:
                    print('excellent!!')
                elif streak == 3:
                    print('Well Done!!')
            else:
                streak = 0
                print(f'Incorrect. The english word is "{keys[values.index(word)]}"')
        number_of_asked += 1
    print("===========================")
    print(f"Your score is {correct_answers}/{number_of_asked}")
    ratio = correct_answers / number_of_asked
    if ratio > 0.9:
        print("excellent!")
    elif ratio > 0.7:
        print("good!")
    elif ratio > 0.5:
        print('nice try')
    else:
        print("you need to practice more!")





if __name__ == "__main__":
    while True:
        print('===========================')
        print('Choose the mode:')
        print('1 - 20 words test')
        print('2 - Infinite words test')
        print('3 - all words form the list test')
        print('q - quit\n')
        choice = input(str('Your choice: ')).strip().lower()
        if choice == 'q':
            print('Exiting...')
            break
        elif choice == '1':
            print('You have chosen the 20 words test mode.\n')
            number_of_words = 20
            run_test(number_of_words)
        elif choice == '2':
            print('You have chosen the infinite words test mode.\n')
            number_of_words = -1
            run_test(number_of_words)
        elif choice == '3':
            print('You have chosen the all words from the list test mode.\n')
            number_of_words = len(words_list)
            run_test(number_of_words)
        else:
            print('Invalid choice. Please try again.')
            continue