#!/usr/bin/env python3

import pickle


def pickle_me(p_path, p_obj):
	"""Creates a pickle file"""
	pickle_out = open(p_path, "wb")
	pickle.dump(p_obj, pickle_out)
	pickle_out.close()


def get_pickle(p_path):
	"""Retrieves a pickled object from file"""
	pickle_in = open(p_path, "rb")
	obj = pickle.load(pickle_in)
	pickle_in.close()
	return obj
