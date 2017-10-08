#!/usr/bin/env python3

import os
import copy
from time import time
import modules.pickle_funcs as pf
from modules.particle import Particle
import modules.colour_store as cs
import modules.initialisation as init
import modules.distance_handling as dh
import modules.generation_run as gr
import modules.run_modes as rm

# Begin tests on pickle_funcs module


def pickle_funcs_tests():
	"""Pickles an object and checks that retrieved object is same as original
	object"""
	pickle_obj = 'This is a string.'
	pickle_path = 'string.pickle'
	pf.pickle_me(pickle_path, pickle_obj)
	retrieved_obj = pf.get_pickle(pickle_path)
	if retrieved_obj != pickle_obj:
		print('pickle_funcs error: original object and pickled object do not match.')
	os.remove(pickle_path)


# Begin tests on particle module


def particle_tests():
	"""Checks that Particle object is created correctly, and its position updates
	correctly."""
	particle_size = 10
	starting_pos = (5, 5)
	p = Particle(particle_size, starting_pos)
	if p.x != 5 or p.y != 5:
		print('particle error: particle positon is not being set properly')
	# check update_position works as intended
	p.update_position((5, 10))
	if p.x != 10 or p.y != 15:
		print("particle error: particle's position is not being updated correctly")


# Begin tests on initialisation module


def test_get_starting_pos():
	path = os.path.dirname(__file__)
	starting_pos = init.get_starting_pos(0, cs.green, path)
	if starting_pos != (34, 514):
		print(
			"""initialisation_tests error: starting pos determined incorrectly. \
			get_starting_pos function returned {}, \
			but should have returned {}.""".format(
				starting_pos, (34, 514)).replace('\n', ''))


def test_initialise_setup():
	input_params = {'particle_size': 10, 'track_num': 0}
	(
		track_img, particle_width, particle_height, display_width, display_height,
		particle_mask, track_mask, victory_box_mask, possible_moves, starting_pos,
		sections) = init.initialise_setup(input_params)
	if particle_width != 10 or particle_height != 10:
		print(
			"""initialise_setup error: incorrect particle being imported or particle \
			dimensions not being determined correctly. Program thinks particle height \
			is {} and width is {} pixels.""".format(
				particle_height, particle_width).replace('\n', ''))
	if display_width != 800 or display_height != 600:
		print(
			"""initialise_setup error: display dimensions not being determined \
			correctly or wrong track being loaded. Program thinks display_height is{} \
			and display_width is {} pixels.""".format(
				display_height, display_width).replace('\n', ''))


def initialisation_tests():
	"""Tests that initialisation module retrieves starting position correctly and
	other initial parameters and settings"""
	# test that correct start_position is retrieved
	test_get_starting_pos()
	# test that initialise_setup function produced correct results
	test_initialise_setup()


# Begin tests on distance_handling module


def test_retrieve_sections():
	sections = dh.retrieve_sections(0)
	section_rewards = [(1, 0), (0, -1), (-1, 0)]
	section_top_lefts = [(26, 479), (639, 105), (76, 18)]
	section_top_rights = [(638, 479), (778, 105), (778, 18)]
	section_bottom_lefts = [(26, 569), (639, 569), (76, 104)]
	section_bottom_rights = [(638, 569), (778, 569), (778, 104)]
	for i, section in enumerate(sections):
		if section.top_left_point != section_top_lefts[i]:
			print(
				"""retrieve_sections error: top-left point not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
		if section.top_right_point != section_top_rights[i]:
			print(
				"""retrieve_sections error: top-right point not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
		if section.bottom_left_point != section_bottom_lefts[i]:
			print(
				"""retrieve_sections error: bottom-left point not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
		if section.bottom_right_point != section_bottom_rights[i]:
			print(
				"""retrieve_sections error: bottom_right point not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
		if section.increasing_x_reward != section_rewards[i][0]:
			print(
				"""retrieve_sections error: increasing_x_reward not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
		if section.increasing_y_reward != section_rewards[i][1]:
			print(
				"""retrieve_sections error: increasing_y_reward not being retrieved correctly \
				in section {}.""".format(i).replace('\t', ''))
	return sections


def test_overlap_check():
	if dh.overlap_check(5, 10, 15):
		print(
			'overlap_check error: stated that there was an overlap, when there was not')
	if not dh.overlap_check(10, 5, 15):
		print(
			'overlap_check error: stated that there was not an overlap, when there was')


def test_section_check(sections):
	sections_copy = [copy.copy(section) for section in sections]
	# first test that it works on a correct section
	dh.section_check(sections_copy)
	# now repeat test on a faulty section
	faulty_section = sections_copy[1]
	faulty_section.top_left_point = (39, 41)
	faulty_section.increasing_x_reward = 1
	try:
		dh.section_check(sections_copy)
		print('section_check error: faulty sections were not identified')
	except Exception as e:
		if str(e)[0: 19] != 'section_check error':
			print('section_check error: unanticipated exception raised: {}'.format(
				str(e)))


def test_get_section(sections):
	# first try on valid point
	matched_section = dh.get_section((300, 500), sections)
	if (
		matched_section.top_left_point != (26, 479) or
		matched_section.bottom_right_point != (638, 569)):
		print(
			'get_section error: point  matched to incorrect section')
	# next try on point that is not in a section
	try:
		dh.get_section((10, 10), sections)
		print("""get_section error: point that was not in a section was \
			incorrectly matched to a section""".replace('\t', ''))
	except Exception as e:
		if str(e)[0: 17] != 'get_section error':
			print('get_section error: unanticipated exception raised: {}'.format(
				str(e)))


def test_delta_sign_handle():
	# positive delta case
	resulting_range = dh.delta_sign_handle(5, 10, 5)
	if resulting_range != [5, 6, 7, 8, 9, 10]:
		print(
			'delta_sign_handle error: incorrect list produced for positive delta case')
	# negaitve delta case
	resulting_range = dh.delta_sign_handle(-5, 5, 10)
	if resulting_range != [10, 9, 8, 7, 6, 5]:
		print(
			'delta_sign_handle error: incorrect list produced for negative delta case')


def test_separate_by_section_identifier(sections):
	(
		prev_section_dynamic,
		current_section_dynamic) = dh.separate_by_section_identifier(
		'x', (635, 506), (26, 479), sections[0], sections[1], [], [])
	(
		prev_section_dynamic,
		current_section_dynamic) = dh.separate_by_section_identifier(
		'x', (641, 498), (639, 105), sections[0], sections[1], prev_section_dynamic, 
		current_section_dynamic)
	if (
		prev_section_dynamic[0] != (635, 506) or
		current_section_dynamic[0] != (641, 498)):
		print(
			"""separate_by_section_identifier error: points {} and {} were put into the \
			wrong sections""".format((635, 506), (641, 498)).replace('\t', ''))


def test_handle_move_through_boundary(sections):
	score = dh.handle_move_through_boundary(
		'x', (641, 486), (636, 486), 5, 0, sections, sections[0], sections[1])
	if score != 2:
		print(
			"""handle_move_through_boundary error: scoring incorrect for positive \
			delta_x""".replace('\t', ''))
	score = dh.handle_move_through_boundary(
		'x', (636, 486), (641, 486), -5, 0, sections, sections[1], sections[0])
	if score != -2:
		print(
			"""handle_move_through_boundary error: scoring incorrect for negative \
			delta_x""".replace('\t', ''))
	score = dh.handle_move_through_boundary(
		'y', (653, 101), (653, 108), 0, -7, sections, sections[1], sections[2])
	if score != 3:
		print(
			"""handle_move_through_boundary error: scoring incorrect for negative \
			delta_y""".replace('\t', ''))
	score = dh.handle_move_through_boundary(
		'y', (653, 108), (653, 101), 0, 7, sections, sections[2], sections[1])
	if score != -3:
		print(
			"""handle_move_through_boundary error: scoring incorrect for positive \
			delta_y""".replace('\t', ''))


def test_update_distance_score(sections):
	p = Particle(10, (5, 5))
	p.update_position((539, 492))
	# staying within one section
	new_score = dh.update_distance_score(sections, p, (534, 497), 10)
	if new_score != 10:
		print('update_distance_score error: incorrect score calculated')
	# crossing sections
	p.x, p.y = 645, 500
	new_score = dh.update_distance_score(sections, p, (635, 500), 10)
	if new_score != 3:
		if new_score != 10:
			print('update_distance_score error: incorrect score calculated')


def distance_handling_tests():
	# test that sections are retrieved correctly
	sections = test_retrieve_sections()
	# test that overlap_check correctly identifies when sections are overlapping
	test_overlap_check()
	# test that sections are correctly checks by section check
	test_section_check(sections)
	# tests that correct section is matched to certain points
	test_get_section(sections)
	# tests that delta_sign_handle produces correct range form inputted values
	test_delta_sign_handle()
	# tests that separate_by+section_identifier correctly separates points into
	# appropriate sections
	test_separate_by_section_identifier(sections)
	# tests that handle_move_through_boundary correctly scores particle moving
	# between 2 sections
	test_handle_move_through_boundary(sections)
	# tests that update_distance_score gives correct score
	test_update_distance_score(sections)


# Begin tests on generation_run module


def test_collision_check(init_params):
	if not gr.collision_check(
		init_params['track_mask'], init_params['particle_mask'], 225, 470):
		print(
			'collision_check error: collision not detected when it should have been')
	if gr.collision_check(
		init_params['track_mask'], init_params['particle_mask'], 253, 498):
		print(
			'collision_check error: collision detected when it should not have been')


def test_mutate_moves():
	original_moves = [['up', 'down', 'left', 'right',] for i in range(100)]
	input_params = {
		'mutate_moves_mapping_func_type': 'exp',
		'mutation_chance_options': [1000],
		'adaptive_algo': (False, 0, 0, 0)}
	new_moves = gr.mutate_moves(
		original_moves, input_params, ['up', 'left', 'right', 'down'], False)
	if new_moves == original_moves:
		print(
			"""mutate_moves error: resulting list from mutate_moves is same as \
			input list. It is likely that function is not working properly.""".replace(
				'\t', ''))


def test_some_alive_check():
	particles = [Particle(10, (5, 5)) for i in range(5)]
	# test for 1 dead particle
	particles[2].alive = False
	if not gr.some_alive_check(particles):
		print(
			"""some_alive_check error: particles alive yet all are being reported \
			as dead""".replace('\t', ''))
	for p in particles:
		p.alive = False
	if gr. some_alive_check(particles):
		print(
			"""some_alive_check error: particles all dead yet it is reported that some \
			are alive""".replace('\t', ''))


def test_choose_move():
	p = Particle(10, (5, 5))
	p.best_moves_mutated = ['left', 'right', 'up']
	possible_moves = ['right', 'up', 'down', 'left']
	# picking existing move
	move = gr.choose_move(1, possible_moves, p)
	if move != 'right':
		print('choose_move error: picked incorrect move from best_moves_mutated')
	try:
		move = gr.choose_move(10, possible_moves, p)
	except Exception as e:
		print('choose_move error: failed to pick random move, with error: {}'.format(
			str(e)))


def test_act_on_move():
	# changing y coordinate
	x_change, y_change = gr.act_on_move('up', 5)
	if x_change != 0 or y_change != -5:
		print(
			"""act_on_move error: wrong moves made. Gave an x_change of {}, a y_change \
			of {}. Should have produced x_change of 0, y_change of -5""".format(
				x_change, y_change).replace('\t', ''))
	# changing x coordinatew
	x_change, y_change = gr.act_on_move('right', 3)
	if x_change != 3 or y_change != 0:
		print(
			"""act_on_move error: wrong moves made. Gave an x_change of {}, a y_change \
			of {} Should have produced x_change of 3, y_change of 0""".format(
				x_change, y_change).replace('\t', ''))


def test_check_for_collisions(init_params):
	start_time = time()
	# expect collision with boundary
	p = Particle(20, (110, 100))
	gr.check_for_collisions(init_params, p, 5, start_time)
	if p.alive:
		print(
			"""check_for_collisions error: particle should be dead after hitting wall, \
			but isn't""".replace('\t', ''))
	# resurrect particle and expect collision with victory box
	p.alive = True
	p.x, p.y = 32, 60
	gr.check_for_collisions(init_params, p, 5, start_time)
	if p.alive:
		print(
			"""check_for_collisions error: particle should be dead after hitting \
			victory box, but isn't""".replace('\t', ''))
	# resurrect particle and expect it to not collide with anything
	p.alive = True
	p.x, p.y = 264, 35
	gr.check_for_collisions(init_params, p, 5, start_time)
	if not p.alive:
		print(
			"check_for_collisions error: particle should be alive, but isn't.".replace(
				'\t', ''))


def test_check_particle_in_bounds(init_params):
	p = Particle(20, (1000, 1000))
	# expect particle to be out of bounds, so game_exit should be True
	if not gr.check_particle_in_bounds(p, init_params, True, testing=True):
		print("""check_particle_in_bounds error: particle determined to be in bounds, \
			when it is not""".replace('\t', ''))
	# expect particle to be in bounds, so game_exit should be False
	p.x, p.y = 300, 300
	if gr.check_particle_in_bounds(p, init_params, False, testing=True):
		print("""check_particle_in_bounds error: particle determined to be out of bounds, \
			when it is not""".replace('\t', ''))


def test_evaluate_performance():
	p = Particle(20, (50, 50))
	p.moves_made = ['up', 'right', 'down', 'right', 'left']
	p.distance_time_record = (10, 3, 0.3)
	return_list = gr.evaluate_performance([p])
	if (
		return_list[0][0] != ['up', 'right', 'down', 'right'] or
		return_list[0][1] != 10 or
		return_list[0][2] != 0.3):
		print('evaluate_performance error: incorrect return_list returned')


def generation_run_tests():
	input_params = {'particle_size': 20, 'track_num': 0}
	(
		track_img, particle_width, particle_height, display_width, display_height,
		particle_mask, track_mask, victory_box_mask, possible_moves, starting_pos,
		sections) = init.initialise_setup(input_params)
	init_params = {
		'track_mask': track_mask,
		'particle_mask': particle_mask,
		'victory_box_mask': victory_box_mask,
		'particle_width': particle_width,
		'particle_height': particle_height,
		'display_width': display_width,
		'display_height': display_height,
	}
	# tests that collisions are being detected correctly by collision_check
	test_collision_check(init_params)
	# tests that mutate moves does indeed change the moves
	test_mutate_moves()
	# tests that some_alive_check correctly determines when some particles are
	# alive, and when all are dead
	test_some_alive_check()
	# tests that choose_move function works as intended
	test_choose_move()
	# tests that act_on_move makes correct changes to x and y
	test_act_on_move()
	# tests that collisions are detected properly for
	test_check_for_collisions(init_params)
	# tests that check_particle_in_bounds acts correctly
	test_check_particle_in_bounds(init_params)
	# checks that evaluate_performance outputs expected result
	test_evaluate_performance()


# Begin tests on run_modes module

def test_get_top_results(generation_data):
	top_results = rm.get_top_results(2, generation_data)
	if (
		top_results[0][0] != ['down', 'right', 'right'] or
		top_results[1][0] != ['down', 'left', 'right']):
		print('get_top_results error: incorrect ordering produced')
	return top_results


def test_update_best_result(top_results):
	best_moves, best_distance_score, corresponding_best_time = (
		['right', 'right', 'right'], 200, 20)
	updated_top_results = rm.update_best_result(
		best_moves, best_distance_score, corresponding_best_time, top_results,
		testing=True)
	if updated_top_results[0][0] != ['right', 'right', 'right']:
		print('update_best_result error: best result not put to top of top_results')


def test_get_random_selection(generation_data, top_results):
	random_selection = rm.get_random_selection(top_results, generation_data, 1)
	if random_selection[0] != [['up', 'down', 'right'], 50, 10, 0]:
		print(
			"""get_random_selection error: incorrect set of data selected. It is likely \
			that this will result in duplicate selections combined_results, skewing \
			the intended distribution of data passed to the next generation""".replace(
				'\t', ''))
	return random_selection


def test_choose_samples(top_results, random_results):
	input_params = {
		'num_best_to_take': 2,
		'chance_of_picking_random_sample': 20,
		'num_of_particles_per_generation': 100}
	combined_results, chosen_indices = rm.choose_samples(
		input_params, random_results, top_results)
	if (
		len(chosen_indices) != input_params['num_of_particles_per_generation'] or
		len(combined_results) != 3 or
		combined_results[0][0] != ['down', 'right', 'right']):
		print('choose_samples error: samples are not being selected properly')


def run_modes_tests():
	generation_data = [
		(['up', 'down', 'right'], 50, 10),
		(['down', 'right', 'right'], 100, 15),
		(['down', 'left', 'right'], 50, 5)]
	# ensures that get_top_results correctly ranks its input data
	top_results = test_get_top_results(generation_data)
	# ensures that best moves become top result if they are still the best
	test_update_best_result(top_results)
	# ensures that get_random_selection works as intended
	random_selection = test_get_random_selection(generation_data, top_results)
	# ensures that samples to be passed to next generation are chosen correctly
	test_choose_samples(top_results, random_selection)


if __name__ == '__main__':
	print('All tests completed successfully if no more print statements appear.\n')
	pickle_funcs_tests()
	particle_tests()
	initialisation_tests()
	distance_handling_tests()
	generation_run_tests()
	run_modes_tests()
