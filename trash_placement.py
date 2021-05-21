#!/usr/bin/env python3

import numpy as np
import math
import os
# os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# import pygame, sys
# from pygame.locals import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import random
from enum import Enum, unique
from dataclasses import dataclass
from typing import List

# Data from https://www.nature.com/articles/s41598-018-22939-w (Table 2)

"""
For Distribution Reference: https://globaltrashsolutions.com/blog/great-pacific-garbage-patch/
8% Microplastics
13% Mesoplastics
26% Macroplastics
53% Megaplastics
"""
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
    SizeClass.MEGA: (50, 200)
    # Assume >50cm category goes up to 2m. Detailed data on sizes can be found in the 
    # Sampling Information spreadsheet linked in the Figshare (reference 33) of this 
    # article: https://www.nature.com/articles/s41598-018-22939-w. The MosaicDebrisInfo 
    # sheet contains data on larger pieces from aerial imaging. Many pieces, including
    # nets, are long and skinny, so with our simple cube/sphere shapes choosing a max
    # size isn't straightforward, but 2 meters seems reasonable. Given more time, 
    # we could do better modelling on the variation of shapes, etc.
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

# Percent of pieces of each material. Table 3 in the Supplementary Material of https://www.nature.com/articles/s41598-018-22939-w, taking averages within each major size class.
plastic_materials = { 
    SizeClass.MICRO: {
        PlasticType.H: (("PE",0.95), ("PP",0.05)),
        PlasticType.N: (("PE",0.50), ("PP",0.50)),
        PlasticType.P: (("PE",1.00),),
        PlasticType.F: (("PE",0.30), ("PS",0.60)), # 10% unknown
    },
    SizeClass.MESO: {
        PlasticType.H: (("PE",0.75), ("PP",0.25)),
        PlasticType.N: (("PE",0.70), ("PP",0.30)),
        PlasticType.P: (("PE",1.00),),
        PlasticType.F: (("PE",0.40), ("PP",0.05), ("PS",0.40), ("PVC",0.10)) # 5% unknown
    },
    SizeClass.MACRO: {
        PlasticType.H: (("PE",0.55), ("PP",0.45)),
        PlasticType.N: (("PE",0.65), ("PP",0.35)),
        PlasticType.F: (("PE",0.50), ("PP",0.05), ("PS",0.15), ("PVC",0.10)) # 20% unknown
    },
    SizeClass.MEGA: {
        PlasticType.H: (("PE",0.60), ("PP",0.40)),
        PlasticType.N: (("PE",0.80), ("PP",0.10)) # 10% unknown
    }
}

material_densities = { # in kg/m^3, densities from Wikipedia
    "PE": 920, # polyethylene, 0.88–0.96 g/cm3
    "PP": 900.5, # polypropylene, 0.855 g/cm3 amorphous, 0.946 g/cm3 crystalline
    "PS": 1005, # polystyrene, 0.96–1.05 g/cm3
    "PVC": 1005 # polyvinyl chlorine, 1.3–1.45 g/cm3 Rigid PVC, 1.1–1.35 g/cm3 Flexible PVC, use same density as PS since PVC denser than water, and we're not making buoyant shapes.
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

# make total concentration = 100 kg/km^2
default_mean_scale = 100 / total_mean_plastic_concentration[0] # how much to scale concentrations compared to the mean

@dataclass
class Trash:
    x: float
    y: float
    size: float
    mass: float
    density: float
    size_class: SizeClass
    plastic_type: PlasticType

# L: square side length (meters)
# mean_scale: how much to scale concentrations compared to the mean
def generate_trash(W, H, boat_pos=(0,0), boat_box=(0,0), centered=False, mean_scale=default_mean_scale, relevant_size_classes=[SizeClass.MESO, SizeClass.MACRO, SizeClass.MEGA]) -> List[Trash]:
    pieces: List[Trash] = [
        Trash(x=130, y=120, size=0.75, mass=0, density=0, size_class=SizeClass.MEGA, plastic_type=PlasticType.N) # TODO temporary: hardcode megaplastic
    ]
    for size_class in relevant_size_classes:
        for plastic_type in PlasticType:
            total_mass = mean_scale * mean_plastic_concentration[size_class][plastic_type][0] * (W/1000)*(H/1000)
            n_pieces = mean_scale * mean_plastic_concentration[size_class][plastic_type][1] * (W/1000)*(H/1000)
            if n_pieces > 0:
                avg_mass_per_piece = total_mass / n_pieces
                n_pieces = np.random.choice((math.floor(n_pieces), math.ceil(n_pieces)), p=(1 - (n_pieces-math.floor(n_pieces)), 1 - (math.ceil(n_pieces)-n_pieces))).astype(int) # round with appropriate probability
                total_mass = avg_mass_per_piece * n_pieces # adjust total_mass after rounding n_pieces to the nearest whole number
                total_mass_proportion = 0
                for i in range(n_pieces):
                    pos_range = ((-W/2, W/2), (-H/2, H/2)) if centered else ((0, W), (0, H))
                    pos = (random.uniform(*pos_range[0]), random.uniform(*pos_range[1]))
                    while boat_pos[0] - boat_box[0]/2 < pos[0] and pos[0] < boat_pos[0] + boat_box[0]/2 and boat_pos[1] - boat_box[1]/2 < pos[1] and pos[1] < boat_pos[1] + boat_box[1]/2:
                        pos = (random.uniform(*pos_range[0]), random.uniform(*pos_range[1])) # don't place trash that intersects with the boat
                    
                    size = 10 ** random.uniform(math.log10(size_ranges[size_class][0]), math.log10(size_ranges[size_class][1])) # Distribute sizes uniformly on log scale, since size classes are broken up evenly on a log scale, and number concentration follows a roughly logarithmic relation.
                    size /= 100 # convert from cm to m

                    possible_materials = []
                    material_probabilities = []
                    for material in plastic_materials[size_class][plastic_type]:
                        possible_materials.append(material[0])
                        material_probabilities.append(material[1])
                    material_probabilities = np.array(material_probabilities)
                    material_probabilities = material_probabilities / np.sum(material_probabilities)
                    material = np.random.choice(possible_materials, p=material_probabilities)
                    density = material_densities[material]
                    
                    pieces.append(Trash(x=pos[0], y=pos[1], size=size, mass=0, density=density, size_class=size_class, plastic_type=plastic_type)) # (position), size, mass
                    total_mass_proportion += density * size**3 # set mass proportional to density * size^3
                for i in range(len(pieces) - n_pieces, len(pieces)):
                    pieces[i].mass = total_mass * (pieces[i].density * pieces[i].size**3)/total_mass_proportion # assume mass is proportional to the cube of size

    return pieces

def plot_trash(W, H, pieces: List[Trash], centered=False):
    pos_range = ((-W/2, W/2), (-H/2, H/2)) if centered else ((0, W), (0, H))
    fig, ax = plt.subplots()
    plt.xlim(pos_range[0])
    plt.ylim(pos_range[1])
    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")
    
    size_classes = set()
    piece_counts = {}
    for size_class in SizeClass:
        piece_counts[size_class] = {}
        for plastic_type in PlasticType:
            piece_counts[size_class][plastic_type] = 0

    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    pixel_width = bbox.width*fig.dpi
    outlinline_width = 2
    radius_buffer = outlinline_width * W/pixel_width

    for piece in pieces:
        size_classes.add(piece.size_class)
        piece_counts[piece.size_class][piece.plastic_type] += 1
        outline_circle = plt.Circle((piece.x, piece.y), piece.size/2 + radius_buffer, clip_on=False, color=size_class_colors[piece.size_class])
        piece_circle = plt.Circle((piece.x, piece.y), piece.size/2, clip_on=False, color='black')
        ax.add_patch(outline_circle)
        ax.add_patch(piece_circle)
        # plt.scatter(np.array(pieces[size_class][plastic_type][0])[:,0], np.array(pieces[size_class][plastic_type][0])[:,1], np.pi * (np.array(pieces[size_class][plastic_type][1]))**2, c=None, linewidths=None, edgecolors=None)
    
    for size_class in size_classes:
        for plastic_type in PlasticType:
            print("Number of {} of type {}: {}".format(size_class_names[size_class], plastic_type_names[plastic_type], piece_counts[size_class][plastic_type]))

    legend_elements = [Patch(color=size_class_colors[size_class], label=size_class_names[size_class]) for size_class in size_classes]
    ax.legend(handles=legend_elements, bbox_to_anchor=(0.5, 1.14), loc='upper center')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def main():
    W = 100 # area width (meters)
    H = 100 # area height (meters)
    # note, there is 1 piece of megaplastic every (527m^2)/sqrt(mean_scale)

    mean_scale = default_mean_scale

    relevant_size_classes = [SizeClass.MESO, SizeClass.MACRO, SizeClass.MEGA]

    centered = False
    pieces = generate_trash(W, H, (0,0), (0,0), centered, mean_scale, relevant_size_classes)
    plot_trash(W, H, pieces, centered)
    
if __name__ == "__main__":
    main()
