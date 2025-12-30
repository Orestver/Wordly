import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import json, os
import random
from test import build_words_list, save_words_to_file
import sys, pygame
from statistics_handler import load_stats, add_answer, add_session, save_stats

# Шлях до папки словників
if getattr(sys, 'frozen', False):  # Якщо запущено як .exe
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

wordlists_dir = os.path.join(base_path, "wordlists")
os.makedirs(wordlists_dir, exist_ok=True)

try:
    pygame.mixer.init()
except pygame.error:
    print("Sound disabled")



if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
words_list = {}
pack_text_widgets = {}

# ---------------- ФУНКЦІЇ ----------------
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("PDF files", "*.pdf"),
            ("DOCX files", "*.docx"),
            ("JSON files", "*.json"),
            ("Text files", "*.txt")
        ]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def load_file():
    global words_list
    file_path = entry_file.get()
    if not file_path:
        messagebox.showwarning("Увага", "Оберіть файл!")
        return

    if file_path.lower().endswith(".pdf"):
        words_list = build_words_list(pdf_path=file_path)
    elif file_path.lower().endswith(".docx"):
        words_list = build_words_list(docx_path=file_path)
    elif file_path.lower().endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            words_list = json.load(f)
    elif file_path.lower().endswith(".txt"):
        words_list = {}
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if " - " in line:
                    eng, ukr = line.strip().split(" - ", 1)
                    words_list[eng] = ukr
    else:
        messagebox.showwarning("Увага", "Непідтримуваний формат файлу!")
        return

    text_box.delete("1.0", tk.END)
    for eng, ukr in words_list.items():
        text_box.insert(tk.END, f"{eng} - {ukr}\n")


def save_edited_words():
    edited_text = text_box.get("1.0", tk.END).splitlines()
    new_dict = {}

    filename = entry_wordslist_name.get().strip()
    if not filename:
        messagebox.showwarning("Помилка", "Введіть назву паку слів")
        return

    path = f"wordlists/{filename}.json"

    for line in edited_text:
        if " - " in line:
            eng, ukr = line.split(" - ", 1)
            new_dict[eng.strip()] = ukr.strip()

    save_words_to_file(new_dict, path)
    messagebox.showinfo("Готово", "Словник збережено!")
    load_word_packs()






def style_button(btn, bg_color="#4CAF50", hover_color="#45a049", fg_color="white"):
    btn.config(
        bg=bg_color, fg=fg_color, relief="flat", bd=0,
        font=("Arial", 12, "bold"), padx=15, pady=5,
        activebackground=hover_color, activeforeground=fg_color
    )
    def on_enter(e):
        btn['background'] = hover_color
    def on_leave(e):
        btn['background'] = bg_color
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def incorrect_sound():
    filepath = os.path.join(BASE_DIR, 'sounds', 'incorrect.mp3')
    pygame.mixer.Sound(filepath).play()

def correct_sound():
    filepath = os.path.join(BASE_DIR, 'sounds', 'correct.mp3')
    pygame.mixer.Sound(filepath).play()




# ---------------- ТЕСТ ----------------
def set_test_state(enabled: bool):
    state = "normal" if enabled else "disabled"
    entry_answer.config(state=state)
    btn_answer.config(state=state)
    btn_hint.config(state=state)


test_words = {}
keys = []
values = []
remaining_words = []  # Копія слів для режиму "all"
wrong_words = []
number_of_asked = 0
correct_answers = 0
streak = 0
current_word = ""
current_direction = 1
test_mode = "20"

def start_test(mode="20"):
    set_mode('typing')
    global test_words, keys, values, remaining_words, number_of_asked, correct_answers, streak, test_mode
    test_mode = mode
    selected_pack = combo_wordpacks.get()
    if not selected_pack:
        messagebox.showwarning("Увага", "Оберіть словник для тестування")
        return
    with open(os.path.join(wordlists_dir, f"{selected_pack}.json"), "r", encoding="utf-8") as f:
        test_words = json.load(f)

    if not test_words:
        messagebox.showwarning("Увага", "Словник пустий, додайте слова!")
        return

    keys = list(test_words.keys())
    values = list(test_words.values())
    remaining_words = keys.copy()  # Створюємо копію ключів для режиму "all"

    number_of_asked = 0
    correct_answers = 0
    streak = 0
    set_test_state(True)

    if mode == "20":
        progress_bar["maximum"] = min(20, len(keys))
    elif mode == "all":
        progress_bar["maximum"] = len(keys)
    else:  # infinite
        progress_bar["maximum"] = float("inf")
    progress_bar["value"] = 0

    next_question()




def start_repeat_mode():
    set_mode('typing')
    global test_words, keys, values
    global remaining_words, number_of_asked, streak, test_mode

    stats = load_stats()

    if not stats["wrong_words"]:
        messagebox.showinfo("Повтор", "Немає помилкових слів 👍")
        return

    test_words = get_repeat_words(stats)
    keys = list(test_words.keys())
    values = list(test_words.values())

    remaining_words = keys.copy()
    number_of_asked = 0
    streak = 0
    test_mode = "all"
    set_test_state(True)
    progress_bar["maximum"] = len(keys)

    next_question()

def next_question():
    global current_word, current_translation
    global current_direction, number_of_asked, remaining_words

    max_words = {"20": 20, "all": len(keys), "infinite": float("inf")}[test_mode]

    if number_of_asked >= max_words or (test_mode == "all" and not remaining_words):
        show_result()
        return

    current_direction = random.choice([1, 2])

    if test_mode == "all":
        current_word = random.choice(remaining_words)
        remaining_words.remove(current_word)
    else:
        current_word = random.choice(keys)

    current_translation = test_words[current_word]  # ✅ ЗАВЖДИ ТУТ

    if current_direction == 1:
        # слово → переклад
        var_word.set(
            f'({number_of_asked+1}/{max_words}) '
            f'Що означає "{current_word}" українською?'
        )
    else:
        # переклад → слово
        var_word.set(
            f'({number_of_asked+1}/{max_words}) '
            f'Як буде "{current_translation}"?'
        )

    entry_answer.delete(0, tk.END)
    var_feedback.set("")




def check_answer(event=None):
    global number_of_asked, streak, correct_answers

    user_input = entry_answer.get().strip().lower()
    if not user_input:
        return

    if current_direction == 1:
        # кілька перекладів: "собака, пес"
        correct_answers_list = [
            t.strip().lower()
            for t in current_translation.split(",")
        ]
        is_correct = user_input in correct_answers_list
    else:
        is_correct = user_input == current_word.lower()

    stats = load_stats()
    add_answer(
        stats,
        word=current_word,                 
        translation=current_translation,   
        is_correct=is_correct
    )
    save_stats(stats)
    update_statistics_ui(stats)

    number_of_asked += 1
    progress_bar["value"] = number_of_asked
    entry_answer.delete(0, tk.END)

    if is_correct:
        correct_answers += 1
        streak += 1
        label_feedback.config(fg="green")
        var_feedback.set(f"Правильно! Стрік: {streak}")
        correct_sound()
        root.after(1200, next_question)
    else:
        wrong_words.append(f'{current_translation} - {user_input}' )
        streak = 0
        label_feedback.config(fg="red")
        if current_direction == 1:
            var_feedback.set(
                f"Неправильно! Правильна відповідь: {current_translation}"
            )
        else:
            var_feedback.set(
                f"Неправильно! Правильна відповідь: {current_word}"
            )
        incorrect_sound()
        root.after(2500, next_question)

    

def show_result():
    global wrong_words, correct_answers
    ratio = correct_answers / number_of_asked if number_of_asked > 0 else 0
    msg = f"Ви відповіли правильно: {correct_answers}/{number_of_asked}\n"
    if ratio > 0.9: msg += "Відмінно!"
    elif ratio > 0.7: msg += "Добре!"
    elif ratio > 0.5: msg += "Непогано!"
    else: msg += "Потрібно більше практики"
    
    if wrong_words:
        msg += '\nСлова які введено неправильно: '
        for word in wrong_words:
            msg += f'\n{word}'
    else:
        msg += "\nВсі слова було введено правильно!!"
    stats = load_stats()
    add_session(stats)
    update_statistics_ui(stats)
    messagebox.showinfo("Результат тесту", msg)
    var_word.set("Тест завершено")
    wrong_words = []
    correct_answers = 0
    var_feedback.set("")
    set_test_state(False)

def give_hint_gui():
    if current_direction == 1:
        hint = test_words[current_word][0]
    else:
        hint = keys[values.index(current_translation)][0]
    var_feedback.set(f"Підказка: перша літера - {hint}")
    label_feedback.config(fg="blue")

# ---------------- GUI ----------------
root = TkinterDnD.Tk()
root.title("Wordly")
root.geometry("640x640")
root.update_idletasks()

width = root.winfo_width()
height = root.winfo_height()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)

root.geometry(f"+{x}+{y}")
icon_path = os.path.join(BASE_DIR, "static", "logo-wordly.ico")
root.iconbitmap(icon_path)

# icon = tk.PhotoImage(file="static/logo-wordly.png")
# root.iconphoto(False, icon)
root.configure(bg="#d9d9d9")
root.resizable(True, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), background="#d9d9d9", padding=[10,5])

notebook_main = ttk.Notebook(root)
notebook_main.pack(expand=True, fill="both", padx=10, pady=10)

# -------- Редактор --------
tab_editor = tk.Frame(notebook_main, bg="#ececec")
notebook_main.add(tab_editor, text="Додати словник")

frame_top = tk.Frame(tab_editor, bg="#ececec")
frame_top.pack(pady=10)
entry_file = tk.Entry(frame_top, width=32, font=("Arial",12))
entry_file.pack(side=tk.LEFT, padx=5)

select_btn = tk.Button(frame_top, text="Огляд", command=select_file)
select_btn.pack(side=tk.LEFT, padx=5)
style_button(select_btn, bg_color="#4CAF50", hover_color="#45a049")

load_file_btn = tk.Button(frame_top, text="Завантажити", command=load_file)
load_file_btn.pack(side=tk.LEFT, padx=5)
style_button(load_file_btn, bg_color="#2196F3", hover_color="#1976D2")


def drop_file(event):
    path = event.data.strip("{}")
    entry_file.delete(0, tk.END)
    entry_file.insert(0, path)
    load_file()  


drop_frame = tk.Frame(
    tab_editor,
    bg="#dddddd",
    height=80,
    bd=2,
    relief="ridge"
)
drop_frame.pack(fill="x", padx=20, pady=10)


drop_label = tk.Label(
    drop_frame,
    text="Перетягніть PDF, DOCX, JSON, TXT файл сюди",
    height=2,
    bg="#dddddd",
    font=("Arial", 12)
)
drop_label.pack(expand=True)

drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind("<<Drop>>", drop_file)


frame_pack = tk.Frame(tab_editor, bg="#ececec")
frame_pack.pack(pady=10)
tk.Label(frame_pack, text="Назва словника:", font=("Arial",12), bg="#ececec").pack(side=tk.LEFT)
entry_wordslist_name = tk.Entry(frame_pack, width=30, font=("Arial",12), state='normal')
entry_wordslist_name.pack(side=tk.LEFT)

tk.Label(
    tab_editor,
    text="Формат: слово - переклад (кожне з нового рядка)",
    font=("Arial", 11),
    fg="gray",
    bg="#ececec"
).pack()



text_box = tk.Text(tab_editor, width=65, height=18, font=("Arial",12), state='normal')
text_box.pack(padx=10, pady=10)

save_wordlist_btn = tk.Button(tab_editor, text="Зберегти словник", command=save_edited_words)
save_wordlist_btn.pack(pady=5)
style_button(save_wordlist_btn, bg_color="#4CAF50", hover_color="#45a049")

# -------- Словники --------




def open_selected_pack(event=None):
    selection = dictionarys_sidebar.curselection()
    if not selection:
        return

    pack_name = dictionarys_sidebar.get(selection[0])
    dictionary_text.delete("1.0", tk.END)

    with open(os.path.join(wordlists_dir, f"{pack_name}.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    for eng, ukr in data.items():
        dictionary_text.insert(tk.END, f"{eng} - {ukr}\n")


def load_word_packs():
    dictionarys_sidebar.delete(0, tk.END)
    pack_text_widgets.clear()

    wordpacks = []

    if os.path.exists(wordlists_dir):
        for file in os.listdir(wordlists_dir):
            if file.endswith(".json"):
                pack_name = file.replace(".json", "")
                wordpacks.append(pack_name)
                dictionarys_sidebar.insert(tk.END, pack_name)

    combo_wordpacks['values'] = wordpacks
    if wordpacks:
        combo_wordpacks.current(0)

def save_current_pack():
    selection = dictionarys_sidebar.curselection()
    if not selection:
        messagebox.showwarning("Увага", "Оберіть словник")
        return

    pack_name = dictionarys_sidebar.get(selection[0])

    data = {}
    for line in dictionary_text.get("1.0", tk.END).splitlines():
        if " - " in line:
            eng, ukr = line.split(" - ", 1)
            data[eng.strip()] = ukr.strip()

    with open(os.path.join(wordlists_dir, f"{pack_name}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    messagebox.showinfo("Готово", f"Пак «{pack_name}» збережено")

def delete_current_pack():
    selection = dictionarys_sidebar.curselection()
    if not selection:
        messagebox.showwarning("Увага", "Оберіть словник")
        return

    pack_name = dictionarys_sidebar.get(selection[0])
    os.remove(f"wordlists/{pack_name}.json")

    dictionary_text.delete("1.0", tk.END)
    load_word_packs()

    messagebox.showinfo("Готово", f"Пак «{pack_name}» видалено")


tab_words = tk.Frame(notebook_main, bg="#e0e0e0")
notebook_main.add(tab_words, text="Мої словники")



content_frame = tk.Frame(tab_words, bg="#e0e0e0")
content_frame.pack(expand=True, fill=tk.BOTH)

buttons_frame = tk.Frame(tab_words, bg="#e0e0e0")
buttons_frame.pack(fill=tk.X, pady=5)


dictionarys_sidebar = tk.Listbox(
    content_frame,
    width=25,
    font=("Arial", 12, "bold"),
    bg="#f0f0f0",       
    fg="#333333",       
    selectbackground="#4CAF50",  
    selectforeground="black",    
    bd=0,               
    highlightthickness=0 
)

dictionarys_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
dictionarys_sidebar.bind("<<ListboxSelect>>", open_selected_pack)

dictionary_text = tk.Text(content_frame, font=("Arial", 12), state='normal')
dictionary_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)



save_cur_wordlist_btn = tk.Button(buttons_frame, text="Зберегти поточний словник",width=30, command=save_current_pack)
save_cur_wordlist_btn.pack(pady=5)
style_button(save_cur_wordlist_btn, bg_color="#4CAF50", hover_color="#45a049")

delete_cur_wordlist_btn = tk.Button(buttons_frame, text="Видалити поточний словник",width=30,command=delete_current_pack)
delete_cur_wordlist_btn.pack(pady=5)
style_button(delete_cur_wordlist_btn, bg_color="#C42D2D", hover_color="#9b1313")


# -------- Тестування --------
tab_wordstest = tk.Frame(notebook_main, bg="#f5f5f5")
notebook_main.add(tab_wordstest, text="Тестування")



mode_frame = tk.Frame(tab_wordstest)
mode_frame.pack(pady=5)
tk.Label(tab_wordstest, text="Оберіть словник для тестування:", font=("Arial",12), bg="#f5f5f5").pack(pady=5)
combo_wordpacks = ttk.Combobox(tab_wordstest, state="readonly", width=40, font=("Arial",12))
combo_wordpacks.pack(pady=5)

frame_modes = tk.Frame(tab_wordstest, bg="#f5f5f5")
frame_modes.pack(pady=5)


top_row = tk.Frame(frame_modes, bg="#f5f5f5")
top_row.pack(pady=3)

# нижній ряд
bottom_row = tk.Frame(frame_modes, bg="#f5f5f5")
bottom_row.pack(pady=3)

btn_20 = tk.Button(top_row, text="20 слів", command=lambda:start_test("20"))
btn_20.pack(side=tk.LEFT, padx=5)
style_button(btn_20)

btn_infinity = tk.Button(top_row, text="Нескінченно", command=lambda:start_test("infinite"))
btn_infinity.pack(side=tk.LEFT, padx=5)
style_button(btn_infinity)

btn_all_words = tk.Button(top_row, text="Всі слова", command=lambda:start_test("all"))
btn_all_words.pack(side=tk.LEFT, padx=5)
style_button(btn_all_words)


repeat_wrong_words_btn = tk.Button(
    bottom_row,
    text="🔁 Повторити помилки",
    font=("Arial", 12, "bold"),
    command=start_repeat_mode,
)

repeat_wrong_words_btn.pack(side=tk.LEFT, padx=5)
style_button(repeat_wrong_words_btn)

matching_btn = tk.Button(
    bottom_row,
    text="🔗 Відповідність",
    command=lambda: set_mode("matching")
)


matching_btn.pack(side=tk.LEFT, padx=5)
style_button(matching_btn)



matching_frame = tk.Frame(tab_wordstest,bg="#f5f5f5")


typing_frame = tk.Frame(tab_wordstest)
typing_frame.pack(pady=0)  

var_word = tk.StringVar()
var_feedback = tk.StringVar()

frame_buttons = tk.Frame(typing_frame, bg="#f5f5f5")
frame_buttons.pack(pady=5)

cur_word_label = tk.Label(frame_buttons, textvariable=var_word, font=("Arial",14), wraplength=500, justify=tk.LEFT, bg="#f5f5f5", state='normal')
cur_word_label.pack(pady=10)

entry_answer = tk.Entry(frame_buttons, width=30, font=("Arial",12))
entry_answer.pack(pady=5)


entry_answer.bind('<Return>', check_answer)



btn_answer = tk.Button(
    frame_buttons,
    text="Відповісти",
    width=12,
    command=check_answer
)
btn_answer.pack(side=tk.TOP, pady=10)
style_button(btn_answer)

btn_hint = tk.Button(
    frame_buttons,
    text="Підказка",
    width=12,
    command=give_hint_gui
)
btn_hint.pack(side=tk.TOP, pady=10)
style_button(btn_hint)


label_feedback = tk.Label(
    typing_frame,
    textvariable=var_feedback,
    font=("Arial", 12),
    bg="#f5f5f5",
    wraplength=500,
    justify="center"
)
label_feedback.pack(pady=(5, 10))




bottom_bar = tk.Frame(tab_wordstest, bg="#f5f5f5")
bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)


progress_bar = ttk.Progressbar(bottom_bar, orient="horizontal", length=500, mode="determinate",)
progress_bar.pack(pady=10)

# -----------------ВІДПОВІДНІСТЬ---------------

selected_left = None
selected_right = None

matching_pairs = {}
matched_words = set()

buttons_left = {}
buttons_right = {}
canvas_lines = None


def start_matching():
    global selected_word, matching_pairs, matched_words
    selected_pack = combo_wordpacks.get()
    
    with open(os.path.join(wordlists_dir, f"{selected_pack}.json"), "r", encoding="utf-8") as f:
        test_words = json.load(f)
    words_count = len(test_words)

    if words_count < 2:
        messagebox.showwarning(
            "Недостатньо слів",
            "Для вправи відповідності потрібно мінімум 2 слова."
        )
        return
    pair_count = min(4, words_count)  # ✅ ГОЛОВНЕ ВИПРАВЛЕННЯ

    selected_word = None
    matched_words = set()
    matching_pairs = {}

    clear_frame(matching_frame)
    matching_frame.pack(pady=10)

    pairs = random.sample(list(test_words.items()), pair_count)

    left_words = []
    right_translations = []

    for word, translation in pairs:
        main_translation = translation.split(",")[0].strip()
        matching_pairs[word] = main_translation
        left_words.append(word)
        right_translations.append(main_translation)

    random.shuffle(right_translations)

    build_matching_ui(left_words, right_translations)



def build_matching_ui(left_words, right_words):
    global buttons_left, buttons_right, canvas_lines
    buttons_left = {}
    buttons_right = {}

    container = tk.Frame(matching_frame)
    container.pack()

    left_frame = tk.Frame(container)
    canvas_lines = tk.Canvas(
        container,
        width=120,
        bg="#f5f5f5",
        highlightthickness=0
    )
    right_frame = tk.Frame(container)

    left_frame.grid(row=0, column=0, padx=10)
    canvas_lines.grid(row=0, column=1)
    right_frame.grid(row=0, column=2, padx=10)
    tk.Label(left_frame, text="Слова", font=("Arial", 14, "bold")).pack(pady=5)
    tk.Label(right_frame, text="Переклади", font=("Arial", 14, "bold")).pack(pady=5)



    for word in left_words:
        btn = tk.Button(
            left_frame,
            text=word,
            width=20,
            font=("Arial", 10),
            wraplength=120,   
            justify="center",
            command=lambda w=word: select_word(w)
        )
        btn.pack(pady=4)
        buttons_left[word] = btn

    for tr in right_words:
        btn = tk.Button(
            right_frame,
            text=tr,
            width=20,
            wraplength=120,   
            justify="center",
            font=("Arial", 10),
            command=lambda t=tr: select_translation(t)
        )
        btn.pack(pady=4)
        buttons_right[tr] = btn

def select_word(word):
    global selected_left

    if buttons_left[word]['state'] == 'disabled':
        return

    selected_left = word

    for btn in buttons_left.values():
        if btn['state'] == 'normal':
            btn.config(bg="SystemButtonFace")

    buttons_left[word].config(bg="lightblue")

    try_match()


def select_translation(translation):
    global selected_right

    if buttons_right[translation]['state'] == 'disabled':
        return

    selected_right = translation

    for btn in buttons_right.values():
        if btn['state'] == 'normal':
            btn.config(bg="SystemButtonFace")

    buttons_right[translation].config(bg="lightblue")

    try_match()



def draw_line(btn_left, btn_right):
    
    x1 = btn_left.winfo_rootx() + btn_left.winfo_width()
    y1 = btn_left.winfo_rooty() + btn_left.winfo_height() // 2

    x2 = btn_right.winfo_rootx()
    y2 = btn_right.winfo_rooty() + btn_right.winfo_height() // 2

    
    cx = canvas_lines.winfo_rootx()
    cy = canvas_lines.winfo_rooty()

    return canvas_lines.create_line(
        x1 - cx, y1 - cy,
        x2 - cx, y2 - cy,
        width=3,
        fill="green"
    )

def try_match():
    global selected_left, selected_right

    if not selected_left or not selected_right:
        return

    btn_left = buttons_left[selected_left]
    btn_right = buttons_right[selected_right]

    line = draw_line(btn_left, btn_right)

    if matching_pairs[selected_left] == selected_right:
        btn_left.config(bg="lightgreen", state="disabled")
        btn_right.config(bg="lightgreen", state="disabled")
        matched_words.add(selected_left)
        stats = load_stats()
        add_answer(
            stats,
            word=selected_left,                 
            translation=matching_pairs[selected_left], 
            is_correct=True
        )
        save_stats(stats)
        update_statistics_ui(stats)
        correct_sound()
    else:
        btn_left.config(bg="red")
        btn_right.config(bg="red")
        stats = load_stats()
        add_answer(
            stats,
            word=selected_left,                 
            translation=matching_pairs[selected_left],   
            is_correct=False
        )
        save_stats(stats)
        update_statistics_ui(stats)
        incorrect_sound()

        matching_frame.after(
            800,
            lambda: (
                canvas_lines.delete(line),
                reset_colors(selected_left, selected_right)
            )
        )

    selected_left = None
    selected_right = None

    if len(matched_words) == len(matching_pairs):
        matching_frame.after(600, finish_matching)

def reset_colors(word, translation):
    if word in buttons_left:
        if buttons_left[word]['state'] == 'normal':
            buttons_left[word].config(bg="SystemButtonFace")

    if translation in buttons_right:
        if buttons_right[translation]['state'] == 'normal':
            buttons_right[translation].config(bg="SystemButtonFace")



def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def finish_matching():
    messagebox.showinfo("Готово", "Всі відповідності знайдені 🎉")
    matching_frame.pack_forget()
    stats = load_stats()
    add_session(stats)
    update_statistics_ui(stats)
    set_mode("typing")


def set_mode(mode):
    typing_frame.pack_forget()
    matching_frame.pack_forget()

    if mode == "typing":
        typing_frame.pack(pady=10)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    elif mode == "matching":
        matching_frame.pack(pady=10)
        bottom_bar.pack_forget()
        start_matching()






# ----------------СТАТИСТИКА-------------
tab_statistics = tk.Frame(notebook_main, bg="#f5f5f5")
notebook_main.add(tab_statistics, text="Статистика")
FONT = ("Arial", 14, "bold")


def update_wrong_words_ui(stats):
    if not stats["wrong_words"]:
        wrong_words_var.set("Неправильні слова: —")
        return

    text = "Неправильні слова:\n"

    for word, data in stats["wrong_words"].items():
        text += f"• {word} — {data['translation']} ({data['count']} раз.)\n"

    wrong_words_var.set(text)


def update_statistics_ui(stats):
    total_answers_var.set(f"Загалом відповідей: {stats['total_answers']}")
    correct_answers_var.set(f"Правильних відповідей: {stats['correct_answers']}")
    wrong_answers_var.set(f"Неправильних відповідей: {stats['wrong_answers']}")
    sessions_var.set(f"Кількість тестувань: {stats['sessions']}")
    current_streak_var.set(f"Поточний стрік: {stats['current_streak']}")
    longest_streak_var.set(f"Найдовший стрік: {stats['longest_streak']}")

    update_wrong_words_ui(stats)

total_answers_var = tk.StringVar()
correct_answers_var = tk.StringVar()
wrong_answers_var = tk.StringVar()
sessions_var = tk.StringVar()
current_streak_var = tk.StringVar()
longest_streak_var = tk.StringVar()
wrong_words_var = tk.StringVar()


def create_statistics_ui(parent):
    tk.Label(parent, textvariable=total_answers_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)

    tk.Label(parent, textvariable=correct_answers_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)

    tk.Label(parent, textvariable=wrong_answers_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)

    tk.Label(parent, textvariable=sessions_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)

    tk.Label(parent, textvariable=current_streak_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)

    tk.Label(parent, textvariable=longest_streak_var, font=FONT, anchor="w") \
        .pack(fill="x", padx=10, pady=3)
    


def get_repeat_words(stats: dict):
    return {
        word: data["translation"]
        for word, data in stats["wrong_words"].items()
    }

def clear_repeat_words():
    stats = load_stats()
    stats['wrong_words'] = {}
    save_stats(stats)
    update_wrong_words_ui(stats)

def clear_statistics():
    stats = {
            "total_answers": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "sessions": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "wrong_words": {}
        }
    save_stats(stats)
    update_wrong_words_ui(stats)
    update_statistics_ui(stats)

    

create_statistics_ui(tab_statistics)
tk.Label(
    tab_statistics,
    textvariable=wrong_words_var,
    font=("Arial", 12),
    anchor="w",
    justify="left",
    wraplength=500
).pack(fill="x", padx=10, pady=5)

clear_wrong_words_btn = tk.Button(tab_statistics, 
                                     font=('Arial',12),
                                     text="Очистити неправильні слова",
                                     width=30,
                                     command=clear_repeat_words)
clear_wrong_words_btn.pack(pady=5)
style_button(clear_wrong_words_btn)

clear_statistics_btn = tk.Button(tab_statistics,
                                font=('Arial',12),
                                text="Очистити статистику",
                                width=30,
                                command=clear_statistics)

clear_statistics_btn.pack(pady=5)
style_button(clear_statistics_btn, bg_color="#C42D2D", hover_color="#9b1313")
stats = load_stats()
save_stats(stats)
update_statistics_ui(stats)


# ---------------- СТАРТ ----------------
load_word_packs()
set_test_state(False)
set_mode('typing')
root.mainloop()
