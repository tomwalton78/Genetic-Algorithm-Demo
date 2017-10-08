#!/usr/bin/env python3

import os
import cv2
import pygame
import modules.initialisation as init
import modules.colour_store as cs

track_num = 1


def get_track_dimensions(track_num, path):
	"""Obtain track width and height"""
	track_img = pygame.image.load(
		path + '/tracks/track_{}/track_{}_full.png'.format(track_num, track_num))
	display_width, display_height = (
		track_img.get_rect().size[0], track_img.get_rect().size[1])
	return display_width, display_height


def get_img_filtered_by_colour(track_num, colour):
	"""Returns matrix of pixels that represent image, with values of True if
	pixel matches specified colour, False otherwise"""
	current_path = os.path.dirname(__file__)
	img = cv2.imread(
		current_path + '/tracks/track_{}/track_{}_full.png'.format(
			track_num, track_num))
	img_to_list = img.tolist()
	display_width, display_height = get_track_dimensions(track_num, current_path)
	track_matrix = (
		[[False for j in range(display_height)] for i in range(display_width)])
	# index items by track_matrix[x][y]
	for i, j in enumerate(img_to_list):
		for k, l in enumerate(j):
			if str(colour) in str(tuple(l)):
				track_matrix[k][i] = True
	return track_matrix


def validate_point(filtered_track, point):
	"""Check that point is on track (cs.grey colour)"""
	if filtered_track[point[0]][point[1]]:
		return point
	else:
		return None


def get_section_direction(section_bounds):
	"""From 3/4 section bounds, determine section direction from one remaining
	None value section bound"""
	if section_bounds.count(None) > 1:
		raise Exception('Not all section_bounds identified correctly!')
	for i, bound in enumerate(section_bounds):
		if bound is None:
			return i


def get_section_bounds_and_direction(filtered_track, start_pos, add_values):
	"""Obtain initial 1st 3 section bounds, and direction of section, defined to
	be the 1 of 4 directions that is furthest from start_pos"""
	section_bounds = [None for i in range(4)]
	current_pos = [start_pos for i in range(4)]
	# 0 index: left path, 1: right path, 2: top path, 3: bottom path
	bounds_found = 0
	while bounds_found < 3:
		next_points = []
		for i, j in enumerate(current_pos):
			if current_pos[i] is not None:
				next_point = (
					j[0] + add_values[i][0], j[1] + add_values[i][1])
				validated_point = validate_point(filtered_track, next_point)
				next_points.append(validated_point)
				if validated_point is None:
					section_bounds[i] = current_pos[i]
					bounds_found += 1
			else:
				next_points.append(None)
		current_pos = next_points
	direction_index = get_section_direction(section_bounds)
	return section_bounds, direction_index


def victory_box_present(points, victory_box):
	"""Checks if point lies in victory_box"""
	for point in points:
		if victory_box[point[0]][point[1]]:
			return True
	else:
		return False


def get_last_boundary(
	filtered_track, section_bounds, direction_index, add_values, victory_box):
	"""Obtain final section bound by moving along the edges, in the direction of
	the section, with the end of the section found when edge of section
	disappears, signalling start of next section"""
	look_directions = [
		[(0, -1), (0, 1)], [(0, -1), (0, 1)], [(-1, 0), (1, 0)], [(-1, 0), (1, 0)]]
	boundary_crawler_options = [
		[section_bounds[2], section_bounds[3]],
		[section_bounds[2], section_bounds[3]],
		[section_bounds[0], section_bounds[1]],
		[section_bounds[0], section_bounds[1]]]

	boundary_there = True
	boundary_crawlers = boundary_crawler_options[direction_index]
	while boundary_there:
		next_points = [(
			point[0] + add_values[direction_index][0], point[1] +
			add_values[direction_index][1]) for point in boundary_crawlers]
		if not victory_box_present(next_points, victory_box):
			look_points = [(
				point[0] + look_directions[direction_index][i][0],
				point[1] + look_directions[direction_index][i][1]) for
				i, point in enumerate(next_points)]
			for i, lp in enumerate(look_points):
				if validate_point(filtered_track, lp) is not None:
					boundary_there = False
					section_bounds[direction_index] = boundary_crawlers[i]
					next_section_direction = look_directions[direction_index][i]
					last_point = lp
			if boundary_there:
				boundary_crawlers = next_points
		else:
			# hit victory box
			boundary_there = False
			section_bounds[direction_index] = boundary_crawlers[0]
			last_point = None
			next_section_direction = None
	return section_bounds, next_section_direction, last_point


def get_section_info(section_bounds, direction_index):
	"""Turns section_bounds list into coordinates of 4 section corners and the
	rewards in x and y directions"""
	rewards = [(-1, 0), (1, 0), (0, -1), (0, 1)]
	top_left_point = (section_bounds[0][0], section_bounds[2][1])
	top_right_point = (section_bounds[1][0], section_bounds[2][1])
	bottom_left_point = (section_bounds[0][0], section_bounds[3][1])
	bottom_right_point = (section_bounds[1][0], section_bounds[3][1])
	increasing_x_reward = rewards[direction_index][0]
	increasing_y_reward = rewards[direction_index][1]
	return (
		top_left_point, top_right_point, bottom_left_point, bottom_right_point,
		increasing_x_reward, increasing_y_reward)


def get_next_starting_pos(
	direction_index, add_values, next_section_direction, filtered_track,
	last_point):
	"""Find starting point that is within, and near to beginning of, next
	section"""
	if last_point is None:
		return None
	else:
		next_starting_pos = (
			last_point[0] + add_values[direction_index][0] + next_section_direction[0],
			last_point[1] + add_values[direction_index][1] + next_section_direction[1])
		validated_point = validate_point(filtered_track, next_starting_pos)
		return validated_point


def explore_section(filtered_track, start_pos, victory_box):
	"""Explore section by finding the edges of the section, finding its direction,
	and finding a point in the next section to start from"""
	add_values = [(-1, 0), (1, 0), (0, -1), (0, 1)]
	section_bounds, direction_index = get_section_bounds_and_direction(
		filtered_track, start_pos, add_values)

	section_bounds, next_section_direction, last_point = get_last_boundary(
		filtered_track, section_bounds, direction_index, add_values, victory_box)

	section_details = get_section_info(section_bounds, direction_index)

	next_starting_pos = get_next_starting_pos(
		direction_index, add_values, next_section_direction, filtered_track,
		last_point)

	return section_details, next_starting_pos


def explore_all_sections(filtered_track, start_pos, victory_box):
	"""Run through explore_section for all sections in track"""
	next_starting_pos = start_pos
	all_sections = []
	while next_starting_pos is not None:
		section_details, next_starting_pos = explore_section(
			filtered_track, next_starting_pos, victory_box)
		all_sections.append(section_details)
	return all_sections


def sections_to_lines(sections):
	"""Convert list of sections to lines that will be written to .section file"""
	lines = []
	for i, section in enumerate(sections):
		lines.append('section_{}'.format(i + 1) + '\n')
		for j, item in enumerate(section):
			if j < 4:
				lines.append(str(item).replace('(', '').replace(')', '') + '\n')
			else:
				lines.append(str(item) + '\n')
		lines.append('\n')
	return lines


def write_sections_to_file(track_num, sections):
	"""Take sections and write them to file, in particular format"""
	current_path = os.path.dirname(__file__)
	lines = sections_to_lines(sections)

	with open(
		current_path + '/tracks/track_{}/track_{}_sections.section'.format(
			track_num, track_num), 'w') as f:
		for line in lines:
			f.write(line)


filtered_track = get_img_filtered_by_colour(track_num, cs.grey)
victory_box = get_img_filtered_by_colour(track_num, cs.vb_red)
starting_pos = init.get_starting_pos(
	track_num, cs.green, os.path.dirname(__file__))

all_sections = explore_all_sections(filtered_track, starting_pos, victory_box)

write_sections_to_file(track_num, all_sections)
