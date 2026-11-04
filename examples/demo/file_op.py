import os
import os.path as op

# Figure out base upload path
static_path = op.join(op.dirname(__file__), "static")


def remove_image(image_path):
    os.remove(op.join(static_path, image_path))


def save_image(file_data, image_path):
    file_data.save(op.join(static_path, image_path))
