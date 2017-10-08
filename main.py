#!/usr/bin/env python3

# incorporate logging

import pygame
import time
import cv2
import modules.generation_run as gr
import modules.initialisation as init
import modules.pickle_funcs as pf
import os
import random
import modules.run_modes as rm

run_mode = 'train'  # valid values are 'train' or 'show'
particle_size = '15'  # in pixels, for square particles
track_num = '1'

num_of_generations = 1000
num_of_particles_per_generation = 100
movement_step = 15  # must be less than width of track boundary + smallest
# particle side length (e.g. max is 19 for particle_1, track_0)
mutation_chance_options = (
	[i for i in range(10, 101, 10)] +
	[i for i in range(100, 1001, 100)])
num_best_to_take = 5  # takes best N samples to mutate upon, with likelihood
# of sample being used for mutation based upon its rank
num_random_to_take = 3  # takes random M samples to mutate upon, for genetic
# diversity
chance_of_picking_random_sample = 10  # %
fps = 60  # frames per second
mutate_moves_mapping_func_type = 'exp'
pickle_best = True  # set to True to save final best moves as a pickle
adaptive_algo = [True, 1, 100, 0]  # (set to True to use a different mutation
# algorithm when victory_box has been reached that mutates all moves with equal
# chance, regardless of position; 2nd value is percent chance of mutation, when
# True; 3rd value is delay offset, which is num of generations after vistory
# that algorithm will switch; last value contains 1st generation of switch,
# auto-populated by program

# Store input parameters in a dictionary, for ease of access and retrieval
input_params = {
	'particle_size': particle_size,
	'track_num': track_num,
	'num_of_generations': num_of_generations,
	'num_of_particles_per_generation': num_of_particles_per_generation,
	'movement_step': movement_step,
	'mutation_chance_options': mutation_chance_options,
	'num_best_to_take': num_best_to_take,
	'num_random_to_take': num_random_to_take,
	'chance_of_picking_random_sample': chance_of_picking_random_sample,
	'fps': fps,
	'mutate_moves_mapping_func_type': mutate_moves_mapping_func_type,
	'pickle_best': pickle_best,
	'adaptive_algo': adaptive_algo
}


(
	track_img, particle_width, particle_height, display_width, display_height,
	particle_mask, track_mask, victory_box_mask, possible_moves,
	starting_pos, sections) = init.initialise_setup(input_params)

pygame.init()
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Genetic Algorithm Demo')
clock = pygame.time.Clock()

# Store initialisation parameters in a dictionary, for ease of access and
# retrieval
init_params = {
	'track_img': track_img,
	'particle_width': particle_width,
	'particle_height': particle_height,
	'display_width': display_width,
	'display_height': display_height,
	'particle_mask': particle_mask,
	'track_mask': track_mask,
	'victory_box_mask': victory_box_mask,
	'possible_moves': possible_moves,
	'starting_pos': starting_pos,
	'sections': sections,
	'game_display': game_display,
	'clock': clock
}


if run_mode == 'train':
	rm.run_all_generations(input_params, init_params)
elif run_mode == 'show':
	input_params['num_of_particles_per_generation'] = 1
	input_params['mutation_chance_options'] = [0]
	init_params['possible_moves'] = None
	rm.run_best_moves(input_params, init_params)
else:
	raise Exception('main error: unknown run_mode specified')


pygame.quit()
