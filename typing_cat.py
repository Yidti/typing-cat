from tkinter import *
from PIL import ImageTk, Image
from allowable_input import *
import math
import time
import threading

_theme_color_1 = 'Light Blue'
_theme_color_2 = 'Sky Blue'
_theme_color_3 = 'Light Steel Blue'
_theme_color_4 = 'Steel Blue'
_theme_color_5 = 'Dodger Blue'
TEST_MIN = 1


class CustomButton(Button):
    def __init__(self, *args, **kwargs):
        Button.__init__(self, *args, **kwargs)
        self['highlightthickness'] = 2
        self['relief'] = FLAT
        self['borderwidth'] = 0
        self['highlightbackground'] = _theme_color_3
        self['font'] = ("Arial", 25)


def get_display_size():
    root = Tk()
    root.update_idletasks()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return width, height


class TypingCat(Tk):

    def __init__(self):
        super().__init__()
        self._timer_running = False
        self.typing_img = None
        self._screen = get_display_size()
        self._char_number = 0
        self._word_index = 0
        self._input_length = 0
        self._file_data: str = ""
        self._input_data: str = ""
        self._words = []
        self._answers = []
        self.typing_words = []
        self._correct = 0
        self._wrong = 0
        self._wpm = 0
        self._typing_running = False
        self.timer_text: Text = None
        self.words_text: Text = None
        self.correct_text: Text = None
        self.wrong_text: Text = None
        self.wpm_text: Text = None
        self.timer_button: Button = None
        self.typing_text: Text = None
        self.timer: threading = None
        self.test_sec = 0
        self.initial_ui()

    def initial_ui(self):
        self.title("Typing Cat")
        self.config(background=_theme_color_1, pady=10)
        center_x = self._screen[0] // 2 - 800 // 2
        center_y = self._screen[1] // 2 - 600 // 2
        self.geometry('{}x{}+{}+{}'.format(800, 600, center_x, center_y))
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=30)
        self.columnconfigure(0, weight=1)
        # timer frame
        timer_frame = Frame(self, bg=_theme_color_2, bd=1, relief=FLAT)
        timer_frame.grid(row=0, column=0, sticky=NSEW, pady=10)
        timer_frame.rowconfigure(0, weight=1)
        timer_frame.columnconfigure(0, weight=1)
        timer_frame.columnconfigure(1, weight=6)
        timer_frame.columnconfigure(2, weight=1)
        timer_frame.columnconfigure(3, weight=1)
        timer_frame.columnconfigure(4, weight=1)
        timer_frame.columnconfigure(5, weight=1)
        timer_frame.columnconfigure(6, weight=1)

        image = Image.open("typing.png").resize((50, 50))
        self.typing_img = ImageTk.PhotoImage(image=image)
        label = Label(timer_frame, text="Test", bg=_theme_color_2, image=self.typing_img)
        label.grid(row=0, column=0, sticky=NSEW, padx=10)
        self.timer_text = Label(timer_frame, text="00:00", font=("Arial", 60))
        self.timer_text.grid(row=0, column=1, sticky=NSEW, padx=10)
        self.correct_text = Label(timer_frame, text="??\nCorrect", font=("Arial", 20))
        self.correct_text.grid(row=0, column=2, sticky=NSEW, padx=10)
        self.wrong_text = Label(timer_frame, text="??\nWrong", font=("Arial", 20))
        self.wrong_text.grid(row=0, column=3, sticky=NSEW, padx=10)
        self.wpm_text = Label(timer_frame, text="??\nWPM", font=("Arial", 20))
        self.wpm_text.grid(row=0, column=4, sticky=NSEW, padx=10)
        self.words_text = Label(timer_frame, text="??\nWords", font=("Arial", 20))
        self.words_text.grid(row=0, column=5, sticky=NSEW, padx=10)

        self.timer_button = CustomButton(timer_frame, text="Start", command=self.press_timer)
        self.timer_button['font'] = ("Arial", 40)
        self.timer_button.grid(row=0, column=6, sticky=NSEW, padx=10)
        # Typing frame
        picture_frame = Frame(bg=_theme_color_4, bd=0, pady=5, relief=FLAT)
        picture_frame.grid(row=1, column=0, sticky=NSEW)
        picture_frame.columnconfigure(0, weight=1)
        picture_frame.rowconfigure(0, weight=1)
        self.typing_text = Text(picture_frame, font=("Arial", 29), wrap="word")
        self.typing_text.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)

        sample = open("typing-sample1.txt", "r")
        self._file_data = sample.read()
        # self.typing_text.insert(INSERT, self._file_data)
        self.typing_text.bind("<Key>", lambda event: self.listen(event))
        self.typing_text.focus()

        # check data
        self.check_data()

    def check_data(self):
        print(f"Character count: {len(self._file_data)}")
        self._words = self._file_data.split(" ")
        self._answers = [word.strip(",").strip(".").strip("?") for word in self._words]
        print(f"Word count: {len(self._words)}")
        self.correct_text['text'] = f"{self._correct}\nCorrect"
        self.wrong_text['text'] = f"{self._wrong}\nWrong"
        self.wpm_text['text'] = f"{self._wpm}\nWPM"
        self.words_text['text'] = f"{len(self._words)}\nWords"

    def listen(self, event):
        if event.char in allowable_list() and self._typing_running is True:
            # check a word if be finished when tying length equal to list item length
            temp_word_length = len(self._words[self._word_index])
            if event.char != " " and self._input_length != temp_word_length:
                self._input_length += 1
            elif event.char == " " and self._input_length != temp_word_length:
                return "break"
            elif event.char != " " and self._input_length == temp_word_length:
                return "break"
            elif event.char == " " and temp_word_length == self._input_length:
                print("get a word")
                self.check_answer()
                self._input_length = 0
                self._word_index += 1
            # save input
            self._input_data = self._input_data + event.char
            # check input if right or wrong
            if event.char == self._file_data[self._char_number]:
                self.typing_text.tag_add(f"right.{self._char_number}", f"1.{self._char_number}",
                                         f"1.{self._char_number + 1}")
                self.typing_text.tag_config(f"right.{self._char_number}", foreground="green", font=("Arial", 29))
            else:
                self.typing_text.tag_add(f"error.{self._char_number}", f"1.{self._char_number}",
                                         f"1.{self._char_number + 1}")
                self.typing_text.tag_config(f"error.{self._char_number}", foreground="red", font=("Arial", 29))
            # move cursor
            self.typing_text.mark_set("insert", "1.%d" % (self._char_number + 1))
            # add char number
            self._char_number += 1

            if self._word_index + 1 == len(self._words) and self._input_length == temp_word_length:
                self._typing_running = False
                self._timer_running = False
                self.timer_button['text'] = "Start"
                self.check_answer()
                # print("Game Over")
                return "break"

            return "break"

        else:
            return "break"

    def check_answer(self):
        # check answer
        self.typing_words = self._input_data.strip().split(" ")
        self.typing_words = [word.strip(",").strip(".").strip("?") for word in self.typing_words]
        self._correct = 0
        self._wrong = 0
        for (index, word) in enumerate(self.typing_words):
            if word == self._answers[index]:
                self._correct += 1
            else:
                self._wrong += 1
        self.correct_text['text'] = f"{self._correct}\nCorrect"
        self.wrong_text['text'] = f"{self._wrong}\nWrong"

        self.wpm_text['text'] = f"{round(self._correct / ((TEST_MIN * 60 - self.test_sec) / 60), 2)}\nWPM"

    def count_down(self, count):
        count_min = math.floor(count / 60)
        count_sec = count % 60

        if count_sec < 10:
            count_sec = f"0{count_sec}"
        self.timer_text['text'] = f"{count_min}:{count_sec}"

    def time_thread(self):
        self.test_sec = TEST_MIN * 60

        while self._timer_running and self._typing_running:
            time.sleep(1)
            self.count_down(self.test_sec)
            if self.test_sec == 0:
                self._timer_running = False
                self._typing_running = False
                self.timer_button['text'] == "Start"
            else:
                self.test_sec -= 1

    def press_timer(self):
        if self.timer_button['text'] == "Start":
            self.typing_text.delete("1.0", "end")
            self.typing_text.insert(INSERT, self._file_data)
            self.reset()
            self.typing_text.focus()
            self.timer_button['text'] = "Stop"
            self._timer_running = True
            self._typing_running = True
            self.timer = threading.Thread(target=self.time_thread)
            self.timer.daemon = True
            self.timer.start()
        else:
            self.timer_button['text'] = "Start"
            self._timer_running = False

    def reset(self):
        self._char_number = 0
        self._word_index = 0
        self._input_data = ""
        self._input_length = 0
        self._input_data = ""
        self.typing_text.mark_set("insert", "1.0")

    def run(self):
        self.mainloop()
