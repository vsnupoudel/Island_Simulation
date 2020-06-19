# -*- coding: utf-8 -*-
"""File has the Cell class and its subclasses, type of terrain"""

__author__ = 'Anders Huse, Bishnu Poudel'
__email__ = 'anhuse@nmbu.no; bipo@nmbu.no'

from .animal import Herbivore, Carnivore
import numpy as np
import math


class Cell:
    """
    Super class for the type of Terrain: Jungle, Savannah, Desert,
    Ocean or Mountain.

    :var row:      int, row index of the position of the cell
    :var column:   int, column index of the position of the cell
                            has procreated or not
    :var f_ij:     float(default=0), food avilable in each cell
    :ivar animal_object_list:   list, list of animal objects
    :ivar tot_herb_weight:      float, total weigth of all herbivores in a cell
    :ivar rel_ab_carn:          float, relative abundance of fodder for
                                carnivores
    :ivar rel_ab_herb:          float, relative abundance of fodder for
                                herbivores

    """

    def __init__(self, row, column, f_ij=0):
        """

        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        :param f_ij:   float(default=0), food avilable in each cell
        """
        self.row = row
        self.column = column
        self.animal_object_list = []
        self.f_ij = f_ij

        self.tot_herb_weight = np.sum([a.weight for a in self.herb_list])
        self.rel_ab_carn = self.tot_herb_weight / (self.n_carns + 1)\
            * Carnivore.animal_params['F']
        self.rel_ab_herb = self.f_ij / (self.n_herbs + 1) *\
            Herbivore.animal_params['F']

    @property
    def pi_ij_carn(self):
        """propensity for a cell object for carnivores"""
        return math.e ** (Carnivore.animal_params['lambda'] * self.rel_ab_carn)

    @property
    def pi_ij_herb(self):
        """propensity for a cell object for herbivores"""
        return math.e ** (Herbivore.animal_params['lambda'] * self.rel_ab_herb)

    def set_population(self, input_dict):
        """
        Sets the population of a cell object

        :param input_dict: dict, dictionary specifying the population to be
                           set for the cell object, containing:

        location of cell object, type of animals, age and weight of animals
        """
        for animal in input_dict['pop']:
            if animal['species'] == "Herbivore":
                self.animal_object_list.append(Herbivore(age=animal[
                    'age'], weight=animal['weight']))
            else:
                self.animal_object_list.append(Carnivore(age=animal[
                    'age'], weight=animal['weight']))

    def get_population(self):
        """
        Gets the population of the cell

        :return: animal_object_list
        """
        return self.animal_object_list

    @property
    def herb_list(self):
        """List of all herbivore objects in the cell object"""
        return [a for a in self.animal_object_list
                if type(a).__name__ == "Herbivore"]

    @property
    def herb_sorted(self):
        """Sorted list of all herbivore objects in the cell object"""
        return sorted(self.herb_list, key=lambda animal: animal.fitness)

    @property
    def herb_sorted_rev(self):
        """Reversed-sorted list of all herbivore objects in the cell object"""
        return sorted(self.herb_list, key=lambda animal: animal.fitness,
                      reverse=True)

    @property
    def carn_list(self):
        """List of all carnivore objects in the cell object"""
        return [a for a in self.animal_object_list
                if type(a).__name__ == "Carnivore"]

    @property
    def carn_sorted_rev(self):
        """Sorted list of all carnivore objects in the cell object"""
        return sorted(self.carn_list, key=lambda animal: animal.fitness,
                      reverse=True)

    @property
    def n_herbs(self):
        """Number of herbivore objects in the cell object"""
        return len(self.herb_list)

    @property
    def n_carns(self):
        """Number of carnivore objects in the cell object"""
        return len(self.carn_list)


class Jungle(Cell):
    """
    Jungle landscape. Child class of the Cell class.

    :cvar parameters:   dict, dictionary of Jungle parameters, containing:
                        f_max: int, maximal available food in Jungle object
                        alpha: (default, None), parameter
    :cvar is_migratable:  bool(default, True), whether the cell is migratable
                          or not for animal objects

    :ivar row:      int, row index of the position of the cell
    :ivar column:   int, column index of the position of the cell
    :ivar f_ij:     float(default=300), food avilable in each cel

    """

    is_migratable = True
    parameters = {'f_max': 800, 'alpha': None}

    def __init__(
            self,
            row,
            column,
            f_ij=300
    ):
        """
        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        :param f_ij:   float(default=300), food avilable in each cell
        """
        super().__init__(row, column)
        self.f_ij = f_ij

    @classmethod
    def update_par(cls, params_dict):
        """
        Updates the landscape parameters

        :param cls: class method
        :param params_dict: Dictionary of parameters to be updated
        """
        for k, v in params_dict.items():
            if k not in cls.parameters:
                raise ValueError(k, ' is an invalid Key')
            if v <= 0:
                raise ValueError(k, v, ' Param value must be positive')

        # print(params_dict)
        cls.parameters.update(params_dict)


class Savannah(Cell):
    """
    Savannah landscape. Child class of the Cell class.

    :cvar parameters:   dict, dictionary of Savannah parameters, containing:
                        f_max: int(default, 300), maximal available food in
                        Savannah object

                        alpha: (default, 0.3), parameter
    :cvar is_migratable:  bool(default, True), whether the cell is migratable
                          or not for animal objects
    :ivar row:      int, row index of the position of the cell
    :ivar column:   int, column index of the position of the cell
    :ivar f_ij:     float(default=200), food avilable in each cel

    """

    is_migratable = True
    parameters = {'f_max': 300, 'alpha': 0.3}

    def __init__(
            self,
            row,
            column,
            f_ij=200
    ):
        """
        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        :param f_ij:   float(default=200), food avilable in each cell
        """

        super().__init__(row, column)
        self.f_ij = f_ij

    @classmethod
    def update_par(cls, params_dict):
        """
        Updates the landscape parameters

        :param cls: class method
        :param params_dict: dict, Dictionary of parameters to be updated
        """
        for k, v in params_dict.items():
            if k not in cls.parameters:
                raise ValueError(k, ' is an invalid Key')
            if v <= 0:
                raise ValueError(k, v, ' Param value must be positive')
        cls.parameters.update(params_dict)


class Desert(Cell):
    """
    Desert landscape. Child class of the Cell class.

    :cvar is_migratable:  bool(default, True), whether the cell is migratable
                          or not for animal objects
    :ivar row:      int, row index of the position of the cell
    :ivar column:   int, column index of the position of the cell

    """
    is_migratable = True

    def __init__(
            self,
            row,
            column
    ):
        """

        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        """
        super().__init__(row, column)


class Ocean(Cell):
    """Ocean landscape. Child class of the Cell class.

    :cvar is_migratable:  bool(default, False), whether the cell is migratable
                          or not for animal objects
    :ivar row:      int, row index of the position of the cell
    :ivar column:   int, column index of the position of the cell

    """

    is_migratable = False

    def __init__(self, row, column):
        """

        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        """
        super().__init__(row, column)


class Mountain(Cell):
    """Mountian landscape.  Child class of the Cell class.

    :cvar is_migratable:  bool(default, False), whether the cell is migratable
                          or not for animal objects
    :ivar row:      int, row index of the position of the cell
    :ivar column:   int, column index of the position of the cell

    """
    is_migratable = False

    def __init__(self, row, column):
        """

        :param row:    int, row index of the position of the cell
        :param column: int, column index of the position of the cell
        """
        super().__init__(row, column)
