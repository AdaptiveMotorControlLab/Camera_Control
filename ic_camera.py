"""
Camera Control
Copyright M. Mathis Lab
Written by  Gary Kane - https://github.com/gkane26
post-doctoral fellow @ the Adaptive Motor Control Lab
https://github.com/AdaptiveMotorControlLab

camera class for imaging source cameras - helps load correct settings
"""

import tisgrabber as ic
import numpy as np
import os
import json
import cv2
import ctypes as C

path = os.path.dirname(os.path.realpath(__file__))
dets_file = os.path.normpath(path + '/camera_details.json')
cam_details = json.load(open(dets_file, 'r'))

class ICCam(object):

    def __init__(self, cam_num=0, rotate=None, crop=None, exposure=None):
        '''
        Params
        ------
        cam_num = int; camera number (int)
            default = 0
        crop = dict; contains ints named top, left, height, width for cropping
            default = None, uses default parameters specific to camera
        '''

        self.cam_num = cam_num
        self.rotate = rotate if rotate is not None else cam_details[str(self.cam_num)]['rotate']
        self.crop = crop if crop is not None else cam_details[str(self.cam_num)]['crop']
        self.exposure = exposure if exposure is not None else cam_details[str(self.cam_num)]['exposure']

        self.cam = ic.TIS_CAM()
        self.cam.open(self.cam.GetDevices()[cam_num].decode())
        self.add_filters()

    def add_filters(self):
        if self.rotate != 0:
            h_r = self.cam.CreateFrameFilter(b'Rotate Flip')
            self.cam.AddFrameFilter(h_r)
            self.cam.FilterSetParameter(h_r, 'Rotation Angle', self.rotate)

        h_c = self.cam.CreateFrameFilter(b'ROI')
        self.cam.AddFrameFilter(h_c)
        self.cam.FilterSetParameter(h_c, b'Top', self.crop['top'])
        self.cam.FilterSetParameter(h_c, b'Left', self.crop['left'])
        self.cam.FilterSetParameter(h_c, b'Height', self.crop['height'])
        self.cam.FilterSetParameter(h_c, b'Width', self.crop['width'])
        self.size = (self.crop['width'], self.crop['height'])

    def set_frame_rate(self, fps):
        self.cam.SetFrameRate(fps)

    def set_exposure(self, val):
        val = 1 if val > 1 else val
        val = 0 if val < 0 else val
        self.cam.SetPropertyAbsoluteValue("Exposure", "Value", val)

    def get_exposure(self):
        exposure = [0]
        self.cam.GetPropertyAbsoluteValue("Exposure", "Value", exposure)
        return round(exposure[0], 3)

    def get_image(self):
        self.cam.SnapImage()
        frame = self.cam.GetImageEx()
        return cv2.flip(frame,0)

    def get_image_dimensions(self):
        im = self.get_image()
        height = im.shape[0]
        width = im.shape[1]
        return (width, height)

    def start(self, show_display=1):
        self.cam.SetContinuousMode(0)
        self.cam.StartLive(show_display)

    def close(self):
        self.cam.StopLive()
