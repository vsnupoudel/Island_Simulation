# -*- coding: utf-8 -*-
"""File has the cycle class and annual cycle methods in it"""

__author__ = "Anders Huse, Bishnu Poudel"
__email__ = "anhuse@nmbu.no; bipo@nmbu.no"

import numpy as np


class Cycle:
    """
    This class contains the componentes of the annual cycle on Rossumaøya. The
    componentes follows a fixed order:

    1. Food grows on the island
    2. Animals feed
    3. Animals procreate
    4. Animals migrate
    5. Animals die
    6. Animals age and lose weight

    """
    def __init__(self, object_matrix):
        """
        :param object_matrix: list, 2D list of cell objects containing
                               herbivores and carnivores
        """
        self.object_matrix = object_matrix

    def food_grows(self):
        """
        Updates/increases the amount of food available in Jungle and Savannah
        objects.
        """
        for row_of_obj in self.object_matrix:
            for obj in row_of_obj:
                if type(obj).__name__ == "Savannah":
                    # print('food grow in Savannah')
                    obj.f_ij += obj.parameters['alpha'] *\
                                (obj.parameters['f_max'] - obj.f_ij)
                elif type(obj).__name__ == "Jungle":
                    obj.f_ij = obj.parameters['f_max']

    def animals_eat(self):
        """
        Herbivores and Carnivores eat. This happens once in every cycle.

        This method updates:

        - Increases the weight of animal if they eat
        - Decreases the food in Savannah and Jungle if animals eat in that
          particular cell
        """

        for row_of_obj in self.object_matrix:
            for cell in row_of_obj:
                if type(cell).__name__ in ["Savannah", "Jungle"]:
                    for herb in cell.herb_sorted_rev:
                        herb.herb_eat(cell)

                # Carnivores in the cell eat after herbivores
                if type(cell).__name__ in ["Savannah", "Jungle", "Desert"]:
                    for carn in cell.carn_sorted_rev:
                        carn.carn_eat(cell)

    def animals_reproduce(self):
        """
        Animals reproduce in every cell on the island.
        Animals reproduce if they meet the conditions (for each cell).

        This method updates:

        - The number of animals in the particular cell
        - The weight of the parents

        This method creates:

        - New animal objects in the cell
        -----------------------------------------------------
        Rules for procreation:

        - Probability for procreation = min (1, gamma × F × (N − 1))
        """

        for row_of_obj in self.object_matrix:
            for cell in row_of_obj:
                if type(cell).__name__ in ["Desert", "Savannah", "Jungle"]:
                    new_herbs = []
                    for animal in cell.herb_list:
                        new = animal.herb_reproduce(cell.n_herbs)
                        if new:
                            new_herbs.append(new)

                    for herb in new_herbs:
                        cell.animal_object_list.append(herb)

                    # For carnivore reproduction
                    new_carns = []
                    for animal in cell.carn_list:
                        new = animal.carn_reproduce(cell.n_carns)
                        if new:
                            new_carns.append(new)

                    for carn in new_carns:
                        cell.animal_object_list.append(carn)

    def get_adjacent_migratable_cells(self, row, column):
        """
        This method calculates the position of the adjacent migratable cells
        to the current cell (with position (row, column)). Ocean and Mountain
        cells are not migratable

        :param row:            int, row index
        :param column:         int, column index
        :return: list_of_adj   list, list of adjacent cells
        """

        list_of_adj = []
        for i in (-1, 1):
            try:
                _t = self.object_matrix[row][column+i]
            except IndexError:
                pass
            else:
                if type(_t).__name__ in ["Desert", "Savannah", "Jungle"]:
                    list_of_adj.append(_t)
            try:
                _t = self.object_matrix[row+i][column]
            except IndexError:
                pass
            else:
                if type(_t).__name__ in ["Desert", "Savannah", "Jungle"]:
                    list_of_adj.append(_t)
        return list_of_adj

    def animals_migrate(self):
        """
        Animals migrate

        :param self: the map object with all the cells and all the animals

        This method accomplishes the following:

        - Delete migrated animals from current cell
        - Add incoming animals to the new cell

        :return: None
        """
        for row_of_obj in self.object_matrix:
            for cell in row_of_obj:
                for animal in cell.animal_object_list:
                    animal.has_migrated = False

        for row, row_of_obj in enumerate(self.object_matrix):
            for col, cell in enumerate(row_of_obj):
                animals_moved_away = []
                if type(cell).__name__ in ["Desert", "Savannah", "Jungle"]:
                    adj_cells = self.get_adjacent_migratable_cells(row, col)
                    # Propensity calculation for each adjacent cell
                    propen_list_h = []
                    for _c in adj_cells:
                        propen_list_h.append(_c.pi_ij_herb)

                    propen_list_c = []
                    for _c in adj_cells:
                        propen_list_c.append(_c.pi_ij_carn)

                    # propability calculation for each adjacent cell
                    proba_list_h = np.array(propen_list_h
                                            ) / np.sum(propen_list_h)
                    proba_list_c = np.array(propen_list_c
                                            ) / np.sum(propen_list_c)

                    # Animal migrates only if it passes probability

                    for animal in cell.animal_object_list:
                        rand_num = np.random.random()
                        if (rand_num <= animal.move_prob) & \
                                (not animal.has_migrated):
                            if type(animal).__name__ == "Herbivore":
                                animal.herb_migrates(animal, adj_cells,
                                                     proba_list_h)

                            if type(animal).__name__ == "Carnivore":
                                # print('Carn migrates called')
                                animal.carn_migrates(animal, adj_cells,
                                                     proba_list_c)

                            animal.has_migrated = True
                            animals_moved_away.append(animal)

                cell.animal_object_list = [animal for animal in
                                           cell.animal_object_list if
                                           animal not in animals_moved_away]

    def animals_die(self):
        """
        This method makes animals die.

        Animals die:

        - With certainty if the animals fitness is equal to zero
        - with probability
                           omega*(1 - fitness)
          otherwise

        :return: None
        """
        death_list = []
        for row, row_of_obj in enumerate(self.object_matrix):
            for col, cell in enumerate(row_of_obj):
                if type(cell).__name__ in ["Desert", "Savannah", "Jungle"]:
                    for animal in cell.animal_object_list:
                        if animal.fitness == 0:
                            death_list.append(animal)
                        else:
                            rand_num = np.random.random()
                            if rand_num < animal.death_prob:
                                death_list.append(animal)

                cell.animal_object_list = [animal for animal in
                                           cell.animal_object_list if
                                           animal not in death_list]

    def animals_age(self):
        """
        Increases the age of every animal at the end of the cycle
        Decreases the weight of animal by eta*weight of animal"""
        for list_of_obj in self.object_matrix:
            for cell in list_of_obj:
                for animal in cell.animal_object_list:
                    animal.animals_age()
