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
import argparse
import shutil
import sys
import os
import random
import time
import math
import json
import multiprocessing as mp
from ete3 import Tree
from timeit import default_timer as timer
from datetime import timedelta

start = timer()


class Position:
    """Clase posicion.

    Attributes:
        coordinate (tuple): tupla con las coordenadas de la Posicion.
        color (list): color del numero.
        way (list): lista de conexiones.
        number (int): numero del cuadrado.
        adjacents (list): lista de Posiciones adyacentes.
        ini (bool): indica si es el inicio del camino.
        pair (Position): Posicion pareja.
        new (bool): indica si ha sido generado nuevamente.

    """
    def __init__(self, posy, posx, color, number):
        """Clase que describe un cuadrado del puzzle.

        Args:
            posy (int): posicion columna del cuadrado.
            posx (int): posicion file del cuadrado.
            color (list): color del numero.
            number (int): numero del cuadrado.

        """
        self.coordinate = (posy, posx)
        self.color = color
        self.way = []
        self.number = number
        self.adjacents = []
        self.ini = False
        self.pair = self
        self.new = True

    def __repr__(self):
        return "%s[%s]%s" % (repr(self.coordinate), self.number, self.color)

    def clear(self):
        """Resetea una posicion.

        """
        self.number = 1
        self.ini = False
        self.way = []
        self.pair = self
        self.new = True

    def euclides(self, pos):
        """Calcula la distancia euclidea de dos posiciones en un puzzle.

        Args:
            pos (Position): posicion destino.

        Returns:
            Distancia entre las dos posiciones.

        """
        return abs(int(round(math.sqrt((self.coordinate[0] - pos.coordinate[0]) ** 2 +
                                       (self.coordinate[1] - pos.coordinate[1]) ** 2))))


class Puzzle:
    """Clase puzzle

    Attributes:
        size (tuple); tamaño del puzzle.
        initial (list): lista de Posiciones iniciales del Puzzle.
        candidate (list): lista de Posiciones candidatas del Puzzle.
        final (list): lista de Posiciones finales del Puzzle.

    """

    def __init__(self, size, initial):
        """Clase que describe un puzzle formado por Posiciones.

        Args:
            size (tuple); tamaño del puzzle.
            initial (list): lista de Posiciones iniciales leida del csv.

        """
        self.size = size
        self.initial = initial
        self.candidate = []
        self.final = []

    def initialice(self):
        """ Inicializa las lista de posiciones finales con los 1's que no tengan 1's adyacentes (en cruz) e
        inicializa la lista de posiciones candidatas con el resto.

        """
        print('inicializando puzzle', end='\r')
        for pos1 in self.initial:
            for pos2 in self.initial:  # añadimos las Posiciones adyacentes a las Posiciones del Puzzle.
                if pos2.coordinate in [(pos1.coordinate[0] + 1, pos1.coordinate[1]),
                                       (pos1.coordinate[0] - 1, pos1.coordinate[1]),
                                       (pos1.coordinate[0], pos1.coordinate[1] + 1),
                                       (pos1.coordinate[0], pos1.coordinate[1] - 1)]:
                    pos1.adjacents.append(pos2)
            if pos1.number == 1:
                for pos_ad in pos1.adjacents:
                    if pos1 not in self.final:
                        self.final.append(pos1)
                    if pos_ad.number == 1 and pos_ad.color == pos1.color:
                        self.candidate.append(pos1)
                        self.final.remove(pos1)
                        break
            else:
                self.final.append(pos1)
        print('inicializando puzzle ( candidatos', len(self.candidate), ')')
        mid = timer()
        print('='*40, seconds_to_str(mid - start))

    def show_stats(self):
        """Devuelve las estadisticas de numeros en el puzzle.

        Returns:
            Diccionario con las estadisticas del puzzle final.

        """
        stats = {}
        for pos in self.final:
            if str(pos.number) in stats:
                stats[str(pos.number)] = stats.get(str(pos.number)) + 1
            else:
                stats[str(pos.number)] = 1
        return stats


class Generator:
    """Clase generador.

    Attributes:
        puzzle (Puzzle): Puzzle sobre el que generar el puzzle.
        temporal_way (list): Lista temporal para guardar el camino.
        max_number (int): Numero maximo que tendra el Puzzle.
        speed (int): Nivel de velocidad (0:muy lento; 1:lento; 2:normal; 3:rapido; 4:muy rapido).

    """
    def __init__(self, puzzle, max_number, speed=0, nspeed=2):
        """Clase para generar el puzzle a partir de un Puzzle.

        Args:
            puzzle (Puzzle): Puzzle sobre el que generar el puzzle.
            max_number (int): Numero maximo que tendra el Puzzle.
            speed (int): Nivel de velocidad (0:muy lento; 1:lento; 2:normal; 3:rapido; 4:muy rapido).
            nspeed (int): Numero hasta el que se le aplicara la velocidad (speed).

        """
        self.puzzle = puzzle
        self.temporal_way = []
        self.max_number = max_number
        self.nspeed = nspeed
        self.speed = speed
        self.sspeed = ''
        self.set_speed()

    def set_speed(self):
        """Pone la velocidad de la generación del Puzzle.

        """
        ws = ['muy lenta', 'lenta', 'normal', 'rapida', 'muy rapida']
        if self.max_number <= self.nspeed:
            self.speed = self.max_number
            self.sspeed = ws[0]
        elif self.sspeed == '':
            self.sspeed = ws[self.speed-1]
            if self.speed == 1:
                self.speed = self.max_number
            elif self.speed == 2:
                self.speed = self.max_number - (self.max_number / 3)
            elif self.speed == 3:
                self.speed = self.max_number / 2
            elif self.speed == 4:
                self.speed = self.max_number / 3
            elif self.speed == 5:
                self.speed = 0

    def step_one(self):
        """Elegir posición aleatoria de la tabla de candidatos y eliminarlo de ella.

        Returns:
            Posicion aleatoria de la lista de candidatos.

        """
        return self.puzzle.candidate.pop(self.puzzle.candidate.index(random.choice(self.puzzle.candidate)))

    def step_two(self, candidate_position):
        """Elegir Posicion adyacente a la pasada de la lista de candidatos sin camino definido y con numero 1.

        Args:
            candidate_position (Position): Posicion pasada para crear camino.

        Returns:
            Booleano indicando si hay camino posible o la nueva posicion y el candidato sobre el que se hizo el camino.

        """
        ran_adjacent_position = candidate_position.adjacents.pop(
            candidate_position.adjacents.index(random.choice(candidate_position.adjacents)))
        test = [ran_adjacent_position]
        while not (ran_adjacent_position.number == 1 and ran_adjacent_position.color == candidate_position.color
                   ) and len(candidate_position.adjacents) != 0:
            ran_adjacent_position = candidate_position.adjacents.pop(candidate_position.adjacents.index(
                random.choice(candidate_position.adjacents)))
            test.append(ran_adjacent_position)
        candidate_position.adjacents = candidate_position.adjacents + test
        if candidate_position not in self.temporal_way:
            self.temporal_way.append(candidate_position)
        if ran_adjacent_position.number != 1 or ran_adjacent_position.color != candidate_position.color or\
           ran_adjacent_position in self.puzzle.final:  # no hay camino posible.
            return False, candidate_position
        else:  # hay camino posible.
            self.temporal_way.append(ran_adjacent_position)
            candidate_position.number += 1
            ran_adjacent_position.number += 1
            return ran_adjacent_position, candidate_position

    def generate(self):
        """Genera el puzzle.

        """
        self.set_speed()
        print('generando puzzle ( velocidad', self.sspeed, ')')
        while len(self.puzzle.candidate) > 0:  # generamos el puzzle mientras haya candidatos.
            candidate = self.step_one()
            adjacent, candidate = self.step_two(candidate)
            while adjacent:
                self.puzzle.candidate.remove(adjacent)
                if len(self.temporal_way) < self.max_number:
                    adjacent, candidate = self.step_two(adjacent)
                else:
                    break
            self.temporal_way[0].ini = True
            for pos in self.temporal_way:
                if pos is self.temporal_way[0]:
                    pos.pair = self.temporal_way[-1]
                    pos.number = len(self.temporal_way)
                elif pos is self.temporal_way[-1]:
                    pos.pair = self.temporal_way[0]
                    pos.number = len(self.temporal_way)
                else:
                    pos.number = 0
                pos.way = self.temporal_way.copy()
                self.puzzle.final.append(pos)
            self.temporal_way.clear()
        for pos1 in self.puzzle.final:  # reseteamos los menores que el numero generado.
            if pos1.number < self.max_number and pos1 not in self.puzzle.candidate and pos1.number != 1 and\
                                    self.max_number > len(pos1.way) > 0:
                for w in pos1.way:
                    w.clear()
            elif pos1.number == self.max_number:  # opciones de velocidad.
                for pa in self.puzzle.final:
                    if pa.euclides(pos1) <= self.max_number - self.speed and pa is not pos1 and pa is not pos1.pair and\
                                    pa.number == pos1.number and pa.color == pos1.color:
                        for w in pa.way:
                            w.clear()


class Checker:
    """Clase para comprobar la validez del puzzle.

    Attributes:
        puzzle (Puzzle): Puzzle sobre el que comprobar la validez.
        t (TreeNode): arbol para generar caminos a partir de un nodo.
        taux (TreeNode): arbol auxiliar para la comprobacion de la validez de un camino.
        number (int): numero a comprobar.

    """
    def __init__(self, puzzle, cores):
        """Clase para generar el puzzle a partir de un Puzzle.

        Args:
            puzzle (Puzzle): Puzzle sobre el que comprobar la validez.
            cores (int): number of cores to use.

        """
        self.puzzle = puzzle
        self.cores = cores
        self.t = Tree(';', format=1)
        self.taux = Tree(';', format=1)
        self.number = 0
        self.finish = False
        self.casee = 0
        self.maxf = []
        self.maxe = None
        self.q = None

    def run(self, pos1, q):
        self.q = q
        self.three_check(pos1, self.t.add_child(name=pos1), pos1)

    def three_check(self, father, rama, root):
        """Posibles casos:
            (a) 3   0   3  	  (b) 3---*     (c) 8---*   *---*---*---8     (d) 2---2   2
                |       |             |             |   |                             |
                *   0   *         0   3         1   *---*   *---*   1         2   0   2
                |       |                                   |   |             |
                3   0   3                       7---*---*---*   7   1         2   2---2

        Caso A: Si usando ceros de la misma longitud y color o ceros sin nada, es posible llegar a un numero igual que
        el suyo y del mismo color sin ser su pareja Y desde la pareja del nuevo es posible llegar a la pareja del
        primero usando ceros de la misma longitud y color o ceros sin nada.
        Caso B: Si usando ceros sin nada o ceros suyos, es posible llegar a la misma pareja. Descartar su propio camino.
        Caso C: Si usando ceros suyos o ceros de otro (siempre del mismo) o ceros sin nada, es posible llegar a su
        pareja Y el otro usando ceros del suyo, ceros del primero o ceros sin nada es posible llegar a a su pareja.
        Caso D: Si es posible formar un camino cerrado usando parejas. Descartar su propio camino.
        Caso E: Si usando ceros suyos es posible llegar a su pareja al menos dos veces.

        Args:
            father (Position): posicion actual.
            rama (TreeNode): rama actual.
            root (Position): posicion desde la que se comienza a generar el arbol auxiliar.

        """
        dist = self.t.get_distance(self.t.get_tree_root(), rama)
        for adj in father.adjacents:
            if self.number == 2:
                if dist != self.number and root.color == adj.color:
                    self.three_check(adj, rama.add_child(name=adj), root)
            else:
                aux2 = False
                for test in self.puzzle.final:  # para mejorar la velocidad.
                    if test is not root and test.number == self.number and test.euclides(father) <= root.number - dist:
                        aux2 = True
                        break
                if aux2:
                    if (self.number > 3 and (dist < self.number - 1 and adj.number == 0) or (
                                    dist == self.number - 1 and adj.number == self.number)) or\
                       (self.number <= 3 and (dist < self.number - 1 and
                                              ((adj.number == 0 and len(adj.way) == 0) or
                                               (adj.number == 0 and len(adj.way) == self.number))) or
                       (dist == self.number - 1 and adj.number == self.number)):
                        aux = [a.name for a in rama.iter_ancestors()]
                        if adj not in aux:  # para que no vuelva sobre si mismo.
                            self.three_check(adj, rama.add_child(name=adj), root)
        if self.t.__len__() > 1:
            print(self.t.__len__())
        if self.finish:
            rama.detach()
            return
        elif father.number == self.number and dist == self.number:
            aux = [a.name for a in rama.iter_ancestors() if type(a.name) is Position]
            aux.append(father)
            if father is not root.pair and father.pair.euclides(root.pair) <= root.number - 1 and\
               father.color == root.color:
                casea = sum((a.number == 0 and (len(a.way) == 0 or (len(a.way) == self.number and
                                                                    a.color == root.color))) for a in aux)
                if casea == self.number - 2:
                    self.case_a_aux(father.pair, self.taux.add_child(name=father.pair), root)
                    self.taux = Tree(';', format=1)
            elif father is root.pair:
                only = sum(a in root.way for a in aux)
                caseb = sum((a.number == 0 and (len(a.way) == 0 or a in root.way)) for a in aux)
                casec = None
                if self.number > 3:
                    for a in aux:
                        if len(a.way) != self.number and len(a.way) > 3:
                            casec = a
                            break
                if casec is not None:
                    for a in aux:
                        if not (a in root.way or a in casec.way or (a.number == 0 and len(a.way) == 0)):
                            casec = None
                            break
                if only == self.number:
                    self.casee += 1
                    if self.casee > 1:
                        # print('error E encontrado', root)
                        self.q.put(self.puzzle.final.index(root))
                        self.finish = True
                elif caseb == self.number - 2:
                    # print('error B encontrado:', root)
                    self.q.put(self.puzzle.final.index(root))
                    self.finish = True
                elif casec is not None:
                    ncaseci = [elem for elem in casec.way if elem.number != 0 and elem.ini][0]
                    self.case_c_aux(ncaseci, self.taux.add_child(name=ncaseci), root, ncaseci)
                    self.taux = Tree(';', format=1)
        rama.detach()

    def case_a_aux(self, father, rama, root):
        """Construccion de arbol auxiliar para el caso A.

        Args:
            father (Position): posicion actual.
            rama (TreeNode): rama actual.
            root (Position): posicion desde la que se comienza a generar el arbol auxiliar.

        """
        dist = self.taux.get_distance(self.taux.get_tree_root(), rama)
        for adj in father.adjacents:
            if self.number == 2 and root.color == adj.color:
                if dist != self.number:
                    self.case_a_aux(adj, rama.add_child(name=adj), root)
            else:
                if father.euclides(root.pair) <= root.number - dist:
                    if (dist < self.number - 1 and ((adj.number == 0 and len(adj.way) == 0) or
                                                    (adj.number == 0 and len(adj.way) == self.number)))\
                            or (dist == self.number - 1 and adj.number == self.number):
                        aux = [a.name for a in rama.iter_ancestors()]
                        if adj not in aux:  # para que no vuelva sobre si mismo.
                            self.case_a_aux(adj, rama.add_child(name=adj), root)
        if self.finish:
            rama.detach()
            return
        elif father.number == self.number and dist == self.number and \
                father is root.pair and father.color == root.color:
            # print('error A encontrado:', root)
            self.q.put(self.puzzle.final.index(root))
            self.finish = True
        rama.detach()

    def case_c_aux(self, father, rama, root, ncasec):
        """Construccion de arbol auxiliar para el caso A.

        Args:
            father (Position): posicion actual.
            rama (TreeNode): rama actual.
            root (Position): posicion desde la que se comienza a generar el arbol auxiliar.
            ncasec (Position): posicion del caso c (auxiliar).

        """
        dist = self.taux.get_distance(self.taux.get_tree_root(), rama)
        for adj in father.adjacents:
            if father.euclides(ncasec.pair) <= ncasec.number - dist:
                if (dist < ncasec.number - 1 and ((adj.number == 0 and len(adj.way) == 0) or
                                                  (adj.number == 0 and adj in root.way) or
                                                  (adj.number == 0 and adj in ncasec.way)))\
                        or (dist == ncasec.number - 1 and adj.number == ncasec.number):
                    aux = [a.name for a in rama.iter_ancestors()]
                    if adj not in aux:  # para que no vuelva sobre si mismo.
                        self.case_c_aux(adj, rama.add_child(name=adj), root, ncasec)
        if self.finish:
            rama.detach()
            return
        elif dist == ncasec.number and father is ncasec.pair:
            aux = [a.name for a in rama.iter_ancestors() if type(a.name) is Position]
            only = sum(a in ncasec.way for a in aux)
            if not only == ncasec.number:
                # print('error C encontrado:', root)
                if ncasec.number > root.number:
                    self.q.put(self.puzzle.final.index(root))
                else:
                    self.q.put(self.puzzle.final.index(ncasec))
                self.finish = True
        rama.detach()

    def check(self):
        """Mira si el puzzle esta bien generado o no.

        """
        q = mp.Queue()
        aux = 0
        processes = []
        launched = []
        for pos1 in self.puzzle.final:
            if pos1.number == self.number and pos1.ini and pos1.new:
                processes.append(mp.Process(target=self.run, args=(pos1, q, )))
        long = len(processes)
        while len(processes) > 0:
            alive = 0
            for p in launched:
                if p.is_alive():
                    alive += 1
                else:
                    launched.remove(p)
            if (alive != self.cores - 1 or self.cores == 1) and len(processes) > 0:
                aux += 1
                print('progreso:', aux, 'de', long, ' '*40, end='\r')
                uno = processes.pop()
                launched.append(uno)
                uno.start()
            time.sleep(0.1)  # sleep
        while len(launched) > 0:
            for p in launched:
                if not p.is_alive():
                    launched.remove(p)
            print('progreso:', aux, 'de', long, '( procesos activos', len(launched),  ')', ' '*40, end='\r')
            time.sleep(0.1)  # sleep
        while not q.empty():
            test = q.get()
            for w in self.puzzle.final[test].way:
                w.clear()
                self.puzzle.candidate.append(w)
        self.found_error()

    def found_error(self):
        """Funcion para reconstruir la lista de candidatos a partir de los errores.

        """
        auxf = self.puzzle.final  # salvar final.
        print('\nnumero de errores:', int(len(self.puzzle.candidate)/self.number))
        for pos1 in self.puzzle.final:  # volver a construir la lista de candidatos.
            # aquellos 1's que tengan 1's adyacentes.
            if pos1.number == 1 and pos1 not in self.puzzle.candidate:
                for pos_ad in pos1.adjacents:
                    if pos_ad.number == 1 and pos_ad.color == pos1.color:
                        self.puzzle.candidate.append(pos1)
                        break
            # aquellos que sean menores que el numero chequeado.
            elif pos1.number < self.number and pos1 not in self.puzzle.candidate and pos1.number != 1 and (
                            self.number > len(pos1.way) > 0):
                for w in pos1.way:
                    if w is not pos1:
                        w.clear()
                        self.puzzle.candidate.append(w)
                pos1.clear()
                self.puzzle.candidate.append(pos1)
        [self.puzzle.final.remove(pos1) for pos1 in self.puzzle.candidate if pos1 in self.puzzle.final]
        # salvar longitud y ver si no es menor que el anterior. Si es menor restaurar final.
        if self.maxe is None or self.maxe >= len(self.puzzle.candidate):
            self.maxe = len(self.puzzle.candidate)
            self.maxf = auxf
        elif self.maxe < len(self.puzzle.candidate):
            self.puzzle.final = auxf
        print('finales: ', len(self.maxf), ' / ', 'candidatos: ', self.maxe)
        mid = timer()
        print('='*40, seconds_to_str(mid - start))


def read_csv(fname):
    """Lee el archivo csv pasado y construye una lista con su contenido.

    Args:
        fname (str): archivo para ser leido.

    Returns:
        Una lista con el contenido del archivo.

    Raises:
        IOError: si no puede encontrar el archivo.

    """
    try:
        f = open(fname, 'r')
    except IOError:
        print("File not found", fname)
        sys.exit()
    ncolumns = len(f.readline().strip().split(','))  # numero de columnas.
    f.seek(0)
    nrows = 0
    for _ in f.readlines():  # numero de filas.
        nrows += 1
    f.seek(0)
    position_list = []
    for posx in range(0, nrows):  # creamos Posiciones y las añadimos la la lista de posiciones iniciales
        numi = f.readline().strip().split(',')
        for posy in range(0, ncolumns):
            number = int(numi.pop(0).split(',')[0])
            if number >= 1:
                position_list.append(Position(posy, posx, [0, 0, 0], number))  # columna, fila.
            else:
                position_list.append(Position(posy, posx, [255, 255, 255], number))  # columna, fila.
    return Puzzle((nrows, ncolumns), position_list)  # creamos el Puzzle.


def write_csv(puzzle):
    """Escribe la tabla pasada de un Puzzle en un archivo csv. Primero debe ordenar la lista por sus coordenadas,

    Args:
        puzzle (Puzzle): Puzzle a escribir.

    """
    file = open("temp.csv", 'w')
    ncolumn = 0
    for pos1 in sorted(puzzle.final, key=lambda position: (position.coordinate[1], position.coordinate[0])):
        file.write(str(pos1.number))
        ncolumn += 1
        if ncolumn == puzzle.size[1]:
            file.write('\n')
            ncolumn = 0
        else:
            file.write(',')


def read_json(fname):
    """Lee el archivo json pasado y construye una lista con su contenido.

    Args:
        fname (str): archivo para ser leido.

    Returns:
        Una lista con el contenido del archivo.

    Raises:
        IOError: si no puede encontrar el archivo.

    """
    try:
        f = open(fname, 'r')
    except IOError:
        print("File not found")
        sys.exit()
    ncolumns = 0
    data = json.load(f)
    for row in range(len(data)):
        for col in range(len(data[row])):
            ncolumns += 1
        break
    nrows = len(data)
    position_list = []
    for posx in range(0, nrows):
        for posy in range(0, ncolumns):
            position_list.append(Position(posy, posx, data[posx][posy]['color'], data[posx][posy]['number']))
    return Puzzle((nrows, ncolumns), position_list)


def write_json(puzzle):
    """Escribe la tabla pasada de un Puzzle en un archivo json. Primero debe ordenar la lista por sus coordenadas,

    Args:
        puzzle (Puzzle): Puzzle a escribir.

    """
    file = open("temp.json", 'w')
    ncolumn = 0
    row = []
    col = []
    for pos1 in sorted(puzzle.final, key=lambda position: (position.coordinate[1], position.coordinate[0])):
        color = pos1.color
        col.append({'color': {'r': color[0], 'b': color[1], 'g': color[2]}, 'number': pos1.number})
        ncolumn += 1
        if ncolumn == puzzle.size[1]:
            row.append(col)
            col = []
            ncolumn = 0
    json.dump(row, file)


def seconds_to_str(t):
    return str(timedelta(seconds=t))


def main(arg1, arg2, arg3, arg4, arg5, arg6):
    global start
    if arg1.rsplit('/')[-1].rsplit('.')[1] == 'csv':
        p = read_csv(os.path.abspath(os.path.dirname(arg1))+'/'+arg1.rsplit('/')[-1])
    else:
        p = read_json(os.path.abspath(os.path.dirname(arg1))+'/'+arg1.rsplit('/')[-1])
    p.initialice()  # inicializamos las listas candidata y final y los adyacentes.
    it2 = int(arg2)  # numero maximo.
    it1 = it = int(arg3)  # numero de iteraciones por numero.
    g = Generator(p, it2, int(arg4), int(arg5))  # creamos el generador.
    c = Checker(p, arg6)
    while it2 > 1:
        while it > 0:
            print('numero:', it2, '- iteracion:', it1 + 1 - it, 'de', it1)
            g.max_number = it2
            g.generate()  # generamos el puzzle.
            print('buscando errores')
            c.number = it2
            c.check()
            for neu in p.final:
                neu.new = False
            if len(p.candidate) == 0:
                it2 = 0
                break
            it -= 1
        it = it1
        it2 -= 1
    p.final += p.candidate
    print('stats:', p.show_stats())
    if arg1.rsplit('/')[-1].rsplit('.')[1] == 'csv':
        write_csv(p)
    else:
        write_json(p)
    end = timer()
    print('='*40, seconds_to_str(end - start))
    start = timer()

if __name__ == '__main__':
    os.environ['COLUMNS'] = str(shutil.get_terminal_size().columns)  # para que el ancho de la consola lo pille bien.
    parser = argparse.ArgumentParser(description='Generate puzzles for pypbp game.')
    parser.add_argument('--cores', action='store', type=int, metavar='cores', default=1,
                        help='number of cores to use (default: 1)')
    parser.add_argument('file', action='store', type=str, metavar='file',
                        help='CSV or JSON file from which to generate the puzzle')
    parser.add_argument('max_number', action='store', type=int, metavar='max_number', default=2, nargs='?',
                        help='maximun number to be present in the generated puzzle (default: 2)')
    parser.add_argument('iterations', action='store', type=int, metavar='iterations', default=1, nargs='?',
                        help='number of iterations per number (default: 1)')
    parser.add_argument('speed', action='store', type=int, metavar='speed', choices=range(1, 6), default=3, nargs='?',
                        help='speed used to generate the puzzle (1:slowest; 2:slow; 3:normal; 4:fast; 5:fastest) '
                             '(default: 3)')
    parser.add_argument('speed_number', action='store', type=int, metavar='speed_number', default=2, nargs='?',
                        help='number till argument speed is applied (default: 2)')
    args = parser.parse_args()  # (interface=True, iterations=1, max_number=2, speed=1, speed_number=2)
    main(vars(args).get('file'), vars(args).get('max_number'), vars(args).get('iterations'),
         vars(args).get('speed'), vars(args).get('speed_number'), vars(args).get('cores'))
