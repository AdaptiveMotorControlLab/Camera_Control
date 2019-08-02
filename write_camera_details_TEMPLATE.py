"""
Camera Control
Copyright M. Mathis Lab
Written by  Gary Kane - https://github.com/gkane26
post-doctoral fellow @ the Adaptive Motor Control Lab
https://github.com/AdaptiveMotorControlLab

create json parameter file
"""

import os
import json
import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
out = os.path.normpath(path + '/camera_details.json')

# Crop, rotation, and exposure are default parameters. Can be changed in the GUI.

cam_0 = {'name' : 'Cog Rig',
        'crop' : {'top' : 150, 'left' : 225, 'height' : 250, 'width' : 300},
        'rotate' : 0,
        'exposure' : -14,
        'output_dir' : 'C:/Users/user1/Desktop/video/RIG6_DATA/cog_rig/video'}

cam_1 = {'name' : 'Neuro Rig',
        'crop' : {'top' : 200, 'left' : 140, 'height' : 325, 'width' : 200},
        'rotate' : 90,
        'exposure' : -6,
        'output_dir' : 'C:/Users/user1/Desktop/video/RIG6_DATA/cog_rig/video'}

subs = ['test1', 'test2', 'test3'] # optional, can manually enter subject for each session.

labview = ['Dev1/port0/line0'] # optional, can manually enter for each session

details = {'cams' : 2,
           '0' : cam_0,
           '1' : cam_1,
           'subjects' : subs,
           'labview' : labview}

with open(out, 'w') as handle:
    json.dump(details, handle)
