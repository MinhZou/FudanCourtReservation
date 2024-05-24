import cv2
import numpy as np



def get_c(img):
    BGR = np.array([192, 192, 192])
    B = int(BGR[0])
    G = int(BGR[1])
    R = int(BGR[2])

    upRange = 10
    if 255 - B < upRange:
        upRange = 255 - B
    if 255 - G < upRange:
        upRange = 255 - G
    if 255 - R < upRange:
        upRange = 255 - R

    lowRange = 10
    if B - lowRange < 0:
        lowRange = B
    if G - lowRange < 0:
        lowRange = G
    if R - lowRange < 0:
        lowRange = R

    upper = BGR + upRange
    lower = BGR - lowRange

    mask = cv2.inRange(img, lower, upper)
    (contours, hierarchy) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_dis(img_path):
    image_raw = cv2.imread(img_path)
    image_height, image_width, _ = image_raw.shape
    contours = get_c(image_raw)
    offset = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w*h < 200:
            continue
        cv2.rectangle(image_raw, (x, y), (x + w, y + h), (0, 0, 255), 1)
        offset = x - int(w /2) + 3
    cv2.imwrite('image_label.png', image_raw)
    return offset

def get_dis_cv(byte_data):
    np_data = np.frombuffer(byte_data, np.uint8)
    image_raw = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    src_image_height, src_image_width, _ = image_raw.shape
    resized_image = cv2.resize(image_raw, (270, 116))
    image_height, image_width, _ = resized_image.shape
    contours = get_c(resized_image)
    offset = None
    max_offset = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        print(x, y, w, h)
        if w*h < 200:
            continue
        offset = x - int(w /2) + 3
    wbili = image_width / src_image_width
    return offset, wbili


def get_dis_bg_bl(bg_byte_data, bl_byte_data):
    bg_np_data = np.frombuffer(bg_byte_data, np.uint8)
    bg_image_raw = cv2.imdecode(bg_np_data, cv2.IMREAD_COLOR)
    bg_image_gray = cv2.cvtColor(bg_image_raw, cv2.COLOR_BGR2GRAY)

    bl_np_data = np.frombuffer(bl_byte_data, np.uint8)
    bl_image_raw = cv2.imdecode(bl_np_data, cv2.IMREAD_COLOR)
    bl_image_gray = cv2.cvtColor(bl_image_raw, cv2.COLOR_BGR2GRAY)

    # res = cv2.matchTemplate(bl_image_gray,bl_image_gray,cv2.TM_CCOEFF_NORMED)
    res = cv2.matchTemplate(bg_image_raw,bl_image_raw,cv2.TM_CCOEFF_NORMED)
    print(res)
    location = cv2.minMaxLoc(res)
    print(location)
    x = location[2][0]

    bg_src_image_height, bg_src_image_width, _ = bg_image_raw.shape
    bl_src_image_height, bl_src_image_width, _ = bl_image_raw.shape
    print(bl_src_image_height, bl_src_image_width)
    bg_resized_image = cv2.resize(bg_image_raw, (270, 116))
    bg_image_height, bg_image_width, _ = bg_resized_image.shape

    wbili = bg_image_width / bg_src_image_width
    offset = int(wbili*x)
    return offset, wbili
