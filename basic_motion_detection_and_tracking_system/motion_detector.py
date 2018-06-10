"""
Basic motion detection and tracking system

References:
    https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
    https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import time

import cv2
import imutils  # Set of convenience functions for image processing
import ipdb


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
        print('[INFO] File {} already exists in destination {}, trying with counter {}!'.format(new_path, folder_path, counter))
        new_stem = '{}_{}'.format(stem, counter)
        new_path = os.path.join(folder_path, new_stem) + ext
    return new_path


# Return "folder_path" if no folder exists at this path. Otherwise,
# sequentially insert "_[0-9]+" before the end of `folder_path` and return the
# first path for which no folder is present.
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L295
def unique_foldername(folder_path):
    counter = 0
    while os.path.isdir(folder_path):
        counter += 1
        print('[INFO] Folder {} already exists, trying with counter {}!'.format(folder_path, counter))
        folder_path = '{}_{}'.format(folder_path, counter)
    return folder_path


def write_image(path, image, overwrite_image=True):
    if os.path.isfile(path):
        if overwrite_image:
            cv2.imwrite(path, image)
        else:
            print("[DEBUG] File {} already exists and overwrite is switched off".format(path))
    else:
        print("[DEBUG] File {} doesn't exist".format(path))
        print("[DEBUG] Writing file {}".format(path))
        cv2.imwrite(path, image)


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
    args = vars(ap.parse_args())

    # TODO: explain format for image filenames, pad to length ...

    # load the configuration
    conf = json.load(open(args["conf"]))

    # validate gaussian kernel size
    ksize = conf["gaussian_kernel_size"]
    if not ksize["width"] % 2 or ksize["width"] <= 0:
        print("[ERROR] Width of Gaussian kernel should be odd and positive")
        sys.exit(1)
    if not ksize["height"] % 2 or ksize["height"] <= 0:
        print("[ERROR] Height of Gaussian kernel should be odd and positive")
        sys.exit(1)

    if conf["image_format"] not in ['jpg', 'png']:
        print("[WARNING] Image format ({}) is not supported. png will be used".format(conf["image_format"]))
        conf["image_format"] = 'png'

    if conf["resize_image_width"] == 0:
        print("[INFO] Images will not be resized")

    if conf["base_saved_folder"] == 0:
        print("[INFO] Images will not be saved")
    else:
        # Create directory (main) for storing image results
        new_folder = os.path.join(conf["base_saved_folder"], timestamped("image_results"))
        new_folder = unique_foldername(new_folder)
        print("[INFO] Creating folder {}".format(new_folder))
        os.makedirs(new_folder)
        conf["saved_folder"] = new_folder
        # Create folders for each set of images
        for fname in ["security_feed", "thresh", "frame_delta"]:
            image_folder = os.path.join(new_folder, fname)
            print("[INFO] Creating folder {}".format(image_folder))
            os.makedirs(image_folder)

    # setup camera: video file, list of images, or webcam feed
    if conf["video_path"]:
        # reading from a video file
        camera = cv2.VideoCapture(conf["video_path"])
    elif conf["image_path"]:
        # reading from list of images with proper name format
        camera = cv2.VideoCapture(conf["image_path"], cv2.CAP_IMAGES)
    else:
        # reading from webcam feed
        camera = cv2.VideoCapture(0)
        time.sleep(0.25)

    # initialize the first frame in the video file/webcam stream
    # NOTE: first frame can be used to model the background of the video stream
    # We `assume` that the first frame should not have motion, it should just
    # contain background
    firstFrame = None

    # loop over the frames of the video
    frame_num = 2
    while True:
        # grab the current frame and initialize the occupied/unoccupied text
        # grabbed (bool): indicates if `frame` was successfully read from the buffer
        (grabbed, frame) = camera.read()
        text = "Unoccupied"  # no activity in the room

        # if the frame could not be grabbed, then we have reached the end of the video
        if not grabbed:
            break

        # Preprocessing: preprare current frame for motion analysis
        # resize the frame to 500 pixels wide, convert it to grayscale, and blur it
        # NOTE: image width is used when image is resized. If width is 0, image will
        # not be resized.
        if conf["resize_image_width"] > 0:
            if frame.shape[1] <= conf["resize_image_width"]:
                print("[DEBUG] Image is being resized to a width ({}) that is "
                      "greater than its actual width ({})".format(conf["resize_image_width"], frame.shape[1]))
            frame = imutils.resize(frame, width=conf["resize_image_width"])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (ksize["width"], ksize["height"]), 0)

        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            # Save background image
            if conf["saved_folder"]:
                bi_fname = "background_image.{}".format(conf["image_format"])
                bi_fname = os.path.join(conf["saved_folder"], bi_fname)
                write_image(bi_fname, frame, conf["overwrite_image"])
            continue

        ##############################################
        ### Start of motion detection and tracking ###
        ##############################################

        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours on
        # thresholded image
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
        # NOTE 1: the y-axis goes positive downwards (instead of upwards as in the
        # cartesian coordinate system)
        #
        # (0,0) --------> (x)
        #   |
        #   |
        #   |
        #   |
        #   v (y)
        #
        #
        # NOTE 2: frame.shape[0] = maximum y-coordinate
        #         frame.shape[1] = maximum x-coordinate
        #
        # Thus, top-left     = (0, 0)
        #       top-right    = (frame.shape[1], 0)
        #       bottom-left  = (0, frame.shape[0])
        #       bottom-right = (frame.shape[1], frame.shape[0])
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if conf["show_datetime"]:
            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.putText(frame, "Frame # {}".format(frame_num),
                    (frame.shape[1] - 90, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # NOTE: path to the folder where three sets of images (security feed,
        # thresold and frame delta) will be saved
        if conf["saved_folder"]:
            image_sets = {'security_feed': frame, 'thresh': thresh, 'frame_delta': frameDelta}
            for iname, image in image_sets.items():
                inum = "{0:06d}".format(frame_num)
                fname = "{}_{}.{}".format(iname, inum, conf["image_format"])
                fname = os.path.join(conf["saved_folder"], iname ,fname)
                write_image(fname, image, conf["overwrite_image"])

        # show the frame and record if the user presses a key
        cv2.imshow("Security Feed", frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break

        # update frame number
        frame_num += 1

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()
