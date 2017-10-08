#!/usr/bin/env python3

import os


class Section:
	"""Stores properties of rectangular sections of track"""

	def __init__(
		self, top_left_point, top_right_point, bottom_left_point,
		bottom_right_point, increasing_x_reward, increasing_y_reward):
		self.top_left_point = top_left_point
		self.top_right_point = top_right_point
		self.bottom_left_point = bottom_left_point
		self.bottom_right_point = bottom_right_point

		# set incentive for particle to move in certain direction, must be
		# between -1 and 1
		self.increasing_x_reward = increasing_x_reward
		self.increasing_y_reward = increasing_y_reward


def retrieve_sections(track_num):
	"""Converts track sections in .section file to Section objects"""
	parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	with open(
		parent_path + '/tracks/track_{}/track_{}_sections.section'.format(
			track_num, track_num), 'r') as f:
		lines = f.readlines()
	sections = []
	current_section_properties = [0] * 6
	current_section_count = 0
	current_item_count = 0
	for line in lines:
		line = line.replace('\n', '')
		if 'section' in line:
			current_section_count += 1
		else:
			if line != '':
				if ',' in line:
					# coordinate value
					line_data = line.split(',')
					line_data = tuple([int(x.replace(' ', '')) for x in line_data])
				else:
					line_data = int(line.replace(' ', ''))
				current_section_properties[current_item_count] = line_data
				current_item_count += 1
				if current_item_count == 6:
					current_item_count = 0
					sections.append(Section(
						current_section_properties[0],
						current_section_properties[1],
						current_section_properties[2],
						current_section_properties[3],
						current_section_properties[4],
						current_section_properties[5]))

	if len(sections) != current_section_count:
		raise Exception(
			"""retrieve_sections error: discrepancy between number of sections counted
			and number of sections objects created.""")
	return sections


def overlap_check(point_value, region_start, region_end):
	"""Checks if point_value is within range starting at region_start and ending
	at region_end (1 dimensional)"""
	if point_value >= region_start and point_value <= region_end:
		return True
	else:
		return False


def section_check(sections):
	"""Checks some basics about the sections, such that no sections overlap and
	section is rectangular, ensuring that section is of expected form"""
	sections_bounds = []  # contains section start and end points in
	# tuple: (x_start, x_end, y_start, y_end)
	for section in sections:
		# First, checks that section is rectangular
		if section.top_left_point[1] != section.top_right_point[1]:
			raise Exception("""section_check error: x coordinates of top-left and
				top-right points of rectangular section are not equal.""")
		if section.bottom_left_point[1] != section.bottom_right_point[1]:
			raise Exception("""section_check error: x coordinates of bottom-left and
				bottom-right points of rectangular section are not equal.""")
		if section.top_left_point[0] != section.bottom_left_point[0]:
			raise Exception("""section_check error: x coordinates of top-left and
				top-right points of rectangular section are not equal.""")
		if section.top_right_point[0] != section.bottom_right_point[0]:
			raise Exception("""section_check error: x coordinates of bottom-left and
				bottom-right points of rectangular section are not equal.""")
		sections_bounds.append((
			section.top_left_point[0],
			section.top_right_point[0],
			section.top_left_point[1],
			section.bottom_left_point[1]))

	for i, j in enumerate(sections_bounds):
		other_section_bounds = [q for q in sections_bounds if q != j]
		for index, other_section_bound in enumerate(other_section_bounds):
			# check for x overlap
			if (
				overlap_check(other_section_bound[0], j[0], j[1]) or
				overlap_check(other_section_bound[1], j[0], j[1])):
				# x overlap true, so checks for y overlap as well
				if (
					overlap_check(other_section_bound[2], j[2], j[3]) or
					overlap_check(other_section_bound[3], j[2], j[3])):
					# overlap in x and y, therefore regions overlap
					raise Exception(
						"section_check error: regions {} and {} overlap".format(i, index))


def get_section(point, sections):
	"""Finds which section given coordinate is in, assuming rectangular
	sections"""
	matching_section = None
	for section in sections:
		if (
			overlap_check(
				point[0], section.top_left_point[0], section.top_right_point[0]) and
			overlap_check(
				point[1], section.top_left_point[1], section.bottom_left_point[1])):
			matching_section = section
			break
	else:
		raise Exception(
			'get_section error: no matching section found for point: {}.'.format(point))
	return matching_section


def delta_sign_handle(delta, current_pos, prev_pos):
	"""Produces a list of coordinates from prev_pos to current_pos"""
	if delta >= 0:
		resulting_range = [i + prev_pos for i in range(delta + 1)]
	else:
		resulting_range = [i + prev_pos for i in range(delta, 1)][::-1]
	# check to make sure current_pos is at start of list
	if resulting_range[0] != prev_pos or resulting_range[-1] != current_pos:
		raise Exception(
			"""delta_sign_handle error: current_pos ({}) and/or prev_pos({}) are not in
			correct place in resulting_range list ({})""".format(
				current_pos, prev_pos, resulting_range))
	return resulting_range


def separate_by_section_identifier(
	coord_type, coord, section_identifier, prev_section, current_section,
	prev_section_dynamic, current_section_dynamic):
	"""Puts coordinate in correct section list"""
	if section_identifier == prev_section.top_left_point:
		prev_section_dynamic.append(coord)
	elif section_identifier == current_section.top_left_point:
		current_section_dynamic.append(coord)
	else:
		raise Exception(
			"""separate_by_section_identifier error: {}_coordinate in new \
			section. It is likely that the particle has moved through 3 sections in a \
			single iteration.""".format(coord_type))
	return prev_section_dynamic, current_section_dynamic


def handle_move_through_boundary(
	coord_type, current_pos, prev_pos, delta_x, delta_y, sections, prev_section,
	current_section):
	"""Takes in 2 positions and returns the resulting score from moving from the
	1st to the 2nd, for case of crossing between 2 sections. Note will not work if
	crossing over 3 sections in one move."""
	# coord_type refers to coordinate that changes
	if coord_type == 'x':
		static_coord = current_pos[1]
	elif coord_type == 'y':
		static_coord = current_pos[0]
	else:
		raise Exception(
			"""handle_move_through_boundary error: coord_type is not 'x' or 'y' and
			therefore is not valid""")

	# separate changing coordinate into 2 lists, split by which region coordinate
	# is in
	prev_section_dynamic, current_section_dynamic = [], []
	if coord_type == 'x':
		x_range = delta_sign_handle(delta_x, current_pos[0], prev_pos[0])
		for dynamic_coord in x_range:
			section_identifier = get_section(
				(dynamic_coord, static_coord), sections).top_left_point
			(
				prev_section_dynamic,
				current_section_dynamic) = separate_by_section_identifier(
				coord_type, dynamic_coord, section_identifier, prev_section,
				current_section, prev_section_dynamic, current_section_dynamic)
	elif coord_type == 'y':
		y_range = delta_sign_handle(delta_y, current_pos[1], prev_pos[1])
		for dynamic_coord in y_range:
			section_identifier = get_section(
				(static_coord, dynamic_coord), sections).top_left_point
			(
				prev_section_dynamic,
				current_section_dynamic) = separate_by_section_identifier(
				coord_type, dynamic_coord, section_identifier, prev_section,
				current_section, prev_section_dynamic, current_section_dynamic)

	# compute change in score based on section properties in relevant section for
	# each coordinate considered
	prev_section_delta = prev_section_dynamic[-1] - prev_section_dynamic[0]
	current_section_delta = (
		current_section_dynamic[-1] - current_section_dynamic[0])
	if coord_type == 'x':
		score_delta = (
			prev_section_delta * prev_section.increasing_x_reward +
			current_section_delta * current_section.increasing_x_reward)
	elif coord_type == 'y':
		score_delta = (
			prev_section_delta * prev_section.increasing_y_reward +
			current_section_delta * current_section.increasing_y_reward)
	return score_delta


def update_distance_score(
	sections, particle, prev_pos, step_size):
	"""Returns updated distance score, with handling for case where particle stays
	in one section and for when it moves between 2 sections"""
	current_pos = (particle.x, particle.y)
	delta_x = current_pos[0] - prev_pos[0]
	delta_y = current_pos[1] - prev_pos[1]
	if delta_x != 0 and delta_y != 0:
		raise Exception(
			"""update_distance_score error: both delta_x and delta_y are non-zero,
			therefore more than one coordinate is changing in a single iteration
			(not as intended)""")
	prev_section = get_section(prev_pos, sections)
	current_section = get_section(current_pos, sections)
	if current_section.top_left_point != prev_section.top_left_point:
		# crossed over border between sections
		if delta_x != 0:
			# i.e. x coordinate changes
			score_delta = handle_move_through_boundary(
				'x', current_pos, prev_pos, delta_x, delta_y, sections, prev_section,
				current_section)
		elif delta_y != 0:
			# i.e. y coordinate changes
			score_delta = handle_move_through_boundary(
				'y', current_pos, prev_pos, delta_x, delta_y, sections, prev_section,
				current_section)
		else:
			raise Exception(
				"""update_distance_score error: both delta_x and delta_y are zero,
				therefore no move is made in iteration; shouldn't be possible.""")
	else:
		# still within same section as previous iteration
		score_delta = (
			delta_x * current_section.increasing_x_reward +
			delta_y * current_section.increasing_y_reward)
	new_score = particle.current_distance_score + score_delta
	return new_score
