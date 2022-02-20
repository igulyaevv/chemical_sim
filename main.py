from classes import Board
from classes.Drawer import Drawer

import tkinter as tk
from tkinter import ttk, messagebox, HORIZONTAL
from tkinter.filedialog import askopenfilename, asksaveasfilename

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ChemicalApp(Drawer):  # (tk)
    def __init__(self) -> None:
        self.N = 0
        self.mode = 0
        self.b = 0.0
        self.ts = 0.0
        self.u = 0.0
        self.G = 0

        self.WIN_W = 1280
        self.WIN_H = 720
        self.SIDEBAR_W = 200
        self.SIDEBAR_H = self.WIN_H
        self.GRAPHBAR_W = 400
        self.GRAPHBAR_H = self.WIN_H / 2
        self.STATBAR_W = 400
        self.STATBAR_H = self.WIN_H / 2
        self.CANVAS_W = self.WIN_W - self.SIDEBAR_W - self.GRAPHBAR_W
        self.CANVAS_H = self.WIN_H
        self.window = tk.Tk()
        self.sidebar = tk.Frame(self.window, width=self.SIDEBAR_W, height=self.SIDEBAR_H, bd=4, relief=tk.GROOVE)
        self.graphbar = tk.Frame(self.window, width=self.GRAPHBAR_W, height=self.GRAPHBAR_H, bd=4, relief=tk.GROOVE)
        self.statbar = tk.Frame(self.window, width=self.STATBAR_W, height=self.STATBAR_H, bd=4, relief=tk.GROOVE)
        self.canvas = tk.Canvas(self.window, width=self.CANVAS_W, height=self.CANVAS_H, bg="#012")

        self.vcmd = (self.window.register(self.validate), "%P")

        self.graph = None

        self.label_height = tk.Label(self.sidebar, text="Размер поверхности")
        self.textbox_height = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_mode = tk.Label(self.sidebar, text="Режим моделирования")
        self.combobox_mode = ttk.Combobox(self.sidebar, values=["Постояннотоковый", "Переменнотоковый"])
        self.combobox_mode.bind("<<ComboboxSelected>>", self.change_label_create)
        self.label_create = tk.Label(self.sidebar, text="Вероятность появления")
        self.textbox_create = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_ts = tk.Label(self.sidebar, text="Вероятность перехода")
        self.textbox_ts = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_margin = tk.Label(self.sidebar, text="Вероятность слияния")
        self.textbox_margin = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_count = tk.Label(self.sidebar, text="Количество итераций")
        self.textbox_count = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_sleep = tk.Label(self.sidebar, text="Задержка между итерациями")
        self.scale_sleep = tk.Scale(self.sidebar, from_=0, to=5, orient=HORIZONTAL)

        self.stat_atoms = tk.Label(self.statbar)
        self.stat_atoms_wasted = tk.Label(self.statbar)
        self.stat_med_weight = tk.Label(self.statbar)
        self.stat_avg_weight = tk.Label(self.statbar)
        self.stat_span_weight = tk.Label(self.statbar)

        self.btb_run = tk.Button(self.sidebar, text="Run", command=self.run_btn)
        self.btn_pause = tk.Button(self.sidebar, text="Pause", command=self.pause_btn)
        self.btn_restart = tk.Button(self.sidebar, text="Rerun", command=self.restart_btn)
        self.btn_pause["state"] = "disabled"
        self.btn_restart["state"] = "disabled"
        self.btn_result = tk.Button(self.sidebar, text="Result", command=self.result_btn)
        self.btn_result["state"] = "disabled"
        self.btn_openconfig = tk.Button(self.sidebar, text="Открыть конфиг", command=self.open_configfile)
        self.btn_saveconfig = tk.Button(self.sidebar, text="Сохранить конфиг", command=self.save_configfile)

        self.board = None
        self.is_exit = False

    def open_configfile(self) -> None:
        """Open a config file"""
        filepath = askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r") as input_file:
            text = input_file.readlines()
            if len(text) < 6:
                messagebox.showinfo("Warning", "Bad config")
                self.is_exit = True
                return
            else:
                self.is_exit = False
                self.textbox_height.insert(0, text[0].replace('\n', ''))
                self.combobox_mode.insert(0, "Переменнотоковый" if text[1].replace('\n', '') == '1'
                                                                else "Постояннотоковый")
                self.textbox_create.insert(0, text[2].replace('\n', ''))
                self.textbox_ts.insert(0, text[3].replace('\n', ''))
                self.textbox_margin.insert(0, text[4].replace('\n', ''))
                self.textbox_count.insert(0, text[5].replace('\n', ''))

        self.window.title(f"Chemical Simulator - {filepath}")

    def save_configfile(self) -> None:
        """Save current parameters to a new config file"""
        filepath = asksaveasfilename(
            defaultextension="txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, 'w') as output_file:
            self.set_params()
            for item in [self.N, self.mode, self.b, self.ts, self.u, self.G]:
                output_file.write(str(item) + '\n')
        self.window.title(f"Chemical Simulator - {filepath}")

    def validate(self, new_value) -> bool:
        try:
            if new_value == '' or new_value == '-' or new_value == '+':
                return True
            _str = str(float(new_value))
            return True
        except:
            return False

    def set_params(self) -> None:
        if self.textbox_height.get() == '' or self.combobox_mode.get() == '' or self.textbox_create.get() == '' \
                or self.textbox_ts.get() == '' or self.textbox_margin.get() == '' or self.textbox_count.get() == '':
            messagebox.showinfo("Warning", "Заполнены не все поля")
            self.is_exit = True
            return
        self.is_exit = False
        self.N = int(self.textbox_height.get())
        self.mode = 1 if self.combobox_mode.get() == "Переменнотоковый" else 0
        self.b = float(self.textbox_create.get())
        self.ts = float(self.textbox_ts.get())
        self.u = float(self.textbox_margin.get())
        self.G = int(self.textbox_count.get())

    def configurate(self) -> None:
        self.window.config(width=self.WIN_W, height=self.WIN_H)
        self.window.resizable(False, False)
        self.window.title("Chemical Simulator")
        self.sidebar.place(x=0, y=0)
        self.graphbar.place(x=self.SIDEBAR_W, y=0)
        self.statbar.place(x=self.SIDEBAR_W, y=self.STATBAR_H)
        self.canvas.place(x=self.SIDEBAR_W + self.GRAPHBAR_W, y=0)

        self.label_height.place(x=10, y=0)
        self.textbox_height.place(x=12, y=25)
        self.label_mode.place(x=10, y=50)
        self.combobox_mode.place(x=12, y=75)
        self.label_create.place(x=10, y=100)
        self.textbox_create.place(x=12, y=125)
        self.label_ts.place(x=10, y=150)
        self.textbox_ts.place(x=12, y=175)
        self.label_margin.place(x=10, y=200)
        self.textbox_margin.place(x=12, y=225)
        self.label_count.place(x=10, y=250)
        self.textbox_count.place(x=12, y=275)
        self.label_sleep.place(x=12, y=600)
        self.scale_sleep.place(x=12, y=630)

        self.stat_atoms.place(x=10, y=10)
        self.stat_atoms_wasted.place(x=10, y=60)
        self.stat_med_weight.place(x=10, y=110)
        self.stat_avg_weight.place(x=10, y=160)
        self.stat_span_weight.place(x=10, y=210)

        self.btb_run.place(x=12, y=325, width=int(self.SIDEBAR_W / 3))
        self.btn_pause.place(x=12, y=350, width=int(self.SIDEBAR_W / 3))
        self.btn_restart.place(x=12, y=375, width=int(self.SIDEBAR_W / 3))
        self.btn_result.place(x=self.SIDEBAR_W - 20 - int(self.SIDEBAR_W / 3), y=350, width=int(self.SIDEBAR_W / 3))
        self.btn_openconfig.place(x=12, y=425)
        self.btn_saveconfig.place(x=12, y=450)

    def run_btn(self) -> None:
        self.set_params()

        if self.is_exit:
            return

        if not self.board:
            self.board = Board(self.N, self.b, self.ts, self.u, self.mode)
            self.textbox_height["state"] = "disabled"
            self.combobox_mode["state"] = "disabled"
            self.textbox_create["state"] = "disabled"
            self.textbox_ts["state"] = "disabled"
            self.textbox_margin["state"] = "disabled"
        else:
            self.G = int(self.textbox_count.get()) if self.textbox_count and self.textbox_count != '' else 0

        self.btb_run["state"] = "disabled"
        self.btn_pause["state"] = "active"
        self.btn_restart["state"] = "disabled"
        self.btn_result["state"] = "active"
        self.run()

    def pause_btn(self) -> None:
        self.is_exit = True
        self.btn_pause["state"] = "disabled"
        self.btn_restart["state"] = "active"
        self.btb_run["state"] = "active"

    def result_btn(self) -> None:
        if self.board:
            with open("WeightAnalysis.txt", 'w') as file:
                for key, value in self.board.create_bar().items():
                    for i in range(value):
                        file.write(str(key) + ' ')

    def restart_btn(self):
        if self.board:
            self.board = None

        self.textbox_height.delete(0, 'end')
        self.combobox_mode.delete(0, 'end')
        self.textbox_create.delete(0, 'end')
        self.textbox_ts.delete(0, 'end')
        self.textbox_margin.delete(0, 'end')

        self.textbox_height["state"] = "normal"
        self.combobox_mode["state"] = "normal"
        self.textbox_create["state"] = "normal"
        self.textbox_ts["state"] = "normal"
        self.textbox_margin["state"] = "normal"

        self.btn_result["state"] = "disabled"

        if self.graph:
            self.graph.get_tk_widget().destroy()

        self.stat_atoms.config(text='')
        self.stat_atoms_wasted.config(text='')
        self.stat_med_weight.config(text='')
        self.stat_avg_weight.config(text='')
        self.stat_span_weight.config(text='')

        self.canvas.delete("all")

    def get_graph(self) -> None:
        if self.graph:
            self.graph.get_tk_widget().destroy()

        dictionary = self.board.create_bar()
        print(dictionary)

        fig = Figure(figsize=((self.GRAPHBAR_W - 10) / 100, (self.GRAPHBAR_H - 10) / 100), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel("Weight", fontsize=10)
        ax.set_ylabel("Count",  fontsize=10)
        rect = ax.bar(dictionary.keys(), dictionary.values(), width=.5, color='g')

        self.graph = FigureCanvasTkAgg(fig, self.graphbar)
        self.graph.draw()
        self.graph.get_tk_widget().place(x=0, y=0)

    def get_stat(self) -> None:
        stat = self.board.conclusion_dict()
        self.stat_atoms.config(text=f"Всего присоединилось атомов: {stat.get('atoms')}")
        self.stat_atoms_wasted.config(text=f"Потеряно атомов: {stat.get('loss')}")
        self.stat_med_weight.config(text=f"Медиана веса кластеров: {stat.get('med')}")
        self.stat_avg_weight.config(text=f"Среднее значение веса кластеров: {stat.get('avg')}")
        self.stat_span_weight.config(text=f"Размах веса кластеров: {stat.get('span')}")

    def change_label_create(self, _) -> None:
        if self.combobox_mode.get() == "Постояннотоковый":
            self.label_create.config(text="Вероятность появления")
        else:
            self.label_create.config(text="Правая граница вероятности")

    def draw_point(self, row: int, col: int, color_idx: int) -> None:
        diff = self.canvas.winfo_height() / self.board.rows
        colors = ["#ffffff", "#e32636", "#00ffff", "#ffe135", "#1dacd6"]
        self.canvas.create_oval(col * diff, row * diff, col * diff + diff, row * diff + diff,
                                fill=colors[0] if color_idx == 0 else colors[color_idx % len(colors)])

    def start(self) -> None:
        self.configurate()
        self.window.mainloop()

    def run(self) -> None:
        while self.G > 0 and not self.is_exit:
            self.board.Run()
            self.canvas.delete("all")
            self.board.draw(self)
            self.canvas.update()
            self.get_graph()
            self.get_stat()
            self.G -= 1
            self.textbox_count.delete(0, 'end')
            self.textbox_count.insert(0, str(self.G))
            self.window.after(self.scale_sleep.get() * 1000)
        self.is_exit = False
        self.btn_pause["state"] = "disabled"
        self.btb_run["state"] = "active"


app = ChemicalApp()
app.start()


def main():
    print('Выберите способ ввода входных параметров: 1 - из файла; 2 - с клавиатуры.')
    choice = int(input())

    N = 0
    mode = 0
    b = 0.0
    ts = 0.0
    u = 0.0
    G = 0

    if choice != 2:
        # config adaptation
        print(f'Количество секторов сетки: {N}')
        print(f'Режим: {"- постояннотоковый" if mode == 0 else ("- переменнотоковый" if mode == 1 else None)}')
        if mode == 0:
            print('Вероятность появления атома: ')
        elif mode == 1:
            print('Правая граница вероятности появления атома: ')
        else:
            print('Выбран некорректный режим')
            return 1
        print(b)
        print(f'Вероятность перехода атома в соседнюю ячейку: {ts}')
        print(f'Вероятность слияния кластеров при столкновении их не на поверхности: {u}')
        print(f'Количество проходов по сетке: {G}')
    else:
        print('Введите число N - количество секторов сетки: ')
        N = int(input())
        print('Задание вероятностей')
        print('Выберите режим: 0 - постояннотоковый, 1 - переменнотоковый: ')
        mode = int(input())
        if mode == 0:
            print('Вероятность появления атома: ')
        elif mode == 1:
            print('Введите правую границу вероятности появления: ')
        else:
            print('Выбран некорректный режим')
            return 2
        b = float(input())
        print('Вероятность перехода атома в соседнюю ячейку: ')
        ts = float(input())
        print('Вероятность слияния кластеров при столкновении их не на поверхности: ')
        u = float(input())
        print('Введите количество G проходов по сетке: ')
        G = int(input())

    if N < 0 or b < 0 or b > 1 or ts < 0 or ts > 1 or u < 0 or u > 1 or G < 0 or mode > 1 or mode < 0:
        print('Введены некорректные данные')
        return 3

    print('Все данные введены правильно? Y/N')
    vote = input()
    if vote == 'N':
        return 4

    board = Board(N, b, ts, u, mode)

    step = 0
    while step < G:
        board.Run()
        step += 1
    board.Conclusion()

    print('\nДля выхода введите любой символ')
    vote = input()
    return 5

# if __name__ == '__main__':
# main()
