import base64
from io import BytesIO


import imutils
# import numpy as np
from PIL import Image
from imutils import face_utils

# FILE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SHAPE_PREDICTOR_FILE = os.path.join(FILE_DIR, 'files/shape_predictor_68_face_landmarks.dat')
# predictor = dlib.shape_predictor(SHAPE_PREDICTOR_FILE)
from foodshow.ocr_core import ocr_core

# detector = dlib.get_frontal_face_detector()


def base64_decode(data):
    format, imgstr = data.split(';base64,')
    return imgstr


def base64_encode(data):
    if data:
        return 'data:image/png;base64,' + data


def get_face_detect_data(data):
    # print('get face data')

    # nothing under is running....
    # find out why.. print in the pther one..
    nparr = np.fromstring(base64_decode(data), np.uint8)
    # print(nparr)

    # logic to get this data to the processor...

    image = imutils.resize(nparr, width=500)
    extracted_text = ocr_core(image)
    trial_output = str(extracted_text)
    # print(trial_output)
    return trial_output

    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # print(img)

    # image_data = detectImage(img)
    # return base64_encode(image_data)





# or never turn to a string in the first place...
# somehere here import image...
# need to base 64 decode to n image...
# extracted_text = ocr_core(data)
#         trial_output = str(extracted_text)
#         print(trial_output)




def detectImage(image):
    image = imutils.resize(image, width=500)
    extracted_text = ocr_core(image)
    trial_output = str(extracted_text)
    print(trial_output)
    return trial_output
    # rects = detector(image, 1)
    # for (i, rect) in enumerate(rects):
    #     (x, y, w, h) = face_utils.rect_to_bb(rect)
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #     cv2.putText(image, "Face".format(i + 1), (x - 10, y - 10),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # if rects:
    # output = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # buffer = BytesIO()
    # img = Image.fromarray(output)
    # img.save(buffer, format="png")
    # encoded_string = base64.b64encode(buffer.getvalue())
    # return encoded_string
