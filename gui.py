# -*- coding: utf-8 -*-

###############################################################################
# Copyright (C) 2014 Jorge Zilbermann ealdorj@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import tkinter as tk
from tkinter import filedialog
import generator


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()

        self.name = tk.StringVar()
        self.name.set("Puzzle: ")
        self.status = tk.StringVar()
        self.status.set("Estado: ")
        self.leng = tk.StringVar()
        self.leng.set("Número / Iteración: ")
        self.totaltime = tk.StringVar()
        self.totaltime.set("Tiempo total: ")
        self.ones = tk.StringVar()
        self.ones.set("Número de errores: ")
        self.types = tk.StringVar()
        self.types.set("Progreso: ")
        self.candidates = tk.StringVar()
        self.candidates.set("Finales / Candidatos: ")

        self.complete_name = ""

        (self.instruction_label, self.browse_label, self.browse_button, self.maxnumber_label, self.maxnumber_spinbox,
         self.complex_label, self.complex_spinbox, self.gen_label, self.name_label, self.start_button,
         self.cancel_button, self.status_label, self.leng_label, self.totaltime_label, self.ones_label,
         self.types_label, self.quit_button, self.speed, self.speed_spinbox, self.hasta_spinbox,
         self.hasta_label) = self.create_widgets()

    def test(self):
        texti = 'Hasta el número (1 - ' + self.maxnumber_spinbox.get() + '):'
        self.hasta_label.config(text=texti)
        self.hasta_spinbox.config(from_=1, to_=self.maxnumber_spinbox.get())

    def create_widgets(self):
        # Label instrucción
        instruction_label = tk.Label(self, text="Para generar un nuevo puzzle, selecciona 'Examinar ficheros y eli"
                                                "ge el fichero .csv (b&w) o .json (color).\nElige el número máximo"
                                                ", la complejidad y la velocidad.\nEl fichero resultante 'temp.csv'"
                                                " o 'temp.json' estará en el directorio del generador.")
        instruction_label.grid(padx=10, pady=10, column=0, row=0, columnspan=2)

        # Frame option
        browse_label = tk.LabelFrame(self, text="Opciones de generación", padx=10, pady=10)
        browse_label.grid(sticky=tk.N, padx=10, pady=0, column=0, row=1)
        browse_label.columnconfigure(1, pad=10)
        browse_label.rowconfigure(0, pad=10)
        browse_label.rowconfigure(1, pad=0)
        browse_label.rowconfigure(2, pad=10)
        browse_label.rowconfigure(3, pad=0)
        browse_label.rowconfigure(4, pad=2)
        # Botón examinar
        browse_button = tk.Button(browse_label, text='Examinar ficheros', command=self.popup)
        browse_button.grid(sticky=tk.W+tk.E, padx=0, column=0, row=0, pady=0, columnspan=2)
        # Label maxnumber
        maxnumber_label = tk.Label(browse_label, text="Número máximo (2 - 99):")
        maxnumber_label.grid(sticky=tk.SW, padx=0, column=0, row=1, pady=10)
        # Spinbox maxnumber
        maxnumber_spinbox = tk.Spinbox(browse_label, from_=2, to_=99, wrap=True, width=2, state='readonly', command=self.test)
        maxnumber_spinbox.grid(sticky=tk.SE, padx=0, column=1, row=1, pady=10)
        # Label complejidad
        complex_label = tk.Label(browse_label, text="Iteraciones (1 - 999):")
        complex_label.grid(sticky=tk.NW, padx=0, column=0, row=2, pady=0)
        # Spinbox dificultad
        complex_spinbox = tk.Spinbox(browse_label, from_=1, to_=999, wrap=True, width=3, state='readonly')
        complex_spinbox.grid(sticky=tk.NE, padx=0, column=1, row=2, pady=0)
        # Label velocidad
        speed_label = tk.Label(browse_label, text="Velocidad (1 - 5):")
        speed_label.grid(sticky=tk.NW, padx=0, column=0, row=3, pady=10)
        # Spinbox velocidad
        speed_spinbox = tk.Spinbox(browse_label, from_=1, to_=5, wrap=True, width=1, state='readonly')
        speed_spinbox.grid(sticky=tk.NE, padx=0, column=1, row=3, pady=10)
        # Label hasta
        hasta_label = tk.Label(browse_label, text="Hasta el número (1 - 2):")
        hasta_label.grid(sticky=tk.NW, padx=0, column=0, row=4, pady=0)
        # Spinbox hasta
        hasta_spinbox = tk.Spinbox(browse_label, from_=1, to_=2, wrap=True, width=2, state='readonly')
        hasta_spinbox.grid(sticky=tk.NE, padx=0, column=1, row=4, pady=0)

        # Frame generacion
        gen_label = tk.LabelFrame(self, text="Generación", padx=10, pady=10)
        gen_label.grid(sticky=tk.N, padx=10, pady=0, column=1, row=1)
        gen_label.columnconfigure(1, pad=10)
        gen_label.columnconfigure(0, pad=10)
        gen_label.rowconfigure(1, pad=15)
        # Label puzzlename
        name_label = tk.Label(gen_label, textvariable=self.name, justify=tk.LEFT, width=50)
        name_label.grid(sticky=tk.NW, padx=0, column=0, row=0, columnspan=2)
        # Botón generar
        start_button = tk.Button(gen_label, text='Empezar', command=self.start, state="disabled")
        start_button.grid(sticky=tk.W+tk.E, padx=0, column=0, row=1, pady=0)
        # Botón cancelar
        cancel_button = tk.Button(gen_label, text='Cancelar', command=self.cancel, state="disabled")
        cancel_button.grid(sticky=tk.W+tk.E, padx=0, column=1, row=1, pady=0)
        # Label estado
        status_label = tk.Label(gen_label, textvariable=self.status, justify=tk.LEFT)
        status_label.grid(sticky=tk.NW, padx=0, column=0, row=2, columnspan=2)
        # Label longitud
        leng_label = tk.Label(gen_label, textvariable=self.leng, justify=tk.LEFT)
        leng_label.grid(sticky=tk.NW, padx=0, column=0, row=4, columnspan=2)
        # Label tiempo total
        totaltime_label = tk.Label(gen_label, textvariable=self.totaltime, justify=tk.LEFT)
        totaltime_label.grid(sticky=tk.NW, padx=0, column=0, row=7, columnspan=2)
        # Label numero de unos
        ones_label = tk.Label(gen_label, textvariable=self.ones, justify=tk.LEFT)
        ones_label.grid(sticky=tk.NW, padx=0, column=0, row=5, columnspan=2)
        # Label tipo
        types_label = tk.Label(gen_label, textvariable=self.types, justify=tk.LEFT)
        types_label.grid(sticky=tk.NW, padx=0, column=0, row=3, columnspan=2)
        # Label candidatos
        candidates_label = tk.Label(gen_label, textvariable=self.candidates, justify=tk.LEFT)
        candidates_label.grid(sticky=tk.NW, padx=0, column=0, row=6, columnspan=2)

        # Botón quit
        quit_button = tk.Button(self, text='Salir', command=self.quit, width=10)
        quit_button.grid(sticky=tk.W, padx=10, pady=10)

        return (instruction_label, browse_label, browse_button, maxnumber_label, maxnumber_spinbox, complex_label,
                complex_spinbox, gen_label, name_label, start_button, cancel_button, status_label, leng_label,
                totaltime_label, ones_label, types_label, quit_button, speed_label, speed_spinbox, hasta_spinbox,
                hasta_label)

    def popup(self):
        self.complete_name = filedialog.askopenfilename(initialdir="puzzles", filetypes=[("Bitmap", "*.csv"),
                                                                                         ("Bitmap", "*.json")])
        if self.complete_name != "" and self.complete_name != ():
            self.start_button.config(state='normal')
            self.name.set("Puzzle: " + self.complete_name.rsplit("/")[-1])
            if len(self.name.get()) >= 60:
                self.name.set(self.name.get()[0:59] + "...")

    def start(self):
        self.leng.set("Número / Iteración: ")
        self.totaltime.set("Tiempo total: ")
        self.ones.set("Número de errores: ")
        self.types.set("Progreso: ")
        self.candidates.set("Finales / Candidatos: ")
        self.start_button.config(state='disabled')
        self.browse_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.maxnumber_spinbox.config(state='disabled')
        self.complex_spinbox.config(state='disabled')
        self.speed_spinbox.config(state='disabled')
        self.hasta_spinbox.config(state='disabled')
        self.quit_button.config(state='disabled')
        generator.cancel = self.cancel_button
        generator.candi = self.candidates
        generator.errores = self.ones
        generator.num = self.leng
        generator.types = self.types
        generator.status = self.status
        generator.totaltime = self.totaltime
        g = generator.main(self.complete_name, self.maxnumber_spinbox.get(), self.complex_spinbox.get(),
                           self.speed_spinbox.get(), self.hasta_spinbox.get())
        while g and not generator.cancelar:
            pass
        if generator.cancelar:
            self.status.set("Estado: Cancelado")
            self.leng.set("Número / Iteración: ")
            self.totaltime.set("Tiempo total: ")
            self.ones.set("Número de errores: ")
            self.types.set("Progreso: ")
            self.candidates.set("Finales / Candidatos: ")
            generator.cancelar = False
        else:
            self.status.set("Estado: Completado")
        self.start_button.config(state='normal')
        self.browse_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.maxnumber_spinbox.config(state='normal')
        self.complex_spinbox.config(state='normal')
        self.speed_spinbox.config(state='normal')
        self.hasta_spinbox.config(state='normal')
        self.quit_button.config(state='normal')

    def cancel(self):
        self.status.set("Estado: Cancelando...")
        generator.cancelar = True

app = Application()
app.master.title('Pypbp 1.0')
app.mainloop()
