from PIL import Image
import numpy as np
import base64
from io import BytesIO


def process_image(image):
    img_bytes = base64.b64decode(image)
    img = Image.open(BytesIO(img_bytes))
    processed_img = img.resize(
        (256, 192), resample=Image.ANTIALIAS).convert("RGB")
    processed_img = np.asarray(processed_img)
    processed_img = processed_img.astype("float32")
    processed_img /= 255
    processed_img = processed_img.reshape(1, 192, 256, 3)
    return processed_img


def model_predict(model, image):
    processed_img = process_image(image)
    score = model.predict(processed_img)
    print("Model Predictions: ", score)
    prediction = np.argmax(score)
    confidence = np.max(score)
    return confidence, prediction


def decode_image_to_save(data):
    data = base64.b64decode(data)
    buf = BytesIO(data)
    img = Image.open(buf)
    return img
