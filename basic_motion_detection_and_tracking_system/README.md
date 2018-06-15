# Basic motion detection and tracking system

Two basic background substitution models implemented:
* First background model: **first frame** taken to model the background
* Second background model: **weighted average** of frames

The code implementation for these two background models are based from Adrian
Rosebrock's tutorials @ www.pyimagesearch.com:
* [first-frame background model](https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/)
* [weighted-average-of-frames background model](https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/)

## Contents
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Basic motion detection and tracking system](#basic-motion-detection-and-tracking-system)
	- [Contents](#contents)
	- [Sample GIFs and videos](#sample-gifs-and-videos)
	- [Files description](#files-description)
	- [Installation and dependencies](#installation-and-dependencies)
	- [Options and usage](#options-and-usage)
		- [Script configuration options (conf.json)](#script-configuration-options-confjson)
		- [Logging options (logging_conf.json)](#logging-options-loggingconfjson)
		- [Script usage](#script-usage)
	- [Roadmap](#roadmap)
	- [License](#license)

<!-- /TOC -->

## Sample GIFs and videos
Here are some sample GIFs and videos of how the two basic background
substitution methods work when applied on some of the images from the
[SBMnet dataset](http://pione.dinf.usherbrooke.ca/dataset/): ...

As a side-note, if you are wondering how I generated the GIFs or videos from the
test images, check my blog posts: [Make a GIF from a video file on a Mac](http://progsharing.blogspot.com/2018/06/make-gif-from-video-file-on-mac-no.html)
and [Generate a movie from a sequence of images on a Mac]().

## Files description
* `motion_detector.py`: main script that performs motion detection and tracking
of objects on images/videos
* `imutils.py`: module that only has the necessary functions from the [imutils](https://github.com/jrosebr1/imutils)
package from [Adrian Rosebrock](https://www.pyimagesearch.com/). Hence, it is not necessary to install this package
if only very few functions are used. For the moment, only the `resize()` function
is used in the script.
* `conf.json`: **main** configuration options
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

## Options and usage

### Script configuration options (conf.json)

The `motion_detector.py` script has the following configuration options (defined
in [conf.json](https://github.com/raul23/automated_visual_surveillance_system/blob/master/basic_motion_detection_and_tracking_system/conf.json)):
* `disable_logging`: a boolean variable (true/false) that specifies whether logging should be disabled
* `logging_conf_path`: absolute path to the JSON configuration file for setting up logging
* `background_model`: choices are {"first_frame", "weighted_average"}. It is the
type of background model, e.g. weighted average of frames
* `video_path`: full path to the video to be processed
* `image_path`: full path to the sequence of images to be processed.
**Important**: the images must follow a naming pattern with zero paddings,
e.g. image%06d.jpg.
* `base_saved_folder`: full path to the folder for saving all the results from
running the scripts, e.g. debugging logs, security feed images
* `save_security_feed_images`: a boolean variable (true/false) that specifies
whether the 'security feed' images will be saved
* `save_thresh_images`:
* `save_frame_delta_images`:
* `overwrite_image`:
* `image_format`: choices are {"png", "jpg", "jpeg"}. This is the format used
when saving the resulting images. If image format is not supported, png format
is used.
* `show_video`:
* `start_frame`: 0
* `end_frame`: 0
* `min_area`: 100
* `delta_thresh`: 25
* `resize_image_width`: 500
* `show_datetime`:
* `gaussian_kernel_size`:

### Logging options (logging_conf.json)
The `motion_detector.py` script has the following **logging** configuration
options (defined in [logging_conf.json](https://github.com/raul23/automated_visual_surveillance_system/blob/master/basic_motion_detection_and_tracking_system/logging_conf.json)):

### Script usage

## Roadmap
In order of importance, these are the changes I will work on:
* Package the Python script [**topmost**]
* Add unit tests
* Make the code Python 2.7 compatible
* Test the code on Linux
* Implement more sophisticated background substitution models
* Implement more sophisticated tracking systems (e.g. Kalman filter)
* Make a Docker image

## License
The code is licensed under the GNU GPL 3 license. See the [license](https://github.com/raul23/automated_visual_surveillance_system/blob/master/LICENSE)
for more details.
