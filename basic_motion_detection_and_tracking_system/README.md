# Basic motion detection and tracking system

Two basic background substitution models implemented: 
* First background model: **first frame** taken to model the background
* Second background model: **weighted average** of frames

The code implementation for these two background models are taken from Adrian Rosebrock tutorials @ www.pyimagesearch.com:
* [first-frame background model](https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/)
* [weighted-average-of-frames background model](https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/)


## Files description
* `motion_detector.py`: main script that performs motion detection and tracking of objects on images/videos
* `conf.json`: **main** configuration options
* `logging_conf.json`: **logging** configuration options. By default, logging writes to a file.
 
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

The motion_detector.py script has the following configuration options (defined in conf.json):
* `disable_logging`: Default value is false.
* `logging_conf_path`: logging_conf.json.
* `background_model`: "first_frame".
* `video_path`:
* `image_path`:
* `base_saved_folder`:
* `save_security_feed_images`: true
* `save_thresh_images`: true
* `save_frame_delta_images`: true
* `overwrite_image`: true
* `image_format`: "png"
* `show_video`: true
* `start_frame`: 0
* `end_frame`: 0
* `min_area`: 100
* `delta_thresh`: 25
* `resize_image_width`: 500
* `show_datetime`: true
* `gaussian_kernel_size`:

### Logging options (logging_conf.json)
The `motion_detector.py` script has the following **logging** configuration options (defined in logging_conf.json):


### Script usage

## Roadmap
In order of importance, these are the changes I will work on:
* Package the Python script [**topmost**]
* Add unit tests
* Make the code Python 2.7 compatible
* Implement more sophisticated background substitution models
* Implement more sophisticated tracking systems (e.g. Kalman filtering)
* Make a Docker image

## License