"""
Basic motion detection and tracking system

References:
    https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
    https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/
"""
import argparse
import datetime
import json
import linecache
import logging.config
import os
from pathlib import Path
import subprocess
import sys
import time

import cv2
import imutils
import ipdb


# Get the logger
if __name__ == '__main__':
    # When run as a script
    logger = logging.getLogger('{}.{}'.format(os.path.basename(os.getcwd()), os.path.splitext(__file__)[0]))
else:
    # When imported as a module
    # TODO: test this part when imported as a module
    logger = logging.getLogger('{}.{}'.format(os.path.basename(os.path.dirname(__file__)), __name__))


def exit_from_program(code_status=1):
    logger.error('Exiting program')
    sys.exit(code_status)


def file_exists(path):
    """
    Checks if both a file exists and it is a file. Returns True if it is the
    case (can be a file or file symlink).
    ref.: http://stackabuse.com/python-check-if-a-file-or-directory-exists/
    :param path: path to check if it points to a file
    :return bool: True if it file exists and is a file. False otherwise.
    """
    path = os.path.expanduser(path)
    return os.path.isfile(path)


# ref.: https://stackoverflow.com/a/12412153
#       https://stackoverflow.com/a/667754
def get_full_command_line():
    return "python {}".format(subprocess.list2cmdline(sys.argv))


def get_full_exception(error=None):
    """
    For a given exception, return filename, line number, the line itself, and
    exception description.
    ref.: https://stackoverflow.com/a/20264059
    :return: TODO
    """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    if error is None:
        err_desc = exc_obj
    else:
        err_desc = '{}: {}'.format(repr(error).split('(')[0], exc_obj)
    # TODO: find a way to add the error description (e.g. AttributeError) without
    # having to provide the error description as input to the function
    exception_msg = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), err_desc)
    return exception_msg


# f: file object
def load_json(f):
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(get_full_exception(e))
        return None
    return data


def setup_logging(config_path):
    if not file_exists(config_path):
        logger.error("Logging configuration file doesn't exit: {}".format(config_path))
        return None
    config_dict = None
    ext = Path(config_path).suffix
    with open(config_path, 'r') as f:
        if ext == '.json':
            config_dict = load_json(f)
        else:
            logger.error('File format for logging configuration file not '
                         'supported: {}'.format(config_path))
    try:
        logging.config.dictConfig(config_dict)
    except ValueError as e:
        get_full_exception(e)
        config_dict = None

    return config_dict


# This creates a timestamped filename/foldername so we don't overwrite our good work
# ref.: https://stackoverflow.com/a/16713796
def timestamped(fname, fmt='%Y%m%d-%H%M%S-{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)


# Return "folder_path/basename" if no file exists at this path. Otherwise,
# sequentially insert "_[0-9]+" before the extension of `basename` and return the
# first path for which no file is present.
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L295
def unique_filename(folder_path, basename):
    stem = Path(basename).stem
    ext = Path(basename).suffix
    new_path = os.path.join(folder_path, basename)
    counter = 0
    while os.path.isfile(new_path):
        counter += 1
        logger.info('File {} already exists in destination {}, trying with counter {}!'.format(new_path, folder_path, counter))
        new_stem = '{}_{}'.format(stem, counter)
        new_path = os.path.join(folder_path, new_stem) + ext
    return new_path


# Return "folder_path" if no folder exists at this path. Otherwise,
# sequentially insert "_[0-9]+" before the end of `folder_path` and return the
# first path for which no folder is present.
def unique_foldername(folder_path):
    counter = 0
    while os.path.isdir(folder_path):
        counter += 1
        logger.info('Folder {} already exists, trying with counter {}!'.format(folder_path, counter))
        folder_path = '{}_{}'.format(folder_path, counter)
    return folder_path


def write_image(path, image, overwrite_image=True):
    if os.path.isfile(path):
        logger.debug("File {} already exist".format(path))
        if overwrite_image:
            logger.debug("Writing file {}".format(path))
            cv2.imwrite(path, image)
        else:
            logger.debug("File {} already exists and overwrite is switched off".format(path))
    else:
        logger.debug("File {} doesn't exist".format(path))
        logger.debug("Writing file {}".format(path))
        cv2.imwrite(path, image)


if __name__ == '__main__':
    # TODO: use `logger` to log into stdout instead of having a separate logger
    # that logs only into stdout
    root_logger_init_level = logging.DEBUG
    stdout_logger_init_level = logging.INFO
    # configure root logger's level and format
    # NOTE: `logger` and `stdout_logger` will inherit config options from the root logger
    logging.basicConfig(level=root_logger_init_level, format="%(message)s")
    stdout_logger = logging.getLogger("stdout_logger")
    sh = logging.StreamHandler(sys.stdout)
    sh.formatter = logging.Formatter("%(message)s")
    stdout_logger.addHandler(sh)
    stdout_logger.setLevel(stdout_logger_init_level)
    stdout_logger.propagate = False

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
    args = vars(ap.parse_args())

    # TODO: explain format for image filenames, pad to length ...

    # load the configuration file
    conf = json.load(open(args["conf"]))

    ####################################
    # Processing configuration options #
    ####################################

    if conf["disable_logging"]:
        logger.info("Logging will be disabled")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        stdout_logger.setLevel(logging.INFO)
    else:
        root_logger = logging.getLogger()
        formatter = logging.Formatter("%(levelname)s %(message)s")
        handlers = root_logger.handlers + stdout_logger.handlers
        for handler in handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(formatter)

    stdout_logger.info("Starting application ...")

    if conf["base_saved_directory"]:
        # Create 'main' directory for storing image results
        # TODO: first check that base_saved_directory  exists. If it doesn't exit, create it.
        new_folder = os.path.join(conf["base_saved_directory"], timestamped("image_results"))
        new_folder = unique_foldername(new_folder)
        logger.debug("Creating folder {}".format(new_folder))
        os.makedirs(new_folder)
        conf["saved_folder"] = new_folder
        # Create folders for each set of images
        for fname in ["security_feed", "thresh", "frame_delta"]:
            if conf["save_{}_images".format(fname)]:
                image_folder = os.path.join(new_folder, fname)
                logger.debug("Creating folder {}".format(image_folder))
                os.makedirs(image_folder)
            else:
                logger.debug("Folder for {} images not created".format(fname))
    else:
        logger.info("Images will not be saved")
        conf["saved_folder"] = ""

    # Setup logging
    # NOTE: logging is setup once main experiment directory is created
    if not conf["disable_logging"]:
        logger.debug("Setup logging")
        if not conf["logging_conf_path"] or setup_logging(conf["logging_conf_path"]) is None:
            logger.error("Logging could not be setup from configuration file")
            logger.warning("Basic logging will be used instead")
        else:
            # Log to the stdout only, not to any other stream (e.g. file, socket)
            stdout_logger.debug("Updating logger's base filename")
            if conf["saved_folder"]:
                # Update logger's base filename
                # NOTE: all handlers' baseFilename are updated
                for handler in logger.handlers:
                    # close() is needed before updating the handler's baseFilename
                    # and os.path.abspath() must be used
                    # ref.: https://stackoverflow.com/a/35120050
                    handler.close()
                    base_filename = os.path.basename(handler.__getattribute__("baseFilename"))
                    new_filename = os.path.abspath(os.path.join(conf["saved_folder"], base_filename))
                    handler.__setattr__("baseFilename", new_filename)
            else:
                logger.error("Logging could not be setup")
                exit_from_program()
            logger.info("Logging is enabled")

    # validate background model
    background_models = ["first_frame", "gitA"]
    if conf["background_model"] not in background_models:
        logger.error("Background model ({}) is not supported".format(conf["background_model"]))
        logger.error("Background models supported are {}".format(background_models))
        exit_from_program()
    else:
        logger.info("Background model used: {}".format(conf["background_model"]))

    # validate gaussian kernel size
    ksize = conf["gaussian_kernel_size"]
    if not ksize["width"] % 2 or ksize["width"] <= 0:
        logger.error("Width of Gaussian kernel should be odd and positive")
        sys.exit(1)
    if not ksize["height"] % 2 or ksize["height"] <= 0:
        logger.error("Height of Gaussian kernel should be odd and positive")
        exit_from_program()

    if conf["image_format"] not in ['jpg', 'jpeg', 'png']:
        logger.error("Image format ({}) is not supported. png will be used".format(conf["image_format"]))
        conf["image_format"] = 'png'

    if conf["resize_image_width"] == 0:
        logger.info("Images will not be resized")

    if conf["start_frame"] == 0 or not conf["start_frame"]:
        logger.warning("start_frame will be changed from {} to 1".format(conf["start_frame"]))
        conf["start_frame"] = 1
    if conf["end_frame"] == 0 or not conf["end_frame"]:
        logger.info("end_frame is set to {}, thus motion detection will run "
                    "until last image".format(conf["end_frame"]))
        # TODO: use inf instead?
        conf["end_frame"] = 1000000

    # setup camera: video file, list of images, or webcam feed
    logger.info("Setup camera")
    if conf["video_path"]:
        # reading from a video file
        stdout_logger.info("Reading video file ...")
        camera = cv2.VideoCapture(conf["video_path"])
        stdout_logger.info("Finished reading video file")
    elif conf["image_path"]:
        # reading from list of images with proper name format
        stdout_logger.info("Reading images ...")
        camera = cv2.VideoCapture(conf["image_path"], cv2.CAP_IMAGES)
        stdout_logger.info("Finished reading images")
    else:
        # reading from webcam feed
        stdout_logger.info("Reading webcam feed ...")
        camera = cv2.VideoCapture(0)
        time.sleep(0.25)
        stdout_logger.info("Finished reading webcam feed")

    # Save configuration file and command line
    if conf["saved_folder"]:
        logger.info("Saving configuration file and command line")
        with open(os.path.join(conf["saved_folder"], 'conf.json'), 'w') as outfile:
            # ref.: https://stackoverflow.com/a/20776329
            json.dump(conf, outfile, indent=4, ensure_ascii = False)
        with open(os.path.join(conf["saved_folder"], 'command.txt'), 'w') as outfile:
            outfile.write(get_full_command_line())

    ###########################
    # Processing images/video #
    ###########################
    stdout_logger.info("Start of images/video processing ...")

    # initialize the first/average frame in the video file/webcam stream
    # NOTE 1: first frame can be used to model the background of the video stream
    # We `assume` that the first frame should not have motion, it should just
    # contain background
    # NOTE 2: the weighted mean of frames frame can also be used to model the
    # background of the video stream
    background_model_frame = None

    # loop over the frames of the video
    # The first frame is the background image and is numbered as frame number 1
    frame_num = 2
    while True:
        if conf["start_frame"] <= frame_num <= conf["end_frame"]:
            # grab the current frame and initialize the occupied/unoccupied text
            # grabbed (bool): indicates if `frame` was successfully read from the buffer
            (grabbed, frame) = camera.read()
            text = "Unoccupied"  # no activity in the room

            # if the frame could not be grabbed, then we have reached the end of the video
            if not grabbed:
                break

            # Preprocessing: prepare current frame for motion analysis
            # resize the frame to 500 pixels wide, convert it to grayscale, and blur it
            # NOTE: image width is used when image is resized. If width is 0, image will
            # not be resized.
            if conf["resize_image_width"] > 0:
                if frame.shape[1] <= conf["resize_image_width"]:
                    logger.debug("Image is being resized to a width ({}) that is "
                                 "greater than its actual width ({})".format(conf["resize_image_width"], frame.shape[1]))
                frame = imutils.resize(frame, width=conf["resize_image_width"])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (ksize["width"], ksize["height"]), 0)

            # if frame representing background model is None, initialize it
            if background_model_frame is None:
                logger.debug("Starting background model ({})...".format(conf["background_model"]))
                if conf["background_model"] == "first_frame":
                    background_model_frame = gray
                    # Save background image
                    if conf["saved_folder"]:
                        bi_fname = "background_image.{}".format(conf["image_format"])
                        bi_fname = os.path.join(conf["saved_folder"], bi_fname)
                        # TODO: overwrite_image is not really necessary since the folder name is unique
                        write_image(bi_fname, frame, conf["overwrite_image"])
                else:
                    assert conf["background_model"] == "weighted_average"
                    # TODO: save background image
                    background_model_frame = gray.copy().astype("float")
                continue

            ##############################################
            ### Start of motion detection and tracking ###
            ##############################################

            if conf["background_model"] == "first_frame":
                # compute the absolute difference between the current frame and first frame
                frameDelta = cv2.absdiff(background_model_frame, gray)
            else:
                assert conf["background_model"] == "weighted_average"
                # accumulate the weighted average between the current frame and
                # previous frames, then compute the difference between the current
                # frame and running average
                # TODO: save background image
                cv2.accumulateWeighted(gray, background_model_frame, 0.5)
                # TODO: why cv2.convertScaleAbs()?
                frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(background_model_frame))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                # --min-area: minimum size (pixels) for a region of an image to be
                # considered actual “motion”
                if cv2.contourArea(c) < conf["min_area"]:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

            # draw the text (top left), timestamp (bottom left), and frame # (top right)
            # on the current frame
            # TODO: add as option the "Room Status" message
            # cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            if conf["show_datetime"]:
                datetime_now = datetime.datetime.now()
                # TODO: remove the following
                datetime_now = datetime_now.replace(hour=15)
                cv2.putText(frame, datetime_now.strftime("%A %d %B %Y %I:%M:%S%p"),
                            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            cv2.putText(frame, "Frame # {}".format(frame_num),
                        (frame.shape[1] - 90, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            # NOTE: path to the folder where three sets of images (security feed,
            # thresold and frame delta) will be saved
            if conf["saved_folder"]:
                image_sets = {'security_feed': frame, 'thresh': thresh, 'frame_delta': frameDelta}
                for iname, image in image_sets.items():
                    if conf["save_{}_images".format(iname)]:
                        inum = "{0:06d}".format(frame_num)
                        fname = "{}_{}.{}".format(iname, inum, conf["image_format"])
                        fname = os.path.join(conf["saved_folder"], iname ,fname)
                        write_image(fname, image, conf["overwrite_image"])
                    else:
                        logger.debug("{} image not saved: frame # {}".format(iname, frame_num))

            # check to see if the frames should be displayed to screen
            if conf["show_video"]:
                # show the frame and record if the user presses a key
                cv2.imshow("Security Feed", frame)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Frame Delta", frameDelta)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the loop
                if key == ord("q"):
                    logger.debug("Q key pressed. Quitting program ...")
                    break

        elif frame_num > conf["end_frame"]:
            logger.debug("Reached end of frames: frame # {}".format(frame_num))
            break
        else:
            logger.debug("Skipping frame number {}".format(frame_num))

        if frame_num == 2:
            ipdb.set_trace()

        # update frame number
        frame_num += 1

    stdout_logger.info("End of images/video processing")
    logger.info("Number of frames processed: {}".format(frame_num - 1))

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()

    stdout_logger.info("End of application")
