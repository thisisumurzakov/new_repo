# from cv2 import cv2
# import pytesseract
# import numpy as np
# import math
# import re
# from pytesseract import Output
# pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
#
#
# def create_file(file_name):
#     with open('/scr/firstproject/static/crm/upload/readme.txt', 'w') as f:
#         f.write(file_name)
#         f.close()
#
#
# def handle_uploaded_file(f):
#     file_name = f.name
#     create_file(file_name)
#     with open('Z:/PYTHON/try-django/scr/static/crm/upload/'+f.name, 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#
#
# def stage1(img, p_dict):
#     x, y = img.shape[1], img.shape[0]
#     x1, y1, h, w = int(0), int(y*0.17), int(x*0.7), int(y*0.44)
#     img = cv2.rectangle(img, (x1, y1), (h, w), (0, 255, 0), 2)
#     img1 = img[y1:w, x1:h]
#     # d = pytesseract.image_to_data(img, output_type= Output.DICT)
#     # n_boxes = len(d['text'])
#     # for i in range(n_boxes):
#     #     if int(float(d['conf'][i])) > 50:
#     #         (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#     #         img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
#     ss = pytesseract.image_to_string(img1).strip().split('\n')
#     pattern = r"[0-9]{2}[. _]{1}[0-9]{2}[. _]{1}[1-2]{1}[0-9]{3}"
#     # print(ss)
#     for i in ss:
#         if re.match(pattern, i):
#             p_dict['item1'] = ".".join(i[:10].split())
#             p_dict['item2'] = i[11:]
#
#     # cv2.imwrite('card1.jpg', img1)
#
#
# def stage2(img, p_dict):
#     x, y = img.shape[1], img.shape[0]
#     x1, y1, h, w = int(x*0.31), int(y*0.77), int(x*0.6), int(y*0.88)
#     img = cv2.rectangle(img, (x1, y1), (h, w), (0, 255, 0), 2)
#     pattern = r"[0-9]{2}[. _]{1}[0-9]{2}[. _]{1}[1-2]{1}[0-9]{3}"
#     img1 = img[y1:w, x1:h]
#     ss = pytesseract.image_to_string(img1).strip().split('\n')
#     temp = []
#     for i in ss:
#         if re.match(pattern, i):
#             temp.append(i[:10])
#
#     p_dict['item3'] = ".".join(temp[0].split())
#     p_dict['item4'] = ".".join(temp[1].split())
#     # cv2.imwrite('card2.jpg', img)
#     # print(ss)
#     # print(f"Date od Issue: {temp[0]}\nDate of Expiry: {temp[1]}")
#
#
# def stage3(img, p_dict):
#     x, y = img.shape[1], img.shape[0]
#     x1, y1, h, w = int(0), int(y*0.88), int(x), int(y)
#     img = cv2.rectangle(img, (x1, y1), (h, w), (0, 255, 0), 2)
#     img1 = img[y1:w, x1:h]
#     ss = pytesseract.image_to_string(img1).strip().split('\n')
#     pattern = r'^[A-Z][A-Z][0-9]{8}UZB.'
#     for i in ss:
#         if re.match(pattern, i):
#             p_dict['item5'] = i[:9]
#             # print(f"Серия паспорта: {i[:9]}")
#
#     # cv2.imwrite('card3.jpg', img1)
#
#
# def recognition():
#     file_name = open('/scr/firstproject/static/crm/upload/readme.txt', 'r').read()
#
#     img = cv2.imread('Z:/PYTHON/try-django/scr/static/crm/upload/'+file_name, 1)
#     print(f"img shape: {img.shape}\n")
#     img_copy = img.copy()
#     img_canny = cv2.Canny(img_copy, 50, 100, apertureSize=3)
#     img_hough = cv2.HoughLinesP(img_canny, 1, math.pi / 180, 100, minLineLength=100, maxLineGap=10)
#
#     (x, y, w, h) = (np.amin(img_hough, axis=0)[0, 0], np.amin(img_hough, axis=0)[0, 1], np.amax(img_hough, axis=0)[0, 0] -
#                     np.amin(img_hough, axis=0)[0, 0], np.amax(img_hough, axis=0)[0, 1] - np.amin(img_hough, axis=0)[0, 1])
#     img = img[y:y+h, x:x+w]
#     # cv2.imshow("card2", img)
#     # cv2.waitKey(0)
#     p_dict = {}
#     stage1(img, p_dict)
#     stage2(img, p_dict)
#     stage3(img, p_dict)
#     return p_dict
#
