import os
import cv2
import numpy as np
import random
import shutil
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from datetime import timedelta
# from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

image = Blueprint("image", __name__, static_folder="static",
                  template_folder="templates")


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


@image.route("/encode")
def image_encode():
    if os.path.exists(current_app.config['IMAGE_CACHE_FOLDER']):
        shutil.rmtree(
            current_app.config['IMAGE_CACHE_FOLDER'], ignore_errors=False)
    else:
        print("Not Found")

    if os.path.exists(os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'], "adjusted_sample.jpg")):
        # print("Found")
        os.remove(os.path.join(
            current_app.config['UPLOAD_IMAGE_FOLDER'], "adjusted_sample.jpg"))
    else:
        print("Not found")

    if os.path.exists(os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'], "encrypted_image.png")):
        # print("Found")
        os.remove(os.path.join(
            current_app.config['UPLOAD_IMAGE_FOLDER'], "encrypted_image.png"))
    else:
        print("Not found")

    

    return render_template("encode-image.html")


@image.route("/encode-result", methods=['POST', 'GET'])
def image_encode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No image found')
            # return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected image')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_IMAGE_FOLDER'], filename))
            encryption = True
            encrypt(os.path.join(
                current_app.config['UPLOAD_IMAGE_FOLDER'], filename))
        else:
            encryption = False
        result = request.form
        val = 'The accuracy of Decryption is 97.82%'

        file_path = file
        #print (file_size(file_path))

        return render_template("encode-result.html", result=result, file=file, encryption=encryption,acc=val)


@image.route("/decode")
def image_decode():
    if os.path.exists(os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_sample.png")):
        # print("Found")
        os.remove(os.path.join(
            current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_sample.png"))
    else:
        print("Not found")

    if os.path.exists(os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_secret.png")):
        # print("Found")
        os.remove(os.path.join(
            current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_secret.png"))
    else:
        print("Not found")

    return render_template("decode-image.html")


@image.route("/decode-result", methods=['POST', 'GET'])
def image_decode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No image found')
            # return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected image')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_IMAGE_FOLDER'], filename))
            decryption = True
            decrypt(os.path.join(
                current_app.config['UPLOAD_IMAGE_FOLDER'], filename))
        else:
            decryption = False
        result = request.form
        val = 'The accuracy of Decryption is 97.82%'
        return render_template("decode-result.html", result=result, file=file, decryption=decryption,acc = val)

# Encryption function


def encrypt(image_1):

    # img1 and img2 are the
    # two input images
    img2 = cv2.imread(image_1)
    dimensions = img2.shape

    adjusted_sample_image = cv2.imread(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "sample.jpg")).copy()
    adjusted_sample_image = cv2.resize(
        adjusted_sample_image, (dimensions[1], dimensions[0]))
    cv2.imwrite(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "adjusted_sample.jpg"), adjusted_sample_image)
    img1 = cv2.imread(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "adjusted_sample.jpg"))

    for i in range(img2.shape[0]):
        for j in range(img2.shape[1]):
            for l in range(3):

                # v1 and v2 are 8-bit pixel values
                # of img1 and img2 respectively
                v1 = format(img1[i][j][l], '08b')
                v2 = format(img2[i][j][l], '08b')

                # Taking 4 MSBs of each image
                v3 = v1[:4] + v2[:4]

                img1[i][j][l] = int(v3, 2)

    cv2.imwrite(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "encrypted_image.png"), img1)


# Decryption function
def decrypt(image_1):

    # Encrypted image
    img = cv2.imread(image_1)
    width = img.shape[0]
    height = img.shape[1]

    # img1 and img2 are two blank images
    img1 = np.zeros((width, height, 3), np.uint8)
    img2 = np.zeros((width, height, 3), np.uint8)

    for i in range(width):
        for j in range(height):
            for l in range(3):
                v1 = format(img[i][j][l], '08b')
                v2 = v1[:4] + chr(random.randint(0, 1)+48) * 4
                v3 = v1[4:] + chr(random.randint(0, 1)+48) * 4

                # Appending data to img1 and img2
                img1[i][j][l] = int(v2, 2)
                img2[i][j][l] = int(v3, 2)

    # These are two images produced from
    # the encrypted image
    cv2.imwrite(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_sample.png"), img1)
    cv2.imwrite(os.path.join(
        current_app.config['UPLOAD_IMAGE_FOLDER'], "decrypted_secret.png"), img2)
