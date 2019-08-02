"""
Camera Control
Copyright M. Mathis Lab
Written by  Gary Kane - https://github.com/gkane26
post-doctoral fellow @ the Adaptive Motor Control Lab
https://github.com/AdaptiveMotorControlLab

GUI to record from imaging source cameras during experiments
"""

from Tkinter import Entry, Label, Button, StringVar, IntVar, Tk, END, Radiobutton
import tkFileDialog
import ttk
import numpy as np
import datetime
import os
from ic_camera import ICCam
import time
import cv2
import ffmpy
import threading
import json
import nidaqmx
import write_camera_details

class CamGUI(object):

    def __init__(self):

        path = os.path.dirname(os.path.realpath(__file__))
        dets_file = os.path.normpath(path + '/camera_details.json')
        with open(dets_file) as f:
            self.cam_details = json.load(f)
        self.mouse_list = self.cam_details['subjects'] if 'subjects' in self.cam_details else []
        self.labview_channel_list = self.cam_details['labview'] if 'labview' in self.cam_details else []
        self.cam_names = ()
        self.output_dir = ()
        for i in range(self.cam_details['cams']):
            self.cam_names = self.cam_names + (self.cam_details[str(i)]['name'],)
            self.output_dir = self.output_dir + (self.cam_details[str(i)]['output_dir'],)

        self.window = None
        self.selectCams()

    def browse_output(self):
        filepath = tkFileDialog.askdirectory()
        self.output.set(filepath)

    def init_cam(self, num):
        # create pop up window during setup
        setup_window = Tk()
        Label(setup_window, text="Setting up camera, please wait...").pack()
        setup_window.update()

        if self.record_on.get():
            setup_window.destroy()
            cam_on_window = Tk()
            Label(cam_on_window, text="Video is recording, cannot reinitialize camera!").pack()
            Button(cam_on_window, text="Ok", command=lambda:cam_on_window.quit()).pack()
            cam_on_window.mainloop()
            cam_on_window.destroy()
            return

        if len(self.cam) >= num+1:
            self.cam[num].close()
            self.cam[num] = None

        # create camera object
        cam_num = self.camera[num].get()
        names = np.array(self.cam_names)
        cam_num = np.where(names == cam_num)[0][0]
        if len(self.cam) >= num+1:
            self.cam_name[num] = names[cam_num]
            self.cam[num] = ICCam(cam_num)
        else:
            self.cam_name.append(names[cam_num])
            self.cam.append(ICCam(cam_num))
        self.cam[num].start()
        self.exposure[num].set(self.cam[num].get_exposure())

        # reset output directory
        self.output.set(self.output_entry['values'][cam_num])

        setup_window.destroy()

    def set_exposure(self, num):
        # check if camera set up
        if len(self.cam) < num+1:
            cam_check_window = Tk()
            Label(cam_check_window, text="No camera is found! \nPlease initialize camera before setting exposure.").pack()
            Button(cam_check_window, text="Ok", command=lambda:cam_check_window.quit()).pack()
            cam_check_window.mainloop()
            cam_check_window.destroy()
        else:
            self.cam[num].set_exposure(int(self.exposure[num].get()))

    def lv_interrupt(self, task_handle, signal_type, callback_data):

        try:
            return_code = 0
            if self.record_on.get():
                self.lv_ts.append(time.time())
                print("\nRecording timestamp %d" % len(self.lv_ts))
        except Exception as e:
            print(e)
            return_code = 1
        finally:
            return return_code

    def init_labview(self):

        if self.lv_task is None:

            lv_chan = self.labview_channel.get()
            if lv_chan != "":
                self.lv_task = nidaqmx.Task("read_behavior_ttl")
                self.lv_task.di_channels.add_di_chan(lv_chan)
                self.lv_task.timing.cfg_change_detection_timing(rising_edge_chan=lv_chan)
                self.lv_task.register_signal_event(nidaqmx.constants.Signal.CHANGE_DETECTION_EVENT, self.lv_interrupt)
                self.lv_task.start()
                Label(self.window, text="Recording Timestamps!").grid(row=3*(int(self.number_of_cams.get())), column=2, sticky="w")
            else:
                no_labview_window = Tk()
                Label(no_labview_window, text="No labview channel selected, please select one before initializing").pack()
                Button(no_labview_window, text="Ok", command=lambda:no_labview_window.quit()).pack()
                no_labview_window.mainloop()
                no_labview_window.destroy()
        else:
            no_labview_window = Tk()
            Label(no_labview_window, text="Labview task already started, please end this task before beginning a new one").pack()
            Button(no_labview_window, text="Ok", command=lambda:no_labview_window.quit()).pack()
            no_labview_window.mainloop()
            no_labview_window.destroy()

    def end_labview(self):
        if self.lv_task is not None:
            #self.lv_task.stop()
            self.lv_task.close()
            self.lv_task = None
            Label(self.window, text="").grid(row=3, column=2, sticky="nsew")

    def set_up_vid(self):

        if len(self.vid_out) > 0:
            vid_open_window = Tk()
            Label(vid_open_window, text="Video is currently open! \nPlease release the current video (click 'Save Video', even if no frames have been recorded) before setting up a new one.").pack()
            Button(vid_open_window, text="Ok", command=lambda:vid_open_window.quit()).pack()
            vid_open_window.mainloop()
            vid_open_window.destroy()
            return

        # check if camera set up
        if len(self.cam) == 0:
            cam_check_window = Tk()
            Label(cam_check_window, text="No camera is found! \nPlease initialize camera before setting up video.").pack()
            Button(cam_check_window, text="Ok", command=lambda:cam_check_window.quit()).pack()
            cam_check_window.mainloop()
            cam_check_window.destroy()
        else:

            month = datetime.datetime.now().month
            month = str(month) if month >= 10 else '0'+str(month)
            day = datetime.datetime.now().day
            day = str(day) if day >= 10 else '0'+str(day)
            year = str(datetime.datetime.now().year)
            date = year+'-'+month+'-'+day
            self.out_dir = self.output.get()
            if not os.path.isdir(os.path.normpath(self.out_dir)):
                os.makedirs(os.path.normpath(self.out_dir))

            # create output file names
            self.vid_file = []
            self.base_name = []
            self.ts_file = []
            cam_name_nospace = []
            this_row = 3
            for i in range(len(self.cam)):
                cam_name_nospace.append(self.cam_name[i].replace(' ', ''))
                self.base_name.append(cam_name_nospace[i] + '_' + self.subject.get() + '_' + date + '_')
                self.vid_file.append(os.path.normpath(self.out_dir + '/' + self.base_name[i] + self.attempt.get() + '.avi'))

                # check if file exists, ask to overwrite or change attempt number if it does
                if i==0:
                    self.overwrite = False
                    if os.path.isfile(self.vid_file[i]):
                        self.ask_overwrite = Tk()
                        def quit_overwrite(ow):
                            self.overwrite=ow
                            self.ask_overwrite.quit()
                        Label(self.ask_overwrite, text="File already exists with attempt number = " + self.attempt.get() + ".\nWould you like to overwrite the file? ").pack()
                        Button(self.ask_overwrite, text="Overwrite", command=lambda:quit_overwrite(True)).pack()
                        Button(self.ask_overwrite, text="Cancel & pick new attempt number", command=lambda:quit_overwrite(False)).pack()
                        self.ask_overwrite.mainloop()
                        self.ask_overwrite.destroy()

                        if self.overwrite:
                            self.vid_file[i] = os.path.normpath(self.out_dir +'/' + self.base_name[i] + self.attempt.get() + '.avi')
                        else:
                            return
                else:
                    self.vid_file[i] = self.vid_file[0].replace(cam_name_nospace[0], cam_name_nospace[i])

                self.ts_file.append(self.vid_file[i].replace('.avi', '.npy'))
                self.ts_file[i] = self.ts_file[i].replace(cam_name_nospace[i], 'TIMESTAMPS_'+cam_name_nospace[i])

                self.current_file_label['text'] = self.subject.get() + '_' + date + '_' + self.attempt.get()

                # create video writer
                dim = self.cam[i].get_image_dimensions()
                if len(self.vid_out) >= i+1:
                    self.vid_out[i] = cv2.VideoWriter(self.vid_file[i], cv2.VideoWriter_fourcc(*'DIVX'), int(self.fps.get()), dim)
                else:
                    self.vid_out.append(cv2.VideoWriter(self.vid_file[i], cv2.VideoWriter_fourcc(*'DIVX'), int(self.fps.get()), dim))

                if self.lv_task is not None:
                    self.lv_file = self.ts_file[0].replace('TIMESTAMPS_'+cam_name_nospace[0], 'LABVIEW')

                # create video writer
                self.frame_times = []
                for i in self.ts_file:
                    self.frame_times.append([])
                self.lv_ts = []
                self.setup = True

    def record_on_thread(self, num):
        fps = int(self.fps.get())
        start_time = time.time()
        next_frame = start_time

        try:
            while self.record_on.get():
                if time.time() >= next_frame:
                    self.frame_times[num].append(time.time())
                    self.vid_out[num].write(self.cam[num].get_image())
                    next_frame = max(next_frame + 1.0/fps, self.frame_times[num][-1] + 0.5/fps)
        except Exception as e:
            print(e)

    def start_record(self):
        if len(self.vid_out) == 0:
            remind_vid_window = Tk()
            Label(remind_vid_window, text="VideoWriter not initialized! \nPlease set up video and try again.").pack()
            Button(remind_vid_window, text="Ok", command=lambda:remind_vid_window.quit()).pack()
            remind_vid_window.mainloop()
            remind_vid_window.destroy()
        else:
            self.vid_start_time = time.time()
            t = []
            for i in range(len(self.cam)):
                t.append(threading.Thread(target=self.record_on_thread, args=(i,)))
                t[-1].daemon = True
                t[-1].start()

    def compress_vid(self, ind):
        ff_input = dict()
        ff_input[self.vid_file[ind]] = None
        ff_output = dict()
        out_file = self.vid_file[ind].replace('avi', 'mp4')
        ff_output[out_file] = '-c:v libx264 -crf 17'
        ff = ffmpy.FFmpeg(inputs=ff_input, outputs=ff_output)
        ff.run()

    def save_vid(self, compress=False, delete=False):

        saved_files = []

        # check that videos have been initialized

        if len(self.vid_out) == 0:
            not_initialized_window = Tk()
            Label(not_initialized_window, text="Video writer is not initialized. Please set up first to record a video.").pack()
            Button(not_initialized_window, text="Ok", command=lambda:not_initialized_window.quit()).pack()
            not_initialized_window.mainloop()
            not_initialized_window.destroy()

        else:

            # check for frames before saving. if any video has not taken frames, delete all videos
            frames_taken = all([len(i) > 0 for i in self.frame_times])

            # release video writer (saves file).
            # if no frames taken or delete specified, delete the file and do not save timestamp files; otherwise, save timestamp files.
            for i in range(len(self.vid_out)):
                self.vid_out[i].release()
                self.vid_out[i] = None
                if (delete) or (not frames_taken):
                    os.remove(self.vid_file[i])
                else:
                    np.save(str(self.ts_file[i]), np.array(self.frame_times[i]))
                    saved_files.append(self.vid_file[i])
                    saved_files.append(self.ts_file[i])
                    if compress:
                        threading.Thread(target=lambda:self.compress_vid(i)).start()

        if (len(self.lv_ts) > 0) and (not delete):
            np.save(str(self.lv_file), np.array(self.lv_ts))
            saved_files.append(self.lv_file)

        save_msg = ""
        if len(saved_files) > 0:
            save_msg = "The following files have been saved:"
            for i in saved_files:
                save_msg += "\n" + i
        elif delete:
            save_msg = "Video has been deleted, please set up a new video to take another recording."
        elif not frames_taken:
            save_msg = "Video was initialized but no frames were recorded.\nVideo has been deleted, please set up a new video to take another recording."

        if save_msg:
            save_window = Tk()
            Label(save_window, text=save_msg).pack()
            Button(save_window, text="Close", command=lambda: save_window.quit()).pack()
            save_window.mainloop()
            save_window.destroy()

        self.vid_out = []
        self.frame_times = []
        self.current_file_label['text'] = ""


    def close_window(self):

        self.end_labview()
        if not self.setup:
            self.done = True
            self.window.destroy()
        else:
            self.done = True
            self.window.destroy()

    def selectCams(self):

        if self.window is not None:
            self.window.quit()
            self.window.destroy()

        self.setup = False
        self.done = False
        self.vid_out = []
        self.cam = []
        self.cam_name = []
        self.lv_task = None

        # set up window
        select_cams_window = Tk()
        select_cams_window.title("Select Cameras")

        # number of cameras
        Label(select_cams_window, text="How many cameras?").grid(sticky="w", row=0, column=0)
        self.number_of_cams = StringVar(value="1")
        self.number_of_cams_entry = Entry(select_cams_window, textvariable=self.number_of_cams).grid(sticky="nsew", row=0, column=1)
        Button(select_cams_window, text="Set Cameras", command=select_cams_window.quit).grid(sticky="nsew", row=1, column=0, columnspan=2)
        select_cams_window.mainloop()
        select_cams_window.destroy()

        self.createGUI()

    def createGUI(self):

        self.window = Tk()
        self.window.title("Camera Control")

        cur_row = 0
        self.camera = []
        self.camera_entry = []
        self.exposure = []
        self.exposure_entry = []
        for i in range(int(self.number_of_cams.get())):
            # drop down menu to select camera
            Label(self.window, text="Camera "+str(i+1)+": ").grid(sticky="w", row=cur_row, column=0)
            self.camera.append(StringVar())
            self.camera_entry.append(ttk.Combobox(self.window, textvariable=self.camera[i]))
            self.camera_entry[i]['values'] = self.cam_names
            self.camera_entry[i].current(i)
            self.camera_entry[i].grid(row=cur_row, column=1)

            # inialize camera button
            if i==0:
                Button(self.window, text="Initialize Camera 1", command=lambda:self.init_cam(0)).grid(sticky="nsew", row=cur_row+1, column=0, columnspan=2)
            elif i==1:
                Button(self.window, text="Initialize Camera 2", command=lambda:self.init_cam(1)).grid(sticky="nsew", row=cur_row+1, column=0, columnspan=2)
            elif i==2:
                Button(self.window, text="Initialize Camera 3", command=lambda:self.init_cam(2)).grid(sticky="nsew", row=cur_row+1, column=0, columnspan=2)

            # change exposure
            self.exposure.append(StringVar())
            self.exposure_entry.append(Entry(self.window, textvariable=self.exposure[i]))
            self.exposure_entry[i].grid(sticky="nsew", row=cur_row, column=2)
            if i==0:
                Button(self.window, text="Set Exposure 1", command=lambda:self.set_exposure(0)).grid(sticky="nsew", row=cur_row+1, column=2)
            elif i==1:
                Button(self.window, text="Set Exposure 2", command=lambda:self.set_exposure(1)).grid(sticky="nsew", row=cur_row+1, column=2)
            elif i==2:
                Button(self.window, text="Set Exposure 3", command=lambda:self.set_exposure(2)).grid(sticky="nsew", row=cur_row+1, column=2)

            # empty row
            Label(self.window, text="").grid(row=cur_row+2, column=0)

            # end of camera loop
            cur_row = cur_row+3

        # Labview Channel
        Label(self.window, text="Labview Channel: ").grid(sticky="w", row=cur_row, column=0)
        self.labview_channel = StringVar(value="")
        self.labview_channel_entry = ttk.Combobox(self.window, textvariable=self.labview_channel)
        self.labview_channel_entry['values'] = tuple(self.labview_channel_list)
        self.labview_channel_entry.grid(sticky="nsew", row=cur_row, column=1)
        Button(self.window, text="Initialize Labview", command=self.init_labview).grid(sticky="nsew", row=cur_row+1, column=0, columnspan=2)
        Button(self.window, text="End LV", command=self.end_labview).grid(sticky="nsew", row=cur_row+1, column=2)
        cur_row += 2

        # empty row
        Label(self.window, text="").grid(row=cur_row, column=0)
        cur_row+=1

        # subject name
        Label(self.window, text="Subject: ").grid(sticky="w", row=cur_row, column=0)
        self.subject = StringVar()
        self.subject_entry = ttk.Combobox(self.window, textvariable=self.subject)
        self.subject_entry['values'] = tuple(self.mouse_list)
        self.subject_entry.grid(row=cur_row, column=1)
        cur_row += 1

        # attempt
        Label(self.window, text="Attempt: ").grid(sticky="w", row=cur_row, column=0)
        self.attempt = StringVar(value="1")
        self.attempt_entry = ttk.Combobox(self.window, textvariable=self.attempt)
        self.attempt_entry['values'] = tuple(range(1,10))
        self.attempt_entry.grid(row=cur_row, column=1)
        cur_row += 1

        # type frame rate
        Label(self.window, text="Frame Rate: ").grid(sticky="w", row=cur_row, column=0)
        self.fps = StringVar()
        self.fps_entry = Entry(self.window, textvariable=self.fps)
        self.fps_entry.insert(END, '100')
        self.fps_entry.grid(sticky="nsew", row=cur_row, column=1)
        cur_row += 1

        # output directory
        Label(self.window, text="Output Directory: ").grid(sticky="w", row=cur_row, column=0)
        self.output = StringVar()
        self.output_entry = ttk.Combobox(self.window, textvariable=self.output)
        self.output_entry['values'] = self.output_dir
        self.output_entry.grid(row=cur_row, column=1)
        Button(self.window, text="Browse", command=self.browse_output).grid(sticky="nsew", row=cur_row, column=2)
        cur_row += 1

        # set up video
        Button(self.window, text="Set Up Video", command=self.set_up_vid).grid(sticky="nsew", row=cur_row, column=0, columnspan=2)
        cur_row += 1

        Label(self.window, text="Current :: ").grid(row=cur_row, column=0, sticky="w")
        self.current_file_label = Label(self.window, text="")
        self.current_file_label.grid(row=cur_row, column=1, sticky="w")
        cur_row += 1

        # empty row
        Label(self.window, text="").grid(row=cur_row, column=0)
        cur_row += 1

        # record button
        Label(self.window, text="Record: ").grid(sticky="w",row=cur_row, column=0)
        self.record_on = IntVar(value=0)
        self.button_on = Radiobutton(self.window, text="On", selectcolor='green', indicatoron=0, variable=self.record_on, value=1, command=self.start_record).grid(sticky="nsew", row=cur_row, column=1)
        self.button_off = Radiobutton(self.window, text="Off", selectcolor='red', indicatoron=0, variable=self.record_on, value=0).grid(sticky="nsew", row=cur_row+1, column=1)
        self.release_vid0 = Button(self.window, text="Save Video", command=lambda:self.save_vid(compress=False)).grid(sticky="nsew", row=cur_row, column=2)
        self.release_vid1 = Button(self.window, text="Compress & Save Video", command=lambda:self.save_vid(compress=True)).grid(sticky="nsew", row=cur_row+1, column=2)
        self.release_vid2 = Button(self.window, text="Delete Video", command=lambda:self.save_vid(delete=True)).grid(sticky="nsew", row=cur_row+2, column=2)
        cur_row += 3

        # close window/reset GUI
        Label(self.window).grid(row=cur_row, column=0)
        self.reset_button = Button(self.window, text="Reset GUI", command=self.selectCams).grid(sticky="nsew", row=cur_row+1, column=0, columnspan=2)
        self.close_button = Button(self.window, text="Close", command=self.close_window).grid(sticky="nsew", row=cur_row+2, column=0, columnspan=2)


    def runGUI(self):
        self.window.mainloop()


if __name__ == "__main__":
    rec = CamGUI()
    rec.runGUI()
