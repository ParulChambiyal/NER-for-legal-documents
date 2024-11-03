# import easyocr
# import cv2
# import matplotlib.pyplot as plt
# import flask


# reader = easyocr.Reader(['hi', 'en'])

# print("OCR LIBRARIES SET.")

# image_path = 'Hindi_pic.jpg'
# image = cv2.imread(image_path)

# print("IMAGE LOADED!!!!!!!")
# results = reader.readtext(image_path)

# plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
# plt.axis('off')
# plt.show()

# for (bbox, text, prob) in results:
#     print(f'Text: {text}, Probability: {prob}')