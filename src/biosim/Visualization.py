# -*- coding: utf-8 -*-

__author__ = "Anders Huse, Bishnu Poudel"
__email__ = "anhuse@nmbu.no; bipo@nmbu.no"

import numpy as np
import subprocess
import os
import matplotlib.pyplot as plt

# update these variables to point to your ffmpeg and convert binaries
_FFMPEG_BINARY = 'ffmpeg'
_CONVERT_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_MOVIE_FORMAT = 'mp4'   # alternatives: mp4, gif

class Visualization:
    """
    Plotting island map, heatmaps of herbivore and carnivore distribution
    and line graph of herbivore and carnivore count.

        Attributes:

        object_matrix:                 array, 2D array of cell objects
                                              containing herbivores and
                                              carnivores
        img_dir(default, None):        image directory
        img_name:                      str, image name
        img_fmt(default, png):         str, image fmt

        _fig(default, None):           plt.figure, figure to put subplots in
        _map_ax(default, None):        plot of the island map
        _img_axis(default, None):      axis to _map_ax
        _herb_ax(default, None):       heatmap, plot for herbivore distribution
        _carn_ax(default, None):       heatmap, plot for carnivore distribution
        _mean_ax(default, None):       plot for the linegraphs
        _herb_line(default, None):     herbivore-count line in _mean_ax
        _carn_line(default, None):     carnivore-count line in _mean_ax
        _herb_axis(default, None):     axis to _herb_ax
        _carn_axis(default, None):     axis to _carn_ax

    """

#    def show(self):
#        plt.show()

    def __init__(self, object_matrix, img_dir=None,
                 img_name=_DEFAULT_GRAPHICS_NAME,
                 img_fmt='png'):
        """
        :param object_matrix:   array, 2D array of cell objects containing
                                       herbivores and carnivores
        :param img_dir(default, None):    image directory
        :param img_name:                  str, image name
        :param img_fmt(default, png):     str, image fmt
        """
        self.object_matrix = object_matrix
        self._step = 0
        self._final_step = 200
        self._img_ctr = 0

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None
        self._img_fmt = img_fmt

        # the following will be initialized by _setup_graphics
        self._fig = None
        self._map_ax = None
        self._img_axis = None
        self._mean_ax = None
        self._herb_line = None
        self._carn_line = None
        self._herb_ax = None
        self._carn_ax = None
        self._herb_axis = None
        self._carn_axis = None


    def _set_graphics(self, y_lim, x_lim):
        """
        Sets up the graphics with 4 subplots
        :param y_lim:       float, y limit of plot
        :param x_lim:       int, x limit of plot
        :return: None
        """

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(8,8))

        if self._map_ax is None:
            self._map_ax = self._fig.add_subplot(2, 2, 1)
            self._img_axis = None

        if self._herb_ax is None:
            self._herb_ax = self._fig.add_subplot(2, 2, 2)
            self._herb_axis = None

        if self._carn_ax is None:
            self._carn_ax = self._fig.add_subplot(2, 2, 3)
            self._carn_axis = None

        if self._mean_ax is None:
           self._mean_ax = self._fig.add_subplot(2, 2, 4)
           self._mean_ax.set_ylim(0, y_lim)

        # setting the x limit, manually for now
        self._mean_ax.set_xlim(0, x_lim*3)

        if self._herb_line is None:
            herb_plot = self._mean_ax.plot(np.arange(0, self._final_step),
                                           np.full(self._final_step, np.nan))
            self._herb_line = herb_plot[0]
        else:
            xdata, ydata = self._herb_line.get_data()
            xnew = np.arange(xdata[-1] + 1, self._final_step)
            if len(xnew) > 0:
                ynew = np.full(xnew.shape, np.nan)
                self._herb_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata, ynew)))

        # Do the same for carn_line

        if self._carn_line is None:
            carn_plot = self._mean_ax.plot(np.arange(0, self._final_step),
                                           np.full(self._final_step, np.nan))
            self._carn_line = carn_plot[0]

        else:
            xdata, ydata = self._carn_line.get_data()
            xnew = np.arange(xdata[-1] + 1, self._final_step)
            if len(xnew) > 0:
                ynew = np.full(xnew.shape, np.nan)
                self._carn_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata, ynew)))


    def create_map(self, data):
        """
        Creates island map. Called one time at the start of the simuation.
        :param data:    array, 2D array of map spesifications
        :return: None
        """
        self._img_axis = self._map_ax.imshow(data, cmap='terrain'
                                             , vmax=20, vmin=1)


    def update_herb_ax(self, herb_data):
        """
        Updates heatmap for herbivore distribution
        :return: None
        """
        if self._herb_axis is not None:
            self._herb_axis.set_data(herb_data)

        else:
            self._herb_axis = self._herb_ax.imshow(herb_data,
                                                 interpolation='nearest',
                                                 cmap="Greens")
            self._herb_ax.figure.colorbar(self._herb_axis, ax=self._herb_ax
                                          , orientation='horizontal')


    def update_carn_ax(self, carn_data):
        """
        Updates heatmap for carnivore distribution
        :return: None
        """
        if self._carn_axis is not None:
            self._carn_axis.set_data(carn_data)

        else:
            self._carn_axis = self._carn_ax.imshow(carn_data,
                                                 interpolation='nearest',
                                                 cmap="OrRd")
            self._carn_ax.figure.colorbar(self._carn_axis, ax=self._carn_ax
                                          , orientation='horizontal')


    def update_mean_ax(self, herb_num, carn_num):
        """
        Updates linegraphs for herbivore and carnivore count
        :param herb_num:    int, total number of herbivores on island
        :param carn_num:    int, total number of carnivores on island
        :return: None
        """
        ydata = self._herb_line.get_ydata()
        ydata[self._step] = herb_num
        self._herb_line.set_ydata(ydata)
        # Another line for carnivore
        ydata = self._carn_line.get_ydata()
        ydata[self._step] = carn_num
        self._carn_line.set_ydata(ydata)
        self._step += 1

    def update_graphics(self, herb_pos, carn_pos, num_animals):
        """
        Updates graphics with current data
        :param herb_pos:     herbivore distribution on the island
        :param carn_pos:     carnivore distribution on the island
        :param num_animals:  number of herbivores and carnivores
        :return: None
        """
        # create_map will be called separately
        self.update_herb_ax(herb_pos)
        self.update_carn_ax(carn_pos)
        self.update_mean_ax(num_animals["Herbivore"], num_animals["Carnivore"])
        plt.pause(1e-6)

    def make_movie(self):
        """Makes a movie of a series of images"""
        try:
            subprocess.run(['ffmpeg',
                                    '-f','image2',
                                    '-r','6',
                                    '-i','Images\\Image-%03d.png',
                                    '-vcodec','mpeg4',
                                    '-y', 'movie.mp4',
                                    # To hide the logs
                                    '-hide_banner',
                                    '-loglevel', 'panic'
                                   ])
        except:
            return RuntimeError('Error in video generation')
