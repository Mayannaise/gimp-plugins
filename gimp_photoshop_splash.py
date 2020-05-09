#!/usr/bin/env python
# -*- coding: utf8 -*-

from gimpfu import *

# https://github.com/python/cpython/blob/2.7/Lib/colorsys.py
def rgb_to_hsv(r, g, b):
	maxc = max(r, g, b)
	minc = min(r, g, b)
	v = maxc
	if minc == maxc:
		return 0.0, 0.0, v
	s = (maxc-minc) / maxc
	rc = (maxc-r) / (maxc-minc)
	gc = (maxc-g) / (maxc-minc)
	bc = (maxc-b) / (maxc-minc)
	if r == maxc:
		h = bc-gc
	elif g == maxc:
		h = 2.0+rc-bc
	else:
		h = 4.0+gc-rc
	h = (h/6.0) % 1.0
	return h, s, v
	
# https://github.com/python/cpython/blob/2.7/Lib/colorsys.py
def hsv_to_rgb(h, s, v):
	if s == 0.0:
		return v, v, v
	i = int(h*6.0) # XXX assume int() truncates!
	f = (h*6.0) - i
	p = v*(1.0 - s)
	q = v*(1.0 - s*f)
	t = v*(1.0 - s*(1.0-f))
	i = i%6
	if i == 0:
		return v, t, p
	if i == 1:
		return q, v, p
	if i == 2:
		return p, v, t
	if i == 3:
		return p, q, v
	if i == 4:
		return t, p, v
	if i == 5:
		return v, p, q
		
def photoshopSplash( img, draw ):
	#prepare effect
	current_f=pdb.gimp_context_get_foreground()
	img.disable_undo()

	#create layer group for new effect
	lg=pdb.gimp_layer_group_new(img)
	pdb.gimp_image_insert_layer(img, lg, None, 0)
	pdb.gimp_item_set_name(lg,"Splash")

	#copy original image to new layer (color)
	origCopy=pdb.gimp_layer_new_from_drawable(draw,img)
	pdb.gimp_image_insert_layer(img, origCopy, lg, 0)
	pdb.gimp_item_set_name(origCopy,"Color")
	
	#copy original image to new layer (grayscale)
	grayscaleBG=pdb.gimp_layer_new_from_drawable(draw,img)
	pdb.gimp_image_insert_layer(img, grayscaleBG, lg, 0)
	pdb.gimp_item_set_name(grayscaleBG,"Grayscale")
	pdb.gimp_image_set_active_layer(img,grayscaleBG)
	pdb.gimp_desaturate_full(grayscaleBG, 0)

	#add color mask to grayscale image
	mask=pdb.gimp_layer_create_mask(grayscaleBG,0)
	pdb.gimp_layer_add_mask(grayscaleBG,mask)
	pdb.gimp_image_set_active_layer(img,origCopy)		#swap to color layer
	pdb.gimp_context_set_feather(TRUE)
	pdb.gimp_context_set_feather_radius(15.0,15.0)
	pdb.gimp_context_set_sample_threshold_int(25)
	#select by HSV value
	hsvSplash = rgb_to_hsv(current_f.red,current_f.green,current_f.blue)
	minVal = hsvSplash[2]-0.6
	maxVal = hsvSplash[2]+0.5
	if minVal < 0.2: minVal = 0.2
	if maxVal > 1: maxVal = 1
	val = minVal
	while val < maxVal:
		newcolor = hsv_to_rgb(hsvSplash[0],hsvSplash[1],val)
		pdb.gimp_image_select_color(img,0,draw,newcolor)
		val += 0.01
	#select by HSV saturation
	hsvSplash = rgb_to_hsv(current_f.red,current_f.green,current_f.blue)
	minSat = hsvSplash[1]-0.3
	maxSat = hsvSplash[1]+0.3
	if minSat < 0: minSat = 0
	if maxSat > 1: maxSat = 1
	sat = minSat
	while sat < maxSat:
		newcolor = hsv_to_rgb(hsvSplash[0],sat,hsvSplash[2])
		pdb.gimp_image_select_color(img,0,draw,newcolor)
		sat += 0.01
	#mask selected areas
	pdb.gimp_image_set_active_layer(img,grayscaleBG)	#swap back to mask
	pdb.gimp_context_set_foreground((0,0,0))			#set fg black for masking
	pdb.gimp_edit_bucket_fill(mask,0,0,100,0,FALSE,0,0)
	
	#finish off
	img.enable_undo()
	pdb.gimp_selection_none(img)
	pdb.gimp_image_set_active_layer(img,lg)
	pdb.gimp_context_set_foreground(current_f)


register( "gimp_photoshop_splash",
  "Add Colour Splash effect using fg color",
  "Add Colour Splash effect using fg color",
  "Owen Jeffreys",
  "Owen Jeffreys",
  "2019",
  "<Image>/Filters/Photoshop/Splash/FG Color",
  'RGB*',
  [],
  '',
  photoshopSplash)

main()

