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
import sys
import time

import cv2
import imutils  # Set of convenience functions for image processing
import ipdb


def write_image(path, image, overwrite_image=True):
    if os.path.isfile(path):
        if overwrite_image:
            cv2.imwrite(path, image)
        else:
            print("[DEBUG] file {} already exists and overwrite is switched off".format(path))
    else:
        print("[DEBUG] file {} doesn't exist".format(path))
        print("[DEBUG] writing file {} ...".format(path))
        cv2.imwrite(path, image)


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
    args = vars(ap.parse_args())

    ipdb.set_trace()

    # TODO: explain format for image filenames, pad to length ...

    # load the configuration
    conf = json.load(open(args["conf"]))

    # validate gaussian kernel size
    ksize = conf["gaussian_kernel_size"]
    if not ksize["width"] % 2 or ksize["width"] <= 0:
        print("[ERROR] width of Gaussian kernel should be odd and positive")
        sys.exit(1)
    if not ksize["height"] % 2 or ksize["height"] <= 0:
        print("[ERROR] height of Gaussian kernel should be odd and positive")
        sys.exit(1)

    if conf["resize_image_width"] == 0:
        print("[INFO] images will not be resized")

    if conf["saved_folder"] == 0:
        print("[INFO] images will not be saved")

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
                print("[DEBUG] image is being resized to a width ({}) that is "
                      "greater than its actual width ({})".format(conf["resize_image_width"], frame.shape[1]))
            frame = imutils.resize(frame, width=conf["resize_image_width"])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (ksize["width"], ksize["height"]), 0)

        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            # Save background image
            if conf["saved_folder"]:
                bi_fname = "background_image.png"
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
            sf_fname = "security_feed_{0:06d}.png".format(frame_num)
            t_fname = "thresh_{0:06d}.png".format(frame_num)
            fd_fname = "frame_delta_{0:06d}.png".format(frame_num)
            sf_fname = os.path.join(conf["saved_folder"], sf_fname)
            t_fname = os.path.join(conf["saved_folder"], t_fname)
            fd_fname = os.path.join(conf["saved_folder"], fd_fname)
            write_image(sf_fname, frame, conf["overwrite_image"])
            write_image(t_fname, thresh, conf["overwrite_image"])
            write_image(fd_fname, frameDelta, conf["overwrite_image"])

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
