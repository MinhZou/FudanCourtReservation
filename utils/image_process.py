import base64
import re
from PIL import Image
from io import BytesIO


def base64_to_image(base64_str, image_path=None):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    # image_data = BytesIO(byte_data)
    # img = Image.open(image_data)
    # if image_path:
    #     img.save(image_path)
    return byte_data