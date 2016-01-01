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

import sys
import os
import random
import math
import json
from ete3 import Tree
try:
    import timing
except ImportError:
    pass

maxf = []
maxe = None


class Position:
    """ Clase posicion.

    Attributes:
        coordinate (tuple): tupla con las coordenadas de la Posicion.
        color (list): color del numero.
        way (list): lista de conexiones.
        number (int): numero del cuadrado.
        adjacents (list): lista de Posiciones adyacentes.
        ini (bool): indica si es el inicio del camino.
        pair (Position): Posicion pareja.

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

    def __repr__(self):
        return "%s[%s]%s" % (repr(self.coordinate), self.number, self.color)

    def clear(self):
        """Resetea una posicion.

        """
        self.number = 1
        self.ini = False
        self.way = []
        self.pair = self

    def euclides(self, pos):
        """

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
        print('='*40)


class Generator:
    """Clase generador.

    Attributes:
        puzzle (Puzzle): Puzzle sobre el que generar el puzzle.
        temporal_way (list): Lista temporal para guardar el camino.
        max_number (int): Numero maximo que tendra el Puzzle.

    """
    def __init__(self, puzzle, max_number):
        """Clase para generar el puzzle a partir de un Puzzle.

        Args:
            puzzle (Puzzle): Puzzle sobre el que generar el puzzle.
            max_number (int): Numero maximo que tendra el Puzzle.

        """
        self.puzzle = puzzle
        self.temporal_way = []
        self.max_number = max_number

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
        while True:
            if ran_adjacent_position.number == 1 and ran_adjacent_position.color == candidate_position.color:
                break
            elif len(candidate_position.adjacents) != 0:
                ran_adjacent_position = candidate_position.adjacents.pop(
                    candidate_position.adjacents.index(random.choice(candidate_position.adjacents)))
                test.append(ran_adjacent_position)
            else:
                break
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


class Checker:
    """Clase para comprobar la validez del puzzle. Condiciones:

    Attributes:
        puzzle (Puzzle): Puzzle sobre el que comprobar la validez.
        t (TreeNode): arbol para generar caminos a partir de un nodo.
        taux (TreeNode): arbol auxiliar para la comprobacion de la validez de un camino.
        number (int): numero a comprobar.

    """
    def __init__(self, puzzle, checkn):
        """Clase para generar el puzzle a partir de un Puzzle.

        Args:
            puzzle (Puzzle): Puzzle sobre el que comprobar la validez.
            checkn (int): numero a comprobar.

        """
        self.puzzle = puzzle
        self.t = Tree(';', format=1)
        self.taux = Tree(';', format=1)
        self.number = checkn
        self.finish = False
        self.casee = 0

    def three_check(self, father, rama, root):
        """Posibles casos:
            (a) 3   0   3  	  (b) 3---*     (c) 8---*   *---*---*---8     (d) 2---2   2
                |       |             |             |   |                             |
                *   0   *         0   3         1   *---*   *---*   1         2   0   2
                |       |                                   |   |             |
                3   0   3                       7---*---*---*   7   1         2   2---2

        Caso A: Si usando ceros suyos o ceros de otro (de la misma longitud) o ceros sin nada, es posible llegar a un
        numero igual que el suyo sin ser su pareja Y desde la pareja del nuevo es posible llegar a la pareja del
        primero usando ceros suyos o ceros de otros (de la misma longitud) o ceros sin nada.
        Caso B: Si usando ceros sin nada, es posible llegar a la misma pareja.
        Caso C: Si usando ceros suyos o ceros de otro (siempre del mismo) o ceros sin nada, es posible llegar al menos
        2 veces a su pareja Y el otro usando ceros del suyo, ceros del primero o ceros es posible llegar al menos
        dos veces a su pareja.
        Caso D: Si es posible formar un camino cerrado usando parejas.
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
        if self.finish:
            return
        elif father.number == self.number and dist == self.number:
            aux = [a.name for a in rama.iter_ancestors() if type(a.name) is Position]
            aux.append(father)
            if father is not root.pair and father.pair.euclides(root.pair) <= root.number - 1 and\
               father.color == root.color:
                casea = sum((a.number == 0 and (len(a.way) == 0 or len(a.way) == self.number)) and
                            a.color == root.color for a in aux)
                if casea == self.number - 2:
                    self.case_a_aux(father.pair, self.taux.add_child(name=father.pair), root)
                    self.taux = Tree(';', format=1)
            elif father is root.pair:
                only = sum(a in root.way for a in aux)
                caseb = sum((a.number == 0 and (len(a.way) == 0 or (len(a.way) == self.number and
                                                                    a.color == root.color))) for a in aux)
                casec = None
                if self.number > 3:
                    for a in aux:
                        if len(a.way) != self.number and len(a.way) > 3:
                            casec = a
                            break
                if casec is not None:
                    for a in aux:
                        if not (a in root.way or a in casec.way or (a.number == 0 and len(a.way) == 0) and
                                a.color == casec.color):
                            casec = None
                            break
                if only == self.number:
                    self.casee += 1
                    if self.casee > 1:
                        for w in root.way:
                            w.clear()
                            self.puzzle.candidate.append(w)
                        self.finish = True
                        # print('error E encontrado', root)
                elif caseb == self.number - 2:
                    # print('error B encontrado:', root)
                    for w in root.way:
                        w.clear()
                        self.puzzle.candidate.append(w)
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
                if father.euclides(root.pair) <= root.number - dist and adj.color == root.color:
                    if (dist < self.number - 1 and ((adj.number == 0 and len(adj.way) == 0) or
                                                    (adj.number == 0 and len(adj.way) == self.number)))\
                            or (dist == self.number - 1 and adj.number == self.number):
                        aux = [a.name for a in rama.iter_ancestors()]
                        if adj not in aux:  # para que no vuelva sobre si mismo.
                            self.case_a_aux(adj, rama.add_child(name=adj), root)
        if self.finish:
            rama.detach()
            return
        elif father.number == self.number and dist == self.number and father is root.pair:
            # print('error A encontrado:', root)
            for w in root.way:
                w.clear()
                self.puzzle.candidate.append(w)
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
            if father.euclides(ncasec.pair) <= ncasec.number - dist and adj.color == ncasec.color:
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
            # print('error C encontrado:', root)
            if ncasec.number > root.number:
                for w in root.way:
                    w.clear()
                    self.puzzle.candidate.append(w)
            else:
                for w in ncasec.way:
                    w.clear()
                    self.puzzle.candidate.append(w)
            self.finish = True
        rama.detach()


def generate(puzz, gen):
    """Genera el puzzle.

    Args:
        puzz (Puzzle): Puzzle a comprobar.
        gen (Generator): Generador a usar.

    """
    print('generando puzzle')
    while len(puzz.candidate) > 0:  # generamos el puzzle mientras haya candidatos.
        candidate = gen.step_one()
        adjacent, candidate = gen.step_two(candidate)
        while adjacent:
            puzz.candidate.remove(adjacent)
            if len(gen.temporal_way) < gen.max_number:
                adjacent, candidate = gen.step_two(adjacent)
            else:
                break
        gen.temporal_way[0].ini = True
        for pos in gen.temporal_way:
            if pos is gen.temporal_way[0]:
                pos.pair = gen.temporal_way[-1]
                pos.number = len(gen.temporal_way)
            elif pos is gen.temporal_way[-1]:
                pos.pair = gen.temporal_way[0]
                pos.number = len(gen.temporal_way)
            else:
                pos.number = 0
            pos.way = gen.temporal_way.copy()
            puzz.final.append(pos)
        gen.temporal_way.clear()
    for pos1 in puzz.final:  # reseteamos los menores que el numero generado ya que no hace falta ver sus errores.
        if pos1.number < gen.max_number and pos1 not in p.candidate and pos1.number != 1 and gen.max_number > len(
                pos1.way) > 0:
            for w in pos1.way:
                if w is not pos1:
                    w.clear()
            pos1.clear()


def check(puzz, chec):
    """Mira si el puzzle esta bien generado o no.

    Args:
        puzz (Puzzle): Puzzle a comprobar.
        chec (Checker): Comprobador a usar.

    """
    aux = 0
    for pos1 in puzz.final:
        aux += 1
        print('progreso:', aux, 'de', len(puzz.final), ' '*40, end='\r')
        if pos1.number == chec.number and pos1.ini:
            # print('generando arbol')
            chec.three_check(pos1, chec.t.add_child(name=pos1), pos1)
            chec.casee = 0
            chec.t = Tree(';', format=1)
            chec.finish = False


def found_error(i):
    """Funcion para reconstruir la lista de candidatos a partir de los errores.

        Args:
            i (int): numero analizado.

    """
    auxf = p.final  # salvar final.
    print('\nnumero de errores:', int(len(p.candidate)/i))
    for pos1 in p.final:  # volver a construir la lista de candidatos.
        # aquellos 1's que tengan 1's adyacentes.
        if pos1.number == 1 and pos1 not in p.candidate:
            for pos_ad in pos1.adjacents:
                if pos_ad.number == 1 and pos_ad.color == pos1.color:
                    p.candidate.append(pos1)
                    break
        # aquellos que sean menores que el numero chequeado.
        elif pos1.number < i and pos1 not in p.candidate and pos1.number != 1 and i > len(pos1.way) > 0:
            for w in pos1.way:
                if w is not pos1:
                    w.clear()
                    p.candidate.append(w)
            pos1.clear()
            p.candidate.append(pos1)
    [p.final.remove(pos1) for pos1 in p.candidate if pos1 in p.final]
    global maxe, maxf  # salvar longitud y ver si no es menor que el anterior. Si es menor restaurar final.
    if maxe is None or maxe >= len(p.candidate):
        maxe = len(p.candidate)
        maxf = auxf
    elif maxe < len(p.candidate):
        p.final = auxf
    print('finales: ', len(maxf), ' / ', 'candidatos: ', maxe)
    print('='*40)


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
        num = f.readline().strip().split(',')
        for posy in range(0, ncolumns):
            number = int(num.pop(0).split(',')[0])
            position_list.append(Position(posy, posx, [0, 0, 0], number))  # columna, fila.
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

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr('Not enough params.')
        sys.exit(1)
    if sys.argv[1].rsplit('/')[-1].rsplit('.')[1] == 'csv':
        p = read_csv(os.path.abspath(os.path.dirname(sys.argv[1]))+'/'+sys.argv[1].rsplit('/')[-1])
    else:
        p = read_json(os.path.abspath(os.path.dirname(sys.argv[1]))+'/'+sys.argv[1].rsplit('/')[-1])
    p.initialice()  # inicializamos las listas candidata y final y los adyacentes.
    it2 = itm = int(sys.argv[2])  # numero maximo.
    it1 = it = int(sys.argv[3])  # numero de iteraciones por numero.
    while it2 > 1:
        while it > 0:
            print('numero:', it2, '- iteracion:', it1 + 1 - it, 'de', it1)
            g = Generator(p, it2)  # creamos el generador.
            generate(p, g)  # generamos el puzzle.
            if it2 == 2:
                print('buscando errores del numero:', it2)
                c = Checker(p, it2)  # creamos el comprobador.
                check(p, c)  # comprobamos.
            else:
                for it3 in range(it2, itm + 1):  # errores por cada uno de los numeros entre el maximo y el generado.
                    print('buscando errores del numero:', it3)
                    c = Checker(p, it3)
                    check(p, c)
            found_error(it2)
            if len(p.candidate) == 0:
                it2 = 0
                break
            it -= 1
        it = it1
        it2 -= 1
    p.final += p.candidate
    if sys.argv[1].rsplit('/')[-1].rsplit('.')[1] == 'csv':
        write_csv(p)
    else:
        write_json(p)
