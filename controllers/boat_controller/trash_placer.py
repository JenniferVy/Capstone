import math
from trash_placement import *

BACKSCATTERING_CROSS_SECTION_SCALING = 0.5 # The backscattering cross-section of a piece of trash relative to a sphere with the same diameter.

relevant_size_classes = [
    # SizeClass.MESO,
    SizeClass.MACRO,
    SizeClass.MEGA
]

def place_trash(root_nodes, boat_x, boat_z, W, L):
    pieces = generate_trash(W, L, (boat_z,boat_x), (10,15), centered=True, relevant_size_classes=relevant_size_classes)
    for i in range(len(pieces)):
        piece = pieces[i]
        # A piece of trash is modelled as a cube with a hole, with volume = a^3 - ab^2, where a is the cube side length and b is the hole side length.
        V = piece.mass / piece.density
        a = piece.size
        b = math.sqrt(a**2 - V/a) # hole size, to ensure the correct size and density

        backscattering_cross_section = BACKSCATTERING_CROSS_SECTION_SCALING * math.pi*(piece.size/2)**2

        cr, cg, cb, = (0, 0, 0)
        color_string = size_class_colors[piece.size_class]
        if color_string == "blue":
            cb = 1
        elif color_string == "green":
            cg = 1
        elif color_string == "orange":
            cr = 1
            cg = 0.5
        elif color_string == "red":
            cr = 1

        trash_node_str = """
            DEF TRASH_{i} Solid {{
              translation {y} 0 {x}
              rotation 0 1 0 0
              children [
                DEF TRASH_{i}_SHAPE Group {{
                  children [
                    Transform {{
                      translation 0 0 -{r}
                      children [
                        Shape {{
                          appearance PBRAppearance {{
                            baseColor 0.5 0.5 0.5
                            metalness 0
                            emissiveIntensity 0
                          }}
                          geometry Box {{
                            size {b} {a} {t}
                          }}
                        }}
                      ]
                    }}
                    Transform {{
                      translation 0 0 {r}
                      children [
                        Shape {{
                          appearance PBRAppearance {{
                            baseColor 0.5 0.5 0.5
                            metalness 0
                            emissiveIntensity 0
                          }}
                          geometry Box {{
                            size {b} {a} {t}
                          }}
                        }}
                      ]
                    }}
                    Transform {{
                      translation {r} 0 0
                      children [
                        Shape {{
                          appearance PBRAppearance {{
                            baseColor 0.5 0.5 0.5
                            metalness 0
                            emissiveIntensity 0
                          }}
                          geometry Box {{
                            size {t} {a} {a}
                          }}
                        }}
                      ]
                    }}
                    Transform {{
                      translation -{r} 0 0
                      children [
                        Shape {{
                          appearance PBRAppearance {{
                            baseColor 0.5 0.5 0.5
                            metalness 0
                            emissiveIntensity 0
                          }}
                          geometry Box {{
                            size {t} {a} {a}
                          }}
                        }}
                      ]
                    }}
                  ]
                }}
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {cr} {cg} {cb}
                    transparency 0.5
                    metalness 0
                    emissiveIntensity 0
                  }}
                  geometry Cylinder {{
                    height 0.1
                    radius 0.3
                  }}
                }}
              ]
              name "trash_{i}"
              immersionProperties [
                ImmersionProperties {{
                  fluidName "fluid"
                  dragForceCoefficients 0.001 0.001 0.001
                  dragTorqueCoefficients 0 0 0
                  viscousResistanceForceCoefficient 0
                  viscousResistanceTorqueCoefficient 0
                }}
              ]
              boundingObject USE TRASH_{i}_SHAPE
              physics Physics {{
                density {density}
                mass -1
              }}
              radarCrossSection {rcs}
            }}
        """.format(i=i, x=piece.x, y=piece.y, a=a, b=b, t=(a-b)/2, r=(a+b)/4, density=piece.density, rcs=backscattering_cross_section, cr=cr, cg=cg, cb=cb)
        root_nodes.importMFNodeFromString(-1, trash_node_str)
