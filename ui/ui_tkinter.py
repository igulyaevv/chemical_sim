from classes.coordinate_descent import CoordinateDescent
from classes.default_runner import DefaultRunner
from classes.optuna_integration import OptunaIntegration
from resources.utilities import run_time
from resources.constants import Mode, Algorithm, UISize
from interfaces.sleeper import Sleeper

from interfaces.drawer import Drawer

import tkinter as tk
from tkinter import ttk, messagebox, HORIZONTAL, DISABLED, NORMAL, ACTIVE
from tkinter.filedialog import askopenfilename, asksaveasfilename

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ChemicalAppUI(Drawer, Sleeper):  # (tk)
    def __init__(self) -> None:
        self.N = 0
        self.mode = 0
        self.b = 0.0
        self.ts = 0.0
        self.u = 0.0
        self.G = 0
        self.current_G = 0

        self.theory = None
        self.multiplier = 0.0

        self.opti_count = 0

        self._is_drawing = False

        self.window = tk.Tk()
        self.sidebar = tk.Frame(
            self.window,
            width=UISize.SIDEBAR_W.value,
            height=UISize.SIDEBAR_H.value,
            bd=4,
            relief=tk.GROOVE
        )
        self.graphbar = tk.Frame(
            self.window,
            width=UISize.GRAPHBAR_W.value,
            height=UISize.GRAPHBAR_H.value,
            bd=4,
            relief=tk.GROOVE
        )
        self.statbar = tk.Frame(
            self.window,
            width=UISize.STATBAR_W.value,
            height=UISize.STATBAR_H.value,
            bd=4,
            relief=tk.GROOVE
        )
        self.canvas = tk.Canvas(
            self.window,
            width=UISize.CANVAS_W.value,
            height=UISize.CANVAS_H.value,
            bg="#012",
            relief=tk.GROOVE
        )

        self.vcmd = (self.window.register(self.validate), "%P")

        self.graph = None

        self.label_modelling = tk.Label(self.sidebar, text="Режим работы")
        self.combobox_algo = ttk.Combobox(
            self.sidebar,
            values=[Algorithm.DEFAULT.value, Algorithm.DOWNHILL.value, Algorithm.TPE.value]
        )
        self.combobox_algo.bind("<<ComboboxSelected>>", self.change_opti_visible)
        self.label_height = tk.Label(self.sidebar, text="Размер поверхности")
        self.textbox_height = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_mode = tk.Label(self.sidebar, text="Режим моделирования")
        self.combobox_mode = ttk.Combobox(self.sidebar, values=[Mode.CONST.value, Mode.VAR.value])
        self.combobox_mode.bind("<<ComboboxSelected>>", self.change_label_create)
        self.label_create = tk.Label(self.sidebar, text="Вероятность появления")
        self.textbox_create = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_ts = tk.Label(self.sidebar, text="Вероятность перехода")
        self.textbox_ts = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_margin = tk.Label(self.sidebar, text="Вероятность слияния")
        self.textbox_margin = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_count = tk.Label(self.sidebar, text="Количество итераций")
        self.textbox_count = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.label_opti = tk.Label(self.sidebar, text="Количество оптимизаций")
        self.textbox_opti = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.textbox_opti.config(state=DISABLED)
        self.label_multiplier = tk.Label(self.sidebar, text="Начальный шаг")
        self.textbox_multiplier = tk.Entry(self.sidebar, validate="key", validatecommand=self.vcmd)
        self.textbox_multiplier.config(state=DISABLED)
        self.btn_openhist = tk.Button(self.sidebar, text="Histogram", command=self.open_hist)

        self.btb_run = tk.Button(self.sidebar, text="Run", command=self.run_btn)
        self.no_ui = tk.BooleanVar()
        self.no_bar = tk.BooleanVar()
        self.cb_run = tk.Checkbutton(self.sidebar, text="No canvas", variable=self.no_ui)
        self.cb_bar = tk.Checkbutton(self.sidebar, text="No bar", variable=self.no_bar)
        self.btn_pause = tk.Button(self.sidebar, text="Pause", command=self.pause_btn)
        self.btn_restart = tk.Button(self.sidebar, text="Rerun", command=self.restart_btn)
        self.btn_pause.config(state=DISABLED)
        self.btn_restart.config(state=DISABLED)
        self.btn_result = tk.Button(self.sidebar, text="Result", command=self.result_btn)
        self.btn_result.config(state=DISABLED)
        self.btn_openconfig = tk.Button(self.sidebar, text="Открыть конфиг", command=self.open_configfile)
        self.btn_saveconfig = tk.Button(self.sidebar, text="Сохранить конфиг", command=self.save_configfile)

        self.label_sleep = tk.Label(self.sidebar, text="Задержка между итерациями")
        self.scale_sleep = tk.Scale(self.sidebar, from_=0, to=3, orient=HORIZONTAL, resolution=0.1)

        self.stat_1 = tk.Label(self.statbar)
        self.stat_2 = tk.Label(self.statbar)
        self.stat_3 = tk.Label(self.statbar)

        self._method = None
        self._method_status = False
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
                self.fields_clearing()
                self.textbox_height.insert(0, text[0].replace('\n', ''))
                self.combobox_mode.insert(0, Mode.VAR.value if text[1].replace('\n', '') == '1' else Mode.CONST.value)
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
            for item in [self.N, self.mode, self.b, self.ts, self.u, self.current_G]:
                output_file.write(str(item) + '\n')
        self.window.title(f"Chemical Simulator - {filepath}")

    def open_hist(self) -> None:
        filepath = askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r") as input_file:
            text = input_file.readline()
            try:
                points = text.replace(' ', '').split(',')
                self.theory = {}
                for point in points:
                    item = point.split(':')
                    self.theory[float(item[0])] = float(item[1])
            except:
                return

    @staticmethod
    def validate(new_value) -> bool:
        try:
            if new_value == '' or new_value == '-' or new_value == '+':
                return True
            _str = str(float(new_value))
            return True
        except:
            return False

    def set_params(self) -> None:
        if self.combobox_algo.get() == '' and self.combobox_algo["state"] == NORMAL or \
                self.textbox_height["state"] == NORMAL and self.textbox_height.get() == '' or \
                self.combobox_mode["state"] == NORMAL and self.combobox_mode.get() == '' or \
                self.textbox_create["state"] == NORMAL and self.textbox_create.get() == '' or \
                self.textbox_ts["state"] == NORMAL and self.textbox_ts.get() == '' or \
                self.textbox_margin["state"] == NORMAL and self.textbox_margin.get() == '' or \
                self.textbox_count["state"] == NORMAL and self.textbox_count.get() == '' or \
                self.textbox_opti["state"] == NORMAL and self.textbox_opti.get() == '' or \
                self.textbox_multiplier["state"] == NORMAL and self.textbox_multiplier.get() == '' or \
                self.combobox_algo.get() in [Algorithm.TPE, Algorithm.DOWNHILL] and self.theory is None:
            messagebox.showinfo("Warning", "Заполнены не все поля")
            self.is_exit = True
            return
        self.is_exit = False
        self.N = int(self.textbox_height.get())
        self.mode = 1 if self.combobox_mode.get() == Mode.VAR.value else 0
        self.b = float(self.textbox_create.get()) if self.textbox_create["state"] == NORMAL else 0.0
        self.ts = float(self.textbox_ts.get()) if self.textbox_ts["state"] == NORMAL else 0.0
        self.u = float(self.textbox_margin.get()) if self.textbox_margin["state"] == NORMAL else 0.0
        self.current_G = int(self.textbox_count.get()) if self.textbox_count["state"] == NORMAL else 0
        if self.G == 0 or self.G is None:
            self.G = self.current_G

        self.opti_count = int(self.textbox_opti.get()) if self.textbox_opti["state"] == NORMAL else 1
        self.multiplier = float(self.textbox_multiplier.get()) if self.textbox_multiplier["state"] == NORMAL else 0.0

    def configurate(self) -> None:
        self.window.config(width=UISize.WIN_W.value, height=UISize.WIN_H.value)
        self.window.resizable(False, False)
        self.window.title("Chemical Simulator")
        self.sidebar.place(x=0, y=0)
        self.graphbar.place(x=UISize.SIDEBAR_W.value, y=0)
        self.statbar.place(x=UISize.SIDEBAR_W.value, y=UISize.STATBAR_H.value)
        self.canvas.place(x=UISize.SIDEBAR_W.value + UISize.GRAPHBAR_W.value, y=0)

        self.label_modelling.place(x=12, y=0)
        self.combobox_algo.place(x=12, y=25)

        self.label_height.place(x=10, y=50)
        self.textbox_height.place(x=12, y=75)
        self.label_mode.place(x=10, y=100)
        self.combobox_mode.place(x=12, y=125)
        self.label_create.place(x=10, y=150)
        self.textbox_create.place(x=12, y=175)
        self.label_ts.place(x=10, y=200)
        self.textbox_ts.place(x=12, y=225)
        self.label_margin.place(x=10, y=250)
        self.textbox_margin.place(x=12, y=275)
        self.label_count.place(x=10, y=300)
        self.textbox_count.place(x=12, y=325)
        self.label_opti.place(x=10, y=350)
        self.textbox_opti.place(x=12, y=375)
        self.label_multiplier.place(x=10, y=400)
        self.textbox_multiplier.place(x=12, y=425)

        self.btb_run.place(x=12, y=455, width=int(UISize.SIDEBAR_W.value / 3))
        self.cb_run.place(x=int(UISize.SIDEBAR_W.value / 3) + 20, y=455, width=int(UISize.SIDEBAR_W.value / 2))
        self.cb_bar.place(x=int(UISize.SIDEBAR_W.value / 3) + 20, y=480, width=int(UISize.SIDEBAR_W.value / 2.5))
        self.btn_openhist.place(x=int(UISize.SIDEBAR_W.value / 3) + 30, y=505, width=int(UISize.SIDEBAR_W.value / 3))
        self.btn_pause.place(x=12, y=480, width=int(UISize.SIDEBAR_W.value / 3))
        self.btn_restart.place(x=12, y=505, width=int(UISize.SIDEBAR_W.value / 3))
        self.btn_result.place(x=12, y=530, width=int(UISize.SIDEBAR_W.value / 3))
        self.btn_openconfig.place(x=12, y=570)
        self.btn_saveconfig.place(x=12, y=595)

        self.label_sleep.place(x=12, y=640)
        self.scale_sleep.place(x=12, y=660)

        self.stat_1.place(x=10, y=10)
        self.stat_2.place(x=10, y=60)
        self.stat_3.place(x=10, y=110)

    def run_btn(self) -> None:
        self.set_params()

        if self.is_exit:
            return

        if not self._method:
            if self.combobox_algo.get() == Algorithm.DOWNHILL.value:
                self._method = CoordinateDescent(
                    rows=self.N,
                    addprob=self.b,
                    transitprob=self.ts,
                    mergeprob=self.u,
                    drawer=self,
                    sleeper=self,
                    multiplier=self.multiplier,
                    theory=self.theory
                )
            elif self.combobox_algo.get() == Algorithm.TPE.value:
                self._method = OptunaIntegration(
                    rows=self.N,
                    drawer=self,
                    sleeper=self,
                    theory=self.theory
                )
            else:
                self._method = DefaultRunner(
                    rows=self.N,
                    addprob=self.b,
                    transitprob=self.ts,
                    mergeprob=self.u,
                    drawer=self,
                    sleeper=self,
                    steps=self.G,
                    theory=self.theory
                )

            self.textbox_height.config(state=DISABLED)
            self.combobox_mode.config(state=DISABLED)
            self.textbox_create.config(state=DISABLED)
            self.textbox_ts.config(state=DISABLED)
            self.textbox_margin.config(state=DISABLED)
        else:
            if self.combobox_algo.get() in [Algorithm.TPE.value, Algorithm.DOWNHILL.value]:
                self.opti_count = int(self.textbox_opti.get()) if self.textbox_opti and self.textbox_opti != '' else 0
            else:
                self.current_G = int(self.textbox_count.get()) if self.textbox_count and self.textbox_count != '' else 0
                self._method.change_steps(self.current_G)

        self.textbox_multiplier.config(state=DISABLED)
        self.textbox_opti.config(state=DISABLED)
        self.textbox_count.config(state=DISABLED)
        self.combobox_algo.config(state=DISABLED)
        self.btb_run.config(state=DISABLED)
        self.btn_pause.config(state=ACTIVE)
        self.btn_restart.config(state=DISABLED)
        self.btn_result.config(state=ACTIVE)

        # TODO: добавить или убрать следующие два коммента, добавить - убрать функционал паузы,
        #  убрать - решить проблему с плохими попытками оптимизации из-за их приостановки
        if self.combobox_algo.get() in [Algorithm.TPE.value, Algorithm.DOWNHILL.value]:
            self.btn_pause.config(state=DISABLED)

        self.run()

        if not self.is_exit:
            self.pause_btn()

    def sleep(self):
        self.window.after(int(self.scale_sleep.get() * 1000))

    def prepare_draw(self):
        if not self.no_ui.get() or self._is_drawing:
            self.canvas.delete("all")
            self._is_drawing &= False

    def draw_point(self, row: int, col: int, color_idx: int) -> None:
        if not self.no_ui.get():
            self._is_drawing |= True
            diff = self.canvas.winfo_height() / self._method.rows
            colors = ["#ffffff", "#e32636", "#00ffff", "#ffe135", "#1dacd6"]
            self.canvas.create_oval(col * diff, row * diff, col * diff + diff, row * diff + diff,
                                    fill=colors[0] if color_idx == 0 else colors[color_idx % len(colors)])

    def complete_draw(self):
        self.window.update()
        self.sleep()

    def draw_bar(self, bar: dict) -> None:
        if not self.no_bar.get():
            if self.graph:
                self.graph.get_tk_widget().destroy()

            fig = Figure(figsize=((UISize.GRAPHBAR_W.value - 10) / 100, (UISize.GRAPHBAR_H.value - 10) / 100), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_xlabel("Weight", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.bar(bar.keys(), bar.values(), width=.5, color='g')

            self.graph = FigureCanvasTkAgg(fig, self.graphbar)
            self.graph.draw()
            self.graph.get_tk_widget().place(x=0, y=0)

    def draw_stat(self) -> None:
        # stat = self._method.stats()
        self.stat_1.config(text=f"Вероятность появления: {0.85822}")
        self.stat_2.config(text=f"Вероятность перехода: {0.20146}")
        self.stat_3.config(text=f"Вероятность слияния: {0.73576}")

    @run_time
    def run(self) -> None:
        while self.opti_count > 0:
            self._method_status = True
            self._method.optimize()
            self._method_status = False
            if self.is_exit:
                break
            self.draw_stat()
            self.opti_count -= 1

    def pause_btn(self) -> None:
        self.is_exit = True
        # TODO: сделать ожидание завершения моделирования
        self.btn_pause.config(state=DISABLED)
        self.btn_restart.config(state=ACTIVE)
        self.btb_run.config(state=ACTIVE)
        if self.combobox_algo.get() == Algorithm.DEFAULT.value:
            self.textbox_count.config(state=NORMAL)
            self.textbox_count.delete(0, 'end')
            self.textbox_count.insert(0, str(self._method.current_steps))
        else:
            self.textbox_opti.config(state=NORMAL)
            self.textbox_opti.delete(0, 'end')
            self.textbox_opti.insert(0, str(self.opti_count))

    def result_btn(self) -> None:
        if self._method:
            self._method.result()

    def fields_clearing(self):
        self.textbox_height.delete(0, 'end')
        self.combobox_mode.delete(0, 'end')
        self.textbox_create.delete(0, 'end')
        self.textbox_ts.delete(0, 'end')
        self.textbox_margin.delete(0, 'end')
        self.textbox_count.delete(0, 'end')
        self.textbox_opti.delete(0, 'end')

    def restart_btn(self):
        if self._method:
            self._method = None
            self.G = 0

        self.theory = None

        self.textbox_height.config(state=NORMAL)
        self.combobox_mode.config(state=NORMAL)
        self.textbox_create.config(state=NORMAL)
        self.textbox_ts.config(state=NORMAL)
        self.textbox_margin.config(state=NORMAL)
        self.combobox_algo.config(state=NORMAL)
        self.textbox_count.config(state=NORMAL)

        self.btn_result.config(state=DISABLED)
        self.btn_restart.config(state=DISABLED)

        if self.graph:
            self.graph.get_tk_widget().destroy()

        self.stat_1.config(text='')
        self.stat_2.config(text='')
        self.stat_3.config(text='')

        self.canvas.delete("all")

    def change_label_create(self, _) -> None:
        if self.combobox_mode.get() == Mode.CONST.value:
            self.label_create.config(text="Вероятность появления")
        else:
            self.label_create.config(text="Правая граница вероятности")

    def change_opti_visible(self, _) -> None:
        if self.combobox_algo.get() != Algorithm.DOWNHILL.value and self.combobox_algo.get() != Algorithm.TPE.value:
            self.textbox_opti.delete(0, 'end')
            self.textbox_opti.config(state=DISABLED)
        else:
            self.textbox_opti.config(state=NORMAL)
            self.textbox_count.config(state=DISABLED)

        if self.combobox_algo.get() != Algorithm.DOWNHILL.value:
            self.textbox_multiplier.delete(0, 'end')
            self.textbox_multiplier.config(state=DISABLED)
        else:
            self.textbox_multiplier.config(state=NORMAL)

        if self.combobox_algo.get() == Algorithm.TPE:
            self.textbox_create.delete(0, 'end')
            self.textbox_create.config(state=DISABLED)
            self.textbox_ts.delete(0, 'end')
            self.textbox_ts.config(state=DISABLED)
            self.textbox_margin.delete(0, 'end')
            self.textbox_margin.config(state=DISABLED)
        else:
            self.textbox_create.config(state=NORMAL)
            self.textbox_ts.config(state=NORMAL)
            self.textbox_margin.config(state=NORMAL)

    def start(self) -> None:
        self.configurate()
        self.window.mainloop()
