<img src="https://images.squarespace-cdn.com/content/v1/57f6d51c9f74566f55ecf271/1564768953154-CH2E4W7M0ORYRGGZP0W0/ke17ZwdGBToddI8pDm48kHJH6WvD-K6SQJl_lpgiA4wUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYy7Mythp_T-mtop-vrsUOmeInPi9iDjx9w8K4ZfjXt2dtyDHbM6wOPdgJbmQh4Pb6c9D9xnXrxbqSawZVwoRTUNCjLISwBs8eEdxAxTptZAUg/Camera+Control-logo-black.png?format=1000w" width="450" title="camera control" alt="cam cntrl" align="center" vspace = "350">

#### record video and system timestamps from Imaging Source USB3 cameras

Python GUI + scripts to record video sync'ed to behavior. Can record from multiple imaging source camera feeds while simultaneously grabbing system timestamps for each recorded frame. One can also record timestamps from one NIDAQ card signal to sync with a behavioral task (records timestamp on the rising edge of a TTL signal).


This software package was written by [Gary Kane](https://github.com/gkane26), post-doctoral fellow @ the [Adaptive Motor Control Lab](https://github.com/AdaptiveMotorControlLab).


**Prerequisite Software:**
1. Windows 10
2. [Anaconda](https://www.anaconda.com/)
3. [Git](https://gitforwindows.org/)

**Required Hardware:**
1. [Imaging Source USB cameras](https://www.theimagingsource.com/)
2. (Optional) NIDAQ card. Necessary to record timestamps from a behavioral task. Signal must be a TTL wired to digital input channel that is not dual-PFI (one that has hardware interrupt capabilities).

## Instructions for Installation:

1. Install the latest driver for your camera. You can find the driver from The Imaging Source website: https://www.theimagingsource.com/products/. **If you add new cameras to an existing system, make sure to update the driver!**

1. Clone this repository. Open command prompt (type "cmd" into the search bar and hit enter), then type:<br/><br/>
``git clone https://github.com/AdaptiveMotorControlLab/camera_control``

2. Open the camera control directory, **right-click 'install1.bat' and select 'Run as administrator'**<br/><br/>
This script will install imaging source libraries, ffmpeg for command prompt, and create a new conda environment 'camera27'. Upon completion, the window will close suddenly.

3. Run 'install2.bat'.<br/><br/>
This script will finish setting up the conda environment and create a desktop shortcut to open the GUI.

4. Edit the 'write_camera_details.py' script according to your system's camera configuration. A template is provided (write_camera_details_TEMPLATE.py), please do not edit the template. The 'write_camera_details.py' script will write a dictionary to the file 'camera_details.json' containing the following fields:
    - a dictionary for each imaging source camera with the fields:
        - name = camera name
        - crop = cropping parameters
        - rotate = rotation angle of image
        - exposure = integer exposure values; can edit this in the GUI
        - output_dir = default directory to save videos; can edit this in the GUI
        - Example:
        
              
              cam_0 = {'name' : 'Cog Rig',
                      'crop' : {'top' : 150, 'left' : 225, 'height' : 250, 'width' : 300},
                      'rotate' : 0,
                      'exposure' : -14,
                      'output_dir' : 'C:/Users/user1/Desktop/video'}
              
              
    - subjects = a list of experimental subjects to select. Can be manually entered in GUI
    - labview = a list of labview channels to select, e.g. ['Dev1/port0/line0'] (optional). Can be manually entered in GUI <br/><br/>


## To Run the Program:

Double click the cameraGUI.bat file on the Desktop or open command prompt, navigate to the camera_control directory, and run: ``python camera_control_GUI.py``

1. Select the number of cameras to record from
2. Select and initialize each cameras
3. Select subject, frame rate and output directory, then click 'Set Up Video'
    - Will default to the output directory from 'camera_details.json'
    - Drop down menus for subject and output directory are populated via 'camera_details.json'
4. To start recording, click the On button. Recording can be turned Off/On multiple times -- frames, system timestamps, and timestamps from the nidaq card will be stored only when 'Record' is set to 'On'.
5. Once finished recording, click 'Save Video', 'Compress & Save Video', or 'Delete Video'
    - 'Save Video' saves an .avi file using the DIVX codec to 'output_dir/CameraName_Subject_Date.avi' and timestamp files to 'output_dir/TIMESTAMPS_CameraName_Subject_Date.npy' and (if applicable) 'output_dir/LABVIEW_Subject_Date.npy'. There will be one timestamps file per camera, but only one labview timestamp file per session.
    - 'Compress & Save Video' saves as above, but also saves an .mp4 file using ffmpeg compression to 'output_dir/CameraName_Subject_Date.mp4'
    - 'Delete Video' will not save any videos of timestamp files. Preliminary video files will be deleted.
6. To record more videos, return to step iii.

## LICENSE: 


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED. Please see [here](/LICENSE) for more information. ![GitHub](https://img.shields.io/github/license/AdaptiveMotorControlLab/Camera_Control?color=blue)

## Citation:

If you find this software useful for your research, please cite: [![DOI](https://zenodo.org/badge/200101590.svg)](https://zenodo.org/badge/latestdoi/200101590)
