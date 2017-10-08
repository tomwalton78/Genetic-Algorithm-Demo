#!/usr/bin/env python3

import modules.colour_store as cs
import time
from math import exp
from modules.particle import Particle
import random
import modules.distance_handling as dh
import pygame

"""Note: this script assumes that the direction of a particular section is
towards the wall that is furthest away from the start point, which is at the
corner where the last section turns into the current section. Therefore very
short sections may present issues."""


def track_display(init_params):
	"""Displays track"""
	init_params['game_display'].blit(init_params['track_img'], (0, 0))


def collision_check(static_mask, moving_mask, x_coord, y_coord):
	"""Checks if moving_mask overlaps with static_mask for specified x, y
	coordinates; overlap means collision"""
	x_p, y_p = int(round(x_coord, 0)), int(round(y_coord, 0))
	if static_mask.overlap(moving_mask, (x_p, y_p)):
		return True
	else:
		return False


def mutate_moves(
	input_moves, input_params, possible_moves, victory_status):
	"""Takes input moves and returns list with some moves changed randomly,
	according to specified chance and function. Exponential function ensures that
	it is more likely that moves near the end of the list are mutated, as these
	are more likely to need improving"""
	mutated_moves = []
	if not victory_status:
		input_moves_indexes_scaled = (
			[(i / (len(input_moves) * 100)) for i in range(1, len(input_moves) + 1)])
		if input_params['mutate_moves_mapping_func_type'] == 'exp':
			input_moves_mapped_to_func = (
				[exp(j) for i, j in enumerate(input_moves_indexes_scaled)])
		elif input_params['mutate_moves_mapping_func_type'] == 'quadratic':
			input_moves_mapped_to_func = (
				[j**2 for i, j in enumerate(input_moves_indexes_scaled)])
		else:
			raise Exception("mutate_moves error: unknown mapping_func_type")
		input_moves_probabilities = (
			[j / sum(input_moves_mapped_to_func) for i, j in enumerate(
				input_moves_mapped_to_func)])
		mutation_chance_factor = random.choice(
			input_params['mutation_chance_options'])
		for i, j in enumerate(input_moves_probabilities):
			if random.randint(1, 100) <= j * mutation_chance_factor:
				# mutate move
				mutated_moves.append(random.choice(possible_moves))
			else:
				mutated_moves.append(input_moves[i])
	if victory_status and input_params['adaptive_algo'][0]:
		"""switch to a different mutation algorithm once victory has been achieved and
		a certain no. of generations have passed"""
		rand_index = random.randint(0, len(input_moves) - 1)
		mutated_moves = (
			[j if i != rand_index else random.choice(possible_moves) for
				i, j in enumerate(input_moves)])
	return mutated_moves


def initialise_mutated_moves(
	particles, chosen_indices, combined_results, input_params,
	possible_moves, victory_status):
	"""Mutate moves for each particle"""
	for i, j in enumerate(chosen_indices):
		particles[i].best_moves_mutated = mutate_moves(
			combined_results[j][0], input_params, possible_moves, victory_status)


def some_alive_check(particles):
	"""Check that at least one particle is alive"""
	for particle in particles:
		if particle.alive:
			return True
	else:
		return False


def choose_move(
	counter, possible_moves, particle):
	"""Choose new random move if have not got to this number of moves before,
	otherwise choose from pre-existing, mutated moves"""
	if counter >= len(particle.best_moves_mutated):
		"""If move counter is higher than previous max num of moves, add a new
		random move to move sequence"""
		move = random.choice(possible_moves)
	else:
		move = particle.best_moves_mutated[counter]
	return move


def act_on_move(move, movement_step):
	"""Turn move into appropriate change in x, y coordinates"""
	if move == 'up' or move == 'down':
		# i.e. changes y coordinate
		if move == 'up':
			y_change = - movement_step
		elif move == 'down':
			y_change = movement_step
		x_change = 0
	elif move == 'left' or 'right':
		# i.e. change x coordinate
		if move == 'left':
			x_change = - movement_step
		elif move == 'right':
			x_change = movement_step
		y_change = 0
	return x_change, y_change


def check_for_collisions(init_params, particle, counter, start_time):
	"""Checks for particle colliding with track boundary and victory box"""
	if collision_check(
		init_params['track_mask'], init_params['particle_mask'],
		particle.x, particle.y):
		# game over
		particle.alive = False
	if collision_check(
		init_params['victory_box_mask'], init_params['particle_mask'],
		particle.x, particle.y):
		# victory
		# game over (1st check) or victory (2nd check)
		particle.alive = False
		current_time_elapsed = round(time.time() - start_time, 2)
		particle.distance_time_record = (
			10E8,
			counter,
			current_time_elapsed)


def check_particle_in_bounds(particle, init_params, game_exit, testing=False):
	"""Check that particle is within bounds of pygame display"""
	if (
		particle.x > init_params['display_width'] - init_params['particle_width'] or
		particle.x < 0 or
		particle.y < 0 or
		particle.y > init_params['display_height'] - init_params['particle_height']):
		game_exit = True
		if not testing:
			print("particle exceeded bounds of game!")
	return game_exit


def evaluate_performance(particles):
	"""Return moves up until furthest distance reached, and corresponding
	distance_score and time"""
	return_list = (
		[(particle.moves_made[0: particle.distance_time_record[1] + 1],
			particle.distance_time_record[0],
			particle.distance_time_record[2])
			for i, particle in enumerate(particles)])
	return return_list


def run_one_generation(
	input_params, init_params, combined_results, chosen_indices, victory_status):
	"""Run through all iterations until particle collided with track or
	victory_box, for all particles in a single generation, then returing their
	performance"""
	# Initialise variables and objects
	particles = (
		[Particle(
			input_params['particle_size'], init_params['starting_pos']) for i in range(
			input_params['num_of_particles_per_generation'])])
	initialise_mutated_moves(
		particles, chosen_indices, combined_results, input_params,
		init_params['possible_moves'], victory_status)
	game_exit = False
	start_time = time.time()

	counter = 0
	while some_alive_check(particles) and not game_exit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_exit = True

		# Reset display and set track as background
		init_params['game_display'].fill(cs.white)
		track_display(init_params)

		for i, particle in enumerate(particles):
			if particle.alive:
				move = choose_move(counter, init_params['possible_moves'], particle)
				particle.moves_made.append(move)

				particle.x_change, particle.y_change = act_on_move(
					move, input_params['movement_step'])

				# Update particle with new position and put on display
				particle.update_position((particle.x_change, particle.y_change))
				particle.show(init_params['game_display'], (particle.x, particle.y))

				check_for_collisions(init_params, particle, counter, start_time)

				if particle.alive:
					# no collisions
					particle.current_distance_score = dh.update_distance_score(
						init_params['sections'], particle, particle.last_point,
						input_params['movement_step'])
					particle.last_point = (particle.x, particle.y)
					# update best distance score, if it has improved
					if particle.current_distance_score > particle.distance_time_record[0]:
						current_time_elapsed = round(time.time() - start_time, 2)
						particle.distance_time_record = (
							particle.current_distance_score, counter, current_time_elapsed)

				game_exit = check_particle_in_bounds(particle, init_params, game_exit)

		pygame.display.update()
		init_params['clock'].tick(input_params['fps'])
		counter += 1

	return_list = evaluate_performance(particles)

	return return_list
