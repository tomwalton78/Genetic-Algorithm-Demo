#!/usr/bin/env python3

import pygame
import os


def set_masks(particle_num, track_num):
	"""Initialises mask objects, for given track; used for collision detection"""
	# Import images
	parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	particle_img = pygame.image.load(
		parent_path + '/particles/particle_{}.png'.format(
			particle_num))
	track_boundary_img = pygame.image.load(
		parent_path + '/tracks/track_{}/track_{}_boundary.png'.format(
			track_num, track_num))
	victory_box_img = pygame.image.load(
		parent_path + '/tracks/track_{}/track_{}_victory_box.png'.format(
			track_num, track_num))

	# Set masks
	particle_mask = pygame.mask.from_surface(particle_img)
	track_mask = pygame.mask.from_surface(track_boundary_img)
	victory_box_mask = pygame.mask.from_surface(victory_box_img)

	return particle_mask, track_mask, victory_box_mask
