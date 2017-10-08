#!/usr/bin/env python3

import pygame
import modules.colour_store as cs
import cv2
from modules.mask_handling import set_masks
import modules.distance_handling as dh
import os


def get_starting_pos(track_num, colour, parent_path):
	"""Obtain starting_pos based on position of pixel with specified colour in
	specified track. There should be only 1 pixel with this colour, as first
	discovery of this colour will be used as starting_pos"""
	colour = list(colour)
	img = cv2.imread(
		parent_path + '/tracks/track_{}/track_{}_start_mark.png'.format(
			track_num, track_num))
	img_to_list = img.tolist()
	for i, j in enumerate(img_to_list):
		if colour in j:
			i2 = j.index(colour)
			item_index = (i2, i)
			break
	return item_index[0], item_index[1]


def initialise_setup(input_params):
	"""Retrieves particle and track images and info"""
	parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	if not os.path.isfile(parent_path + '/particles/particle_{}.png'.format(
		input_params['particle_size'])):
		raise Exception(
			"""initialise_setup error: a particle with size {} does not exist, \
			please enter a different size or create this particle.""".format(
				input_params['particle_size']).replace('\t', ''))
	particle_img = pygame.image.load(
		parent_path + '/particles/particle_{}.png'.format(
			input_params['particle_size']))
	# particle referenced by top-left of image
	track_img = pygame.image.load(
		parent_path + '/tracks/track_{}/track_{}_full.png'.format(
			input_params['track_num'], input_params['track_num']))
	particle_width = particle_img.get_rect().size[0]
	particle_height = particle_img.get_rect().size[1]
	display_width, display_height = (
		track_img.get_rect().size[0], track_img.get_rect().size[1])
	# ^top-left is (0, 0)

	particle_mask, track_mask, victory_box_mask = set_masks(
		input_params['particle_size'], input_params['track_num'])
	possible_moves = ['up', 'down', 'left', 'right']

	starting_pos = get_starting_pos(
		input_params['track_num'], cs.green, parent_path)
	sections = dh.retrieve_sections(input_params['track_num'])
	dh.section_check(sections)

	return (
		track_img, particle_width, particle_height, display_width, display_height,
		particle_mask, track_mask, victory_box_mask, possible_moves, starting_pos,
		sections)
