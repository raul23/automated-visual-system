Two basic background substitution models implemented: 
* first background model: first frame taken to model the background
* second background model: weighted average of frames

Files description:
* motion_detector.py: main script that ...
* conf.json: main configuration options
* logging_conf.json: logging configuration options
 
## Installation and dependencies
These are the steps to use the Python script motion_detector.py:
1. Install the dependencies defined below
2. Clone the repository and extract it

Dependencies:
* OpenCV 3
* Python 3

I tested the code with Python 3.6, and macOS Sierra 10.12.6.
 
## Usage and options

### Script configuration options (conf.json)

The motion_detector.py script has the following configuration options (defined in conf.json):
* disable_logging: Default value is false.
* logging_conf_path: logging_conf.json.
* background_model: "first_frame".
* video_path:
* image_path:
* base_saved_folder:
* overwrite_image: true
* image_format: "png"
* show_video: true
* start_frame: 0
* end_frame: 0
* min_area: 100
* delta_thresh: 25
* resize_image_width": 500
* show_datetime: true
* gaussian_kernel_size:

### Logging options (logging_conf.json)
The motion_detector.py script has the following **logging** configuration options (defined in logging_conf.json):


### Script usage

## Roadmap
In order of importance, these are the changes I will work on:
* Package the Python script [topmost]
* Add unit tests
* Make the code Python 2.7 compatible
* Implement more sophisticated background substitution models
* Implement more sophisticated tracking systems (e.g. Kalman filtering)
* Make a Docker image

## License