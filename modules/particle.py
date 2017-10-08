#!/usr/bin/env python3

import pygame
import os


class Particle:
	"""Stores info and properties of a particle"""

	def __init__(self, particle_size, starting_pos):
		parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
		self.x = starting_pos[0]
		self.y = starting_pos[1]
		self.img = pygame.image.load(
			parent_path + '/particles/particle_{}.png'.format(particle_size))

		self.alive = True
		self.x_change = 0
		self.y_change = 0
		self.moves_made = []
		self.distance_time_record = (0, 0, 0)  # tuple of furthest distance,
		# corresponding step no. to reach that distance and time to get to that point
		self.current_distance_score = 0
		self.last_point = (starting_pos[0], starting_pos[1])  # tracks point particle
		# was at 1 generation ago

	def show(self, game_display, position):
		game_display.blit(self.img, position)

	def update_position(self, position_change):
		self.x += position_change[0]
		self.y += position_change[1]
