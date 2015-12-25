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
from ete3 import Tree
import timing


class Position:
    """ Clase posicion.

    Attributes:
        coordinate (tuple): tupla con las coordenadas de la Posicion.
        color (tuple): color del numero.
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
            color (tuple): color del numero.
            number (int): numero del cuadrado.

        """
        self.coordinate = (posy, posx)
        self.color = color
        self.way = []
        self.number = number
        self.adjacents = []
        self.ini = False
        self.pair = None

    def __repr__(self):
        return "%s[%s]" % (repr(self.coordinate), self.number)


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
        print('inicializando puzzle')
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
                    if pos_ad.number == 1:
                        self.candidate.append(pos1)
                        self.final.remove(pos1)
                        break
            else:
                self.final.append(pos1)


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
        while ran_adjacent_position.number != 1:
            if len(candidate_position.adjacents) != 0:
                ran_adjacent_position = candidate_position.adjacents.pop(
                    candidate_position.adjacents.index(random.choice(candidate_position.adjacents)))
                test.append(ran_adjacent_position)
            else:
                break
        candidate_position.adjacents = candidate_position.adjacents + test
        if candidate_position not in self.temporal_way:
            self.temporal_way.append(candidate_position)
        if ran_adjacent_position.number != 1 or ran_adjacent_position in self.puzzle.final:  # no hay camino posible.
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

    def three_check(self, father, rama, root):
        """Posibles casos:
            (a) 3   0   3  	  (b) 3---*     (c) 8---*   *---*---*---8     (d) 2---2   2
                |       |             |             |   |                             |
                *   0   *         0   3         1   *---*   *---*   1         2   0   2
                |       |                                   |   |             |
                3   0   3                       7---*---*---*   7   1         2   2---2

        Args:
            father (Position): posicion actual.
            rama (TreeNode): rama actual.
            root (Position): posicion desde la que se comienza a generar el arbol auxiliar.

        Se podria mejorar la velocidad viendo si desde la hoja donde estemos es posible llegar a algun self.number (que
        no sea el mismo) del puzzle restandole la distancia que llevamos ya.

        """
        if self.finish:
            return

        dist = self.t.get_distance(self.t.get_tree_root(), rama)
        for adj in father.adjacents:
            if self.number == 2:  # para el numero 2.
                if dist != self.number:
                    self.three_check(adj, rama.add_child(name=adj), root)
            else:  # para el resto de numeros mayores que 2.
                if (dist < self.number - 1 and ((adj.number == 0 and len(adj.way) == 0) or
                                                (adj.number == 0 and len(adj.way) == self.number))) or\
                        (dist == self.number - 1 and adj.number == self.number):
                    aux = []
                    for a in rama.get_ancestors():
                        aux.append(a.name)
                    if adj not in aux:  # para que no vuelva sobre si mismo.
                        self.three_check(adj, rama.add_child(name=adj), root)

        if dist == self.number and father.number == self.number and father is not root.pair and\
                abs(int(round(math.sqrt((father.pair.coordinate[0] - root.pair.coordinate[0])**2 +
                                        (father.pair.coordinate[1] - root.pair.coordinate[1])**2)))) <= root.number:
            print('generando arbol auxiliar')
            self.three_check_aux(father.pair, self.taux.add_child(name=father.pair), root)
            print('generado arbol auxiliar')
            self.taux = Tree(';', format=1)
        elif dist == self.number and father.number == self.number and father is root.pair:
            if len(self.t.get_leaves_by_name(root.pair)) >= 2:
                print('error B encontrado')
                for w in root.way:
                    w.number = 1
                    w.ini = False
                    w.way = []
                    self.puzzle.candidate.append(w)
                self.finish = True

    def three_check_aux(self, father, rama, root):
        """Construccion de arbol auxiliar para el caso (a).

        Args:
            father (Position): posicion actual.
            rama (TreeNode): rama actual.
            root (Position): posicion desde la que se comienza a generar el arbol auxiliar.

        """
        if self.finish:
            return

        dist = self.taux.get_distance(self.taux.get_tree_root(), rama)
        for adj in father.adjacents:
            if self.number == 2:  # para el numero 2.
                if dist != self.number:
                    self.three_check_aux(adj, rama.add_child(name=adj), root)
            else:  # para el resto de numeros mayores que 2.
                if abs(int(round(math.sqrt((adj.coordinate[0] - root.pair.coordinate[0]) ** 2 +
                                           (adj.coordinate[1] - root.pair.coordinate[1]) ** 2)))) <= root.number - dist:
                    if (dist < self.number - 1 and ((adj.number == 0 and len(adj.way) == 0) or
                                                    (adj.number == 0 and len(adj.way) == self.number)))\
                            or (dist == self.number - 1 and adj.number == self.number):
                        aux = []
                        for a in rama.get_ancestors():
                            aux.append(a.name)
                        if adj not in aux:  # para que no vuelva sobre si mismo.
                            self.three_check_aux(adj, rama.add_child(name=adj), root)

        if dist == self.number and father.number == self.number and father is root.pair:  # (a).
            print('error A encontrado')
            for w in root.way:
                w.number = 1
                w.ini = False
                w.way = []
                self.puzzle.candidate.append(w)
            self.finish = True


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
    for posx in range(0, int(nrows)):  # creamos Posiciones y las añadimos la la lista de posiciones iniciales
        num = f.readline().strip().split(',')
        for posy in range(0, int(ncolumns)):
            number = int(num.pop(0).split(',')[0])
            position_list.append(Position(posy, posx, (0, 0, 0), number))  # columna, fila.
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


def check(puzz, chec):
    """Mira si el puzzle esta bien generado o no.

    Args:
        puzz (Puzzle): Puzzle a comprobar.
        chec (Checker): Comprobador a usar.

    """
    for pos1 in puzz.final:
        if pos1.number == chec.number and pos1.ini:
            print('generando arbol')
            chec.three_check(pos1, chec.t.add_child(name=pos1), pos1)
            chec.t = Tree(';', format=1)
            chec.finish = False


def found_error(i):
    """Funcion para reconstruir la lista de candidatos a partir de los errores.

        Args:
            i (int): numero analizado.

    """
    print('numero de errores:', len(p.candidate))
    for pos1 in p.final:  # volver a construir la lista de candidatos.
        if pos1.number == 1 and pos1 not in p.candidate:
            for pos_ad in pos1.adjacents:
                if pos_ad.number == 1:
                    p.candidate.append(pos1)
                    p.final.remove(pos1)
                    break
        elif pos1.number < i and len(pos1.way) < i:
            for w in pos1.way:
                w.number = 1
                w.ini = False
                w.way = []
                p.candidate.append(w)
                p.final.remove(w)
    [p.final.remove(pos1) for pos1 in p.candidate if pos1 in p.final]
    print('finales: ', len(p.final), ' / ', 'candidatos: ', len(p.candidate))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr('Not enough params.')
        sys.exit(1)

    p = read_csv(os.path.abspath(os.path.dirname(sys.argv[1]))+'/'+sys.argv[1].rsplit('/')[-1])
    p.initialice()  # inicializamos las listas candidata y final y los adyacentes.
    it2 = itm = int(sys.argv[2])  # numero maximo.
    it1 = it = int(sys.argv[3])  # numero de iteraciones por numero.
    while it2 > 1:
        while it > 0:
            print('numero: ', it2, ' / iteracion: ', it)
            g = Generator(p, it2)  # creamos el generador.
            generate(p, g)  # generamos el puzzle.
            for it3 in range(it2, itm + 1):  # buscar errores por cada uno de los numeros entre el maximo y el generado.
                print('buscando errores del numero: ', it3)
                c = Checker(p, it3)  # creamos el comprobador.
                check(p, c)  # comprobamos.
            found_error(it2)
            it -= 1
        it = it1
        it2 -= 1
    p.final += p.candidate
    write_csv(p)
