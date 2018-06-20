# Basic motion detection and tracking system
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Basic motion detection and tracking system](#basic-motion-detection-and-tracking-system)
	- [Introduction](#introduction)
	- [Sample GIFs and videos](#sample-gifs-and-videos)
	- [Files description](#files-description)
	- [Installation and dependencies](#installation-and-dependencies)
	- [Options, usage, and inputs/outputs](#options-usage-and-inputsoutputs)
		- [Script configuration options (conf.json)](#script-configuration-options-confjson)
		- [Logging options (logging_conf.json)](#logging-options-logging_confjson)
		- [Script usage](#script-usage)
		- [Script Inputs/Outputs](#script-inputsoutputs)
	- [Roadmap](#roadmap)
	- [License](#license)
	- [Notes](#notes)

<!-- /TOC -->
## Introduction
A basic motion detection and tracking system is implemented using two basic
background substitution models:
* First background model: **first frame** taken to model the background
* Second background model: **weighted average** of frames

The **Python** code implementation for these two background models are based
from **Adrian Rosebrock**'s tutorials @ www.pyimagesearch.com:
* [first-frame background model](https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/)
* [weighted-average-of-frames backgroundmodel](https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/)

For each motion detected, a bounding box is drawn around the object like the
following:

The system can be configured through a configuration file
([conf.json](#script-configuration-options-confjson)), and its logging can be
setup with [logging_conf.json](#logging-options-loggingconfjson).

## Sample GIFs and videos
Here are some sample GIFs and videos of how the two basic background
substitution methods work when applied on some of the images from the
[SBMnet dataset](http://pione.dinf.usherbrooke.ca/dataset/):

![test](./samples/first_frame/first_frame_3_videos.gif "'first frame' background model")

![test](./samples/weighted_average/weighted_average_3_videos.gif "'weighted average' background model")

![test](https://3.bp.blogspot.com/-MQJP0igwZgY/WynFtoiIAPI/AAAAAAAAAGk/lfgrsaCDp7wBeReVNXRwFMR4AGjklQUXgCKgBGAs/s1600/weighted_average_3_videos.gif)

As a side-note, if you are wondering how I generated the GIFs or videos from the
test images, check my blog posts: [Make a GIF from a video file on a Mac](http://progsharing.blogspot.com/2018/06/make-gif-from-video-file-on-mac-no.html)
and [Generate a movie from a sequence of images on a Mac]().

## Files description
* `motion_detector.py`: main script that performs motion detection and tracking
of objects on images/videos
* `imutils.py`: module that only has the necessary functions from the
[`imutils`](https://github.com/jrosebr1/imutils) package from
[Adrian Rosebrock](https://www.pyimagesearch.com/). Hence, it is not necessary
to install the `imutils` package if only very few functions are used. For the
moment, only the `resize()` function from the `imutils` package is used in the
script.
* `conf.json`: script configuration options
* `logging_conf.json`: **logging** configuration options. By default, logging
writes to a file.

## Installation and dependencies
These are the steps to use the Python script `motion_detector.py`:
1. Install the dependencies defined below
2. Clone the repository and extract it

Dependencies:
* OpenCV 3
* Python 3

I tested the code with Python 3.6, and macOS Sierra 10.12.6.

## Options, usage, and inputs/outputs

### Script configuration options (conf.json)

The `motion_detector.py` script has the following configuration options (defined
in [conf.json](https://github.com/raul23/automated_visual_surveillance_system/blob/master/basic_motion_detection_and_tracking_system/conf.json)):
* `disable_logging`: a boolean variable (true/false) that specifies whether
logging should be disabled. If logging is disabled, then the console will be
used for writing the messages.
* `logging_conf_path`: absolute path to the JSON configuration file for setting
up logging. Default is **logging_conf.json**.
* `background_model`: choices are {"**first_frame**", "**weighted_average**"}.
It is the type of background model. `first_frame` refers to the background model
where the first frame is used as model of the background. `weighted_average`
refers to modeling the background as a weighted average of the past and current
frame.
* `video_path`: full path to the video to be processed. If no video provided,
leave option empty, i.e. `video_path`=""
* `image_path`: full path to the sequence of images to be processed.
**Important**: the images must follow a naming pattern with zero paddings,
e.g. image%06d.jpg. If no images provided, leave option empty, i.e.
`image_path`=""
* `base_saved_directory`: full path to the **main directory** for saving all the
results from running the scripts, e.g. debugging logs, security feed images.
Each run of the script will write in a separate folder (named as
'YYYYMMDD-HHMMSS-image_results') within `base_saved_directory/`. **IMPORTANT**:
if option left as empty (`base_saved_directory`=""), then no images will be
saved.
* `save_security_feed_images`: a boolean variable (true/false) that specifies
whether the 'security feed' images will be saved. These are the images with the
bounding boxes around the detected moving objects. TODO: add link to image
* `save_frame_delta_images`: a boolean variable (true/false) that specifies
whether the 'frame delta' images will be saved. These are the images that
correspond to the absolute difference between the current grayscale frame and
the image representing the background. TODO: add link to image
* `save_thresh_images`: a boolean variable (true/false) that specifies whether
the 'thresholded' images will be saved. These are the binary images created out
of the 'frame delta' grayscale images: the foreground is white and the
background black. TODO: add link to image
* `overwrite_image`: a boolean variable (true/false) that specifies whether the
already saved images in `.../base_saved_directory/YYYYMMDD-HHMMSS-image_results/`
can be overwritten.
* `image_format`: choices are {"png", "jpg", "jpeg"}. This is the format used
when saving the resulting images. If the entered image format is not supported,
png format is used by default.
* `show_video`: a boolean variable (true/false) that specifies whether to show
the videos (for the different types of images) on screen.
* `start_frame`: an integer variable (default is 1) that specifies the starting
frame to be processed.
* `end_frame`: an integer variable (default is 0) that specifies the ending
frame to be processed. 0 refers to the last frame.
* `min_area`: an integer variable (default is 500) that specifies the minimum
size (500 pixels) for a region of an image to be considered actual “motion”. If
the region (contour) is too small, then it will be ignored, i.e. it will not be
considered as motion.
* `delta_thresh`: an integer variable (default is 25) that specifies the
threshold value used for generating a binary image (thresholded image) out of a
grayscale image ('frame delta' image). Every pixel in the 'frame delta' image
greater than `delta_thresh` will be converted to white (i.e. foreground), and
the other pixels to black (i.e. background).
* `resize_image_width`: an integer variable (default is 500) that
specifies the width in pixels the image should be resized to. If
`resize_image_width` is 0, then the image will not be resized.
* `show_datetime`: a boolean variable (true/false) that specifies whether to
show the actual date & time on the 'security feed' video.
* `gaussian_kernel_size`: a `dict` variable that specifies the width and height
of the Gaussian kernel used for blurring an image:
  * `width`: an integer variable (default is 21) that specifies the width of the
	Gaussian kernel.
  * `height`: an integer variable (default is 21) that specifies the height of
	the Gaussian kernel.

### Logging options (logging_conf.json)
The `motion_detector.py` script has the following important **logging**
configuration options (defined in [logging_conf.json](https://github.com/raul23/automated_visual_surveillance_system/blob/master/basic_motion_detection_and_tracking_system/logging_conf.json)):
* `formatters`: list of formatters. Two types of formatters (`verbose` and
	`simple`) are available by default depending on how much information you need
	for each log message.
* `handlers`: list of handlers that are in charge of "[dispatching the
appropriate log messages](https://docs.python.org/3/howto/logging.html#handlers)".
The most important handlers are for writing logs to files
(`logging.FileHandler`), and to the console (`logging.StreamHandler`s). By
default, the log messages `debug.log` will be saved in
`.../base_saved_directory/YYYYMMDD-HHMMSS-image_results/`.
* `loggers`: list of all the loggers along with their options (e.g. severity
level) and handlers. By default, two loggers are available: one logger for the `motion_detector.py` script named `basic_motion_detection_and_tracking_system.motion_detector` which follows the
usual naming pattern for loggers in **Python**: `package_name.module_name`. The
second logger is the `root` logger with the `WARNING` severity level.

### Script usage
`python motion_detector.py -c conf.json`

`conf.json` can also refer to your own configuration file named whatever you
want. Thus, you can leave the default `conf.json` as a template, and have your
own configuration file, named for example `my_conf.json`, that will be called
when running the script.

Same for `logging_conf.json`, you could name it whatever you want, and refer it
in `conf.json`. Thus, `logging_conf.json` could also be used as a template.

**IMPORTANT:** when running the script for the first time, it might take some
time reading the images if there are a lot of them (e.g. more than 1000). The
next time the script is run, since the images are already loaded on memory, the
images will be read quickly.

### Script Inputs/Outputs
The system can take as **inputs**:
* a video from a file (e.g. a pre-recorded security camera video), or your
webcam feed.
* an image sequence (**png** or **jpg**) having the naming pattern with zero
paddings, e.g. image%06d.jpg.

The system **outputs** the following by *default* within the folder
`.../base_saved_directory/YYYYMMDD-HHMMSS-image_results/`
<sup id="go_back_note_01"><a href="#note_01">[1]</a></sup>:
* `background_image.png`: image representing the background. Depending on the
background model selected (*see the* `background_model` *option*), it can
correspond to the first frame or a weighted average of the past and current
frames.
* `command.txt`: the **Python** command used for running the `motion_detector.py`
script
* `conf.json`: JSON configuration storing the script options. For the detailed
list of the script options, see
[Script configuration options (conf.json)](#script-configuration-options-confjson).
* `logging_conf.json`: JSON configuration file for setting up the logging. For
the list of the most important logging options, see
[Logging options (logging_conf.json)](#logging-options-loggingconfjson).
* `debug.log`: file storing all the written log messages
* `security_feed/`: folder storing all the 'security feed' images
* `thresh/`: folder storing all the thresholded images
* `frame_delta/`: folder storing all the 'frame delta' images

## Roadmap
In order of importance, these are the changes I will work on:
* Add unit tests [**topmost**]
* Implement more sophisticated background substitution models
* Implement more sophisticated tracking systems (e.g. Kalman filter)
* Make the code Python 2.7 compatible
* Test the code on Linux
* Package the Python script
* Make a Docker image

## License
The code is licensed under the GNU GPL 3 license. See the [license](https://github.com/raul23/automated_visual_surveillance_system/blob/master/LICENSE)
for more details.

## Notes
<div id="note_01">1. <a href="#go_back_note_01">^</a> Each time the script is run, ...</a></div>
