#!/usr/bin/env python3

import time
import modules.generation_run as gr
import modules.pickle_funcs as pf
import os
import random


def get_top_results(num_best_to_take, generation_data):
	"""Puts top num_best_to_take results into top_results list, ranked by
	distance_score, then by time if ditance_scores match"""
	top_results = [[[], 0, 1000, 0] for i in range(num_best_to_take)]  # format
	# is: moves, distance_score, time, identifying_index
	for j, data in enumerate(generation_data):
		for k, top_result in enumerate(top_results):
			if data[1] >= top_result[1]:
				if data[1] > top_result[1]:
					top_results = top_results[0: k] + [list(data) + [j]] + top_results[k: -1]
					break
				elif data[2] < top_result[2]:
					top_results = top_results[0: k] + [list(data) + [j]] + top_results[k: -1]
					break
	return top_results


def update_best_result(
	best_moves, best_distance_score, corresponding_best_time, top_results,
	testing=False):
	"""Puts previous best result to top of top_results if it beats it, such that
	current best result is found"""
	if best_distance_score >= top_results[0][1]:
		if best_distance_score > top_results[0][1]:
			top_results = (
				[[best_moves, best_distance_score, corresponding_best_time, None]] +
				top_results[0: -1])
		elif corresponding_best_time < top_results[0][2]:
			top_results = (
				[[best_moves, best_distance_score, corresponding_best_time, None]] +
				top_results[0: -1])
	best_distance, corr_time = top_results[0][1], top_results[0][2]
	if not testing:
		if best_distance == 10E8:
			print('\tVictory achieved in a time of {} seconds.'.format(corr_time))
		else:
			print(
				'\tCurrent record is distance of {} pixels in time of {} seconds.'.format(
					best_distance, corr_time))
	return top_results


def get_random_selection(top_results, generation_data, num_random_to_take):
	"""Retrieves (without replacement) num_random_to_take random samples from
	generation_data, provided that sample is not already in top_results"""
	taken_indices = [x[3] for x in top_results]
	possible_indices = (
		[i for i, j in enumerate(generation_data) if i not in taken_indices])
	random_sample_indices = random.sample(possible_indices, num_random_to_take)
	random_results = (
		[list(j) + [i] for i, j in enumerate(generation_data) if (
			i in random_sample_indices)])
	return random_results


def choose_samples(
	input_params, random_results, top_results):
	"""Chooses moves to be passed on tso next generation"""
	sum_of_ranks = sum([i + 1 for i in range(input_params['num_best_to_take'])])
	dividing_factor = (
		(100 - input_params['chance_of_picking_random_sample']) /
		input_params['chance_of_picking_random_sample'])
	random_score = int((sum_of_ranks / dividing_factor) / len(random_results))
	# combines random and top results into one list, with their score, which
	# represents likelihood of being selected, appended to each data point's
	# list
	combined_results = (
		[y[0: 3] + [len(top_results) - x] for x, y in enumerate(top_results)] +
		[y[0: 3] + [random_score] for y in random_results])
	# generates indices of data points to be selected, based on their given score
	total_score = sum([x[3] for x in combined_results])
	chosen_indices = []
	prev_val = 0
	current_val = 0
	for x in range(input_params['num_of_particles_per_generation']):
		ran_int = random.randint(1, total_score)
		prev_val = 0
		for y, z in enumerate(combined_results):
			current_val = z[3] + prev_val
			if ran_int > prev_val and ran_int <= current_val:
				chosen_indices.append(y)
				break
			prev_val = current_val
	return combined_results, chosen_indices


def run_all_generations(input_params, init_params):
	"""Runs through specified number of generations, improving each generation
	using a genetic algorithm, whereby better performances have a higher chance of
	being mutated from"""
	best_moves = []
	best_distance_score = 0
	corresponding_best_time = 1000000000
	victory_status = False
	combined_results = (
		[([], 0, 1000000, 1)] * input_params['num_of_particles_per_generation'])
	chosen_indices = (
		[i for i in range(input_params['num_of_particles_per_generation'])])
	overall_start_time = time.time()
	for i in range(input_params['num_of_generations']):
		current_time_elapsed = round(time.time() - overall_start_time, 0)
		print(
			'Generation: {}, with {} seconds elapsed.'.format(i, current_time_elapsed))
		generation_data = gr.run_one_generation(
			input_params, init_params, combined_results, chosen_indices, victory_status)

		top_results = get_top_results(
			input_params['num_best_to_take'], generation_data)
		random_results = get_random_selection(
			top_results, generation_data, input_params['num_random_to_take'])
		# update best set of moves
		top_results = update_best_result(
			best_moves, best_distance_score, corresponding_best_time, top_results)
		best_moves = top_results[0][0]
		best_distance_score = top_results[0][1]
		corresponding_best_time = top_results[0][2]

		combined_results, chosen_indices = choose_samples(
			input_params, random_results, top_results)

		if best_distance_score == 10E8:
			# victory achieved
			if input_params['adaptive_algo'][3] == 0:
				input_params['adaptive_algo'][3] = i + input_params['adaptive_algo'][2]
			if i >= input_params['adaptive_algo'][3]:
				victory_status = True
			chosen_indices = [0] * input_params['num_of_particles_per_generation']

	if input_params['pickle_best']:
		parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
		pickle_path = (
			parent_path +
			"/pickles/best_moves_for_particle_{},_track_{}.pickle".format(
				input_params['particle_size'], input_params['track_num']))
		pf.pickle_me(pickle_path, best_moves)


def run_best_moves(input_params, init_params):
	"""Runs through pickled set of moves obtained by 'training' particle; it is
	expected that these moves lead to victory"""
	parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	pickle_path = (
		parent_path +
		"/pickles/best_moves_for_particle_{},_track_{}.pickle".format(
			input_params['particle_size'], input_params['track_num']))
	if os.path.isfile(pickle_path):
		best_moves = pf.get_pickle(pickle_path)
	else:
		raise Exception(
			"""run_best_moves error: specified pickle path does not exist. No training
			has been performed for particle {} on track {}.""".format(
				input_params['particle_size'], input_params['track_num']))
	generation_data = gr.run_one_generation(
		input_params, init_params, [[best_moves, 0, 0, 0]], [0], False)
	print(
		"""Saved set of moves for particle {} on track {} achieved victory \
		in a time of {} seconds.""".format(
			input_params['particle_size'], input_params['track_num'],
			generation_data[0][2]).replace('\t', ''))
