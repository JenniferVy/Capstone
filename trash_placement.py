#!/usr/bin/env python3

import numpy as np
import os
# os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# import pygame, sys
# from pygame.locals import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import random
from enum import Enum, unique

# Data from https://www.nature.com/articles/s41598-018-22939-w (Table 2)

@unique
class SizeClass(Enum):
    MICRO = 1
    MESO = 2
    MACRO = 3
    MEGA = 4

size_class_colors = {
    SizeClass.MICRO: 'blue',
    SizeClass.MESO: 'green',
    SizeClass.MACRO: 'orange',
    SizeClass.MEGA: 'red'
}

# centimeters
size_ranges = {
    SizeClass.MICRO: (0.05, 0.5),
    SizeClass.MESO: (0.5, 5),
    SizeClass.MACRO: (5, 50),
    SizeClass.MEGA: (50, 2000) # assume >50cm category goes up to 2m (Subject to change. Some are bigger, but not sure how many.)
}

size_class_names = {
    SizeClass.MICRO: 'Microplastics ({}cm - {}cm)'.format(*size_ranges[SizeClass.MICRO]),
    SizeClass.MESO: 'Mesoplastics ({}cm - {}cm)'.format(*size_ranges[SizeClass.MESO]),
    SizeClass.MACRO: 'Macroplastics ({}cm - {}cm)'.format(*size_ranges[SizeClass.MACRO]),
    SizeClass.MEGA: 'Megaplastics (>{}cm)'.format(size_ranges[SizeClass.MEGA][0])
}

# "Plastic type H include pieces of hard plastic, plastic sheet and film, type N encompasses plastic lines, ropes and fishing nets, type P are pre-production plastic pellets, and type F are pieces made of foamed material."
@unique
class PlasticType(Enum):
    H = 1
    N = 2
    P = 3
    F = 4

plastic_type_names = {
    PlasticType.H: 'H (hard plastic, plastic sheet and film)',
    PlasticType.N: 'N (plastic lines, ropes and fishing nets)',
    PlasticType.P: 'P (pre-production plastic pellets)',
    PlasticType.F: 'F (foamed material)'
}

# mass and number concentration: (kg/km^2, #/km^2)
mean_plastic_concentration = {
    SizeClass.MICRO: {
        PlasticType.H: (2.33, 643930),
        PlasticType.N: (0.041, 19873),
        PlasticType.P: (0.13, 14362),
        PlasticType.F: (0.001, 216)
    },
    SizeClass.MESO: {
        PlasticType.H: (3.68, 20993),
        PlasticType.N: (0.23, 803),
        PlasticType.P: (0.0003, 3.6),
        PlasticType.F: (0.003, 12)
    },
    SizeClass.MACRO: {
        PlasticType.H: (15.53, 640),
        PlasticType.N: (1.27, 49),
        PlasticType.P: (0, 0),
        PlasticType.F: (0.021, 0.7)
    },
    SizeClass.MEGA: {
        PlasticType.H: (3.52, 0.3),
        PlasticType.N: (42.82, 3.3),
        PlasticType.P: (0, 0),
        PlasticType.F: (0, 0)
    }
}

# mass and number concentration: (kg/km^2, #/km^2)
total_mean_plastic_concentration = (69.58, 700,886)

# L: square side length (meters)
# mean_scale: how much to scale concentrations compared to the mean
def generate_trash(W, H, mean_scale, relevant_size_classes):
    masses = {}
    pieces = {}
    for size_class in relevant_size_classes:
        pieces[size_class] = {}
        masses[size_class] = {}
        for plastic_type in PlasticType:
            pieces[size_class][plastic_type] = []
            masses[size_class][plastic_type] = []
            total_mass = mean_scale * mean_plastic_concentration[size_class][plastic_type][0] * (W/1000)*(H/1000)
            n_pieces = mean_scale * mean_plastic_concentration[size_class][plastic_type][1] * (W/1000)*(H/1000)
            if n_pieces > 0:
                mass_per_piece = total_mass / n_pieces
                n_pieces = np.rint(n_pieces).astype(int)
                total_mass = mass_per_piece * n_pieces # adjust total_mass after rounding n_pieces to the nearest whole number
                total_cubed_sum_of_sizes = 0
                for i in range(n_pieces):
                    size = random.uniform(*size_ranges[size_class])
                    pieces[size_class][plastic_type].append(((random.uniform(0, W), random.uniform(0, H)), size)) # (position), size
                    total_cubed_sum_of_sizes += size**3
                for i in range(n_pieces):
                    masses[size_class][plastic_type].append(total_mass * (pieces[size_class][plastic_type][i][1]**3)/total_cubed_sum_of_sizes) # assume mass is proportional to the cube of size

    return pieces, masses

def main():
    # make total concentration = 100 kg/km^2
    mean_scale = 100 / total_mean_plastic_concentration[0] # how much to scale concentrations compared to the mean

    W = 100 # area width (meters)
    H = 100 # area height (meters)
    # note, there is 1 piece of megaplastic every (527m^2)/sqrt(mean_scale)

    relevant_size_classes = [SizeClass.MESO, SizeClass.MACRO, SizeClass.MEGA]

    pieces, masses = generate_trash(W, H, mean_scale, relevant_size_classes)

    fig, ax = plt.subplots()
    plt.xlim([0, W])
    plt.ylim([0, H])
    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")
    
    legend_elements = [Patch(color=size_class_colors[size_class], label=size_class_names[size_class]) for size_class in pieces]
    ax.legend(handles=legend_elements, bbox_to_anchor=(0.5, 1.14), loc='upper center')

    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    pixel_width = bbox.width*fig.dpi
    outlinline_width = 2
    radius_buffer = outlinline_width * W/pixel_width

    for size_class in pieces:
        for plastic_type in pieces[size_class]:
            print("Number of {} of type {}: {}".format(size_class_names[size_class], plastic_type_names[plastic_type], len(pieces[size_class][plastic_type])))
            for piece in pieces[size_class][plastic_type]:
                outline_circle = plt.Circle(piece[0], piece[1]/2/100 + radius_buffer, clip_on=False, color=size_class_colors[size_class])
                piece_circle = plt.Circle(piece[0], piece[1]/2/100, clip_on=False, color='black')
                ax.add_patch(outline_circle)
                ax.add_patch(piece_circle)
                # plt.scatter(np.array(pieces[size_class][plastic_type][0])[:,0], np.array(pieces[size_class][plastic_type][0])[:,1], np.pi * (np.array(pieces[size_class][plastic_type][1])/100)**2, c=None, linewidths=None, edgecolors=None)
    
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == "__main__":
    main()
