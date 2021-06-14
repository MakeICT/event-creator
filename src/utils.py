
import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def save_picture(form_picture, folder=''):
    if not form_picture:
        return False

    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = secure_filename(form_picture.filename)
    folder_path = os.path.join(current_app.root_path, 'static/event_images',
                               folder)
    picture_path = os.path.join(folder_path, picture_fn)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # output_size = (125, 125)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
