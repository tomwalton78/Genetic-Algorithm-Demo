import cv2
import colour_store as cs
import os

track_num = 1

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
img = cv2.imread(
	parent_path + '/tracks/track_{}/track_{}_full.png'.format(
		track_num, track_num))
img_to_list = img.tolist()
colour_dict = {}
for i, j in enumerate(img_to_list):
	for k, l in enumerate(j):
		if str(l) not in colour_dict.keys():
			colour_dict[str(l)] = 1
		else:
			colour_dict[str(l)] += 1

print(colour_dict)