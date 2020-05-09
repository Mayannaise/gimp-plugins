#!/usr/bin/env python
# -*- coding: utf8 -*-

from gimpfu import *

WEDGETYPE_RADIAL = 0
WEDGETYPE_PARALLEL = 1

WEDGESHAPE_TRIANGLE = 0
WEDGESHAPE_RECTANGLE = 1

def wedgedeblur(image, drawable, wedgetype, wedgeshape, wedgegap, slipx, slipy):
    master_layer = image.active_layer
    non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
    wedgesize = y2-y1
    apex = x1, y2
    p1 = x2, y1
    p2 = p1
    offset = 0
    #check use has selected start wedge
    if not non_empty:
        pdb.gimp_message("No selection")
    else:
        #create new layer for edits
        edit_layer = gimp.Layer(image, "Edits", image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
        pdb.gimp_image_insert_layer(image, edit_layer, None, 0)
        image.active_layer = master_layer
        #loop through image creating wedges
        while True:
            #setup wedge vertices
            p1 = p2[0], p2[1]+wedgegap
            p2 = p1[0], p1[1]+wedgesize
            if wedgetype == WEDGETYPE_PARALLEL:
                if wedgeshape == WEDGESHAPE_RECTANGLE:
                    apex = apex[0], p1[1], apex[0], p2[1]
                elif wedgeshape == WEDGESHAPE_TRIANGLE:
                    apex = apex[0], apex[1]+wedgesize
            #quit if we have reached bottom of image
            if p2[1] > image.height:
                break
            #select wedge, copy it and paste into new layer
            segs = list(apex + p2 + p1)
            pdb.gimp_image_select_polygon(image, CHANNEL_OP_REPLACE, len(segs), segs)
            pdb.gimp_edit_copy(master_layer)
            image.active_layer = edit_layer
            offset = offset + wedgegap
            pdb.gimp_layer_set_offsets(edit_layer, 0, offset)
            selection = pdb.gimp_edit_paste(edit_layer, True)
            non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
            selection = pdb.gimp_item_transform_scale(selection, x1, y1, x2+slipx, y2+slipy)
            #selection = pdb.gimp_item_transform_shear(selection, ORIENTATION_HORIZONTAL, -8.0)
            pdb.gimp_floating_sel_anchor(selection)

register(
    "gimp_wedge_deblur",
    "Removes variable motion blur (e.g. camera shake) using a bespoke triangulation method",
    "Removes variable motion blur (e.g. camera shake) using a bespoke triangulation method",
    "Owen Jeffreys",
    "Owen Jeffreys",
    "2020",
    "<Image>/Filters/Enhance/Wedge Deblur...",
    "RGB*",
    [
        (PF_RADIO, "wedgetype", "Wedge type: ", WEDGETYPE_RADIAL,
            (("Radial",   WEDGETYPE_RADIAL),
             ("Parallel", WEDGETYPE_PARALLEL))
        ),
        (PF_RADIO, "wedgeshape", "Wedge shape: ", WEDGESHAPE_TRIANGLE,
            (("Triangular",   WEDGESHAPE_TRIANGLE),
             ("Rectangular", WEDGESHAPE_RECTANGLE))
        ),
        (PF_SLIDER, "wedgegap", "Wedge Gap", 4, [1, 300, 1]),
        (PF_SLIDER, "slipx", "X Distance", 10, [-20, 20, 1]),
        (PF_SLIDER, "slipy", "Y Distance", -5, [-20, 20, 1]),
    ],
    '',
    wedgedeblur
)

main()

