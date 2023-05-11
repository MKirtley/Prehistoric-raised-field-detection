import os
import cv2
import numpy as np

from keras.models import load_model
from keras import backend as K
from skimage import io
from skimage.transform import resize


def preprocess_image(image):
    """
    Pre-processes the input image by removing the alpha channel, resizing it,
    and adding a batch channel. Required for feeding it into the CNN model.

    :param image: The input image.
    :return: The pre-processed image.
    """
    # Remove the alpha channel.
    if image.shape[2] == 4:
        image = image[..., :3]
    
    # Resize image, and add the batch dimension to make it compatible with CNN.
    new_image_resized = resize(image, (512, 512))
    new_image_batch = np.expand_dims(new_image_resized, axis=0)
    
    return new_image_batch

def save_predicted_images(image, prediction, output_subfolder, threshold):
    """
    Saves the predicted mask, overlaid image, inverted mask, predicted probabilities,
    and inverted probabilities as image files in the output subfolder.

    :param image: The input image.
    :param prediction: The prediction obtained from the model.
    :param output_subfolder: The subfolder for the output images.
    :param threshold: The pixel probabilities level used to generate the binary mask from the prediction.
    """

    # Resize the image.
    resized_img = resize(image, (512, 512))

    # Apply threshold, remove dimension, and save the predicted mask.
    predicted_mask = (prediction > threshold).astype(np.uint8) * 255
    predicted_mask = predicted_mask.squeeze()
    io.imsave(os.path.join(output_subfolder, 'predicted_mask.png'), predicted_mask)

    # Save the overlaid image.
    overlaid_image = resized_img.copy()
    overlaid_image[predicted_mask > 0] = 255
    overlaid_image = np.clip(overlaid_image, 0, 1)
    io.imsave(os.path.join(output_subfolder, 'overlaid_image.png'), (overlaid_image * 255).astype(np.uint8))

    # Save the inverted predicted mask.
    inverted_mask = 1 - (predicted_mask / 255)
    io.imsave(os.path.join(output_subfolder, 'inverted_mask.png'), (inverted_mask * 255).astype(np.uint8))

    # Save the predicted probabilities.
    predicted_probabilities = prediction[0, ..., 0] * 1.5
    io.imsave(os.path.join(output_subfolder, 'predicted_probabilities.png'), (predicted_probabilities * 255).astype(np.uint8))

    # Save the inverted probabilities
    inverted_probabilities = 1 - predicted_probabilities
    io.imsave(os.path.join(output_subfolder, 'inverted_probabilities.png'), (inverted_probabilities * 255).astype(np.uint8))


def iou(y_true, y_pred):
    """
    Computes the Intersection over Union (IoU) metric.
    Required to perform inference on the model.
    Function taken from ZFTurbo's example - 
    https://github.com/ZFTurbo/ZF_UNET_224_Pretrained_Model/blob/master/zf_unet_224_model.py

    :param y_true: The ground truth mask.
    :param y_pred: The predicted mask.
    :return: The IoU score.
    """
    y_true_flatten = K.flatten(y_true)
    y_pred_flatten = K.flatten(y_pred)
    intersection = K.sum(y_true_flatten * y_pred_flatten)
    return (intersection + 1.0) / (K.sum(y_true_flatten) + K.sum(y_pred_flatten) - intersection + 1.0)


def adjust_threshold(val):
    """
    Adjusts the current threshold value and updates the displayed image based on the given value.

    :param val: The new value for the threshold.
    """
    # Declare global variables.
    global current_threshold, image, prediction, output_subfolder
    current_threshold = val / 100.0
    
    # Check if image is defined before trying to create an overlaid image.
    if 'image' in globals():
        overlaid_image = get_overlaid_image(image, prediction, current_threshold)
        cv2.imshow('Press S to confirm', overlaid_image)


def get_overlaid_image(image, prediction, threshold):
    """
    Generates an overlaid image based on the image, prediction, and threshold value.

    :param image: The image to be overlaid.
    :param prediction: The prediction mask generated by the model.
    :param threshold: The threshold value used for the prediction mask.
    :return: The overlaid image.
    """
    
    # Resize the image.
    resized_img = resize(image, (512, 512))

    # Set mask and remove dimension.
    predicted_mask = (prediction > threshold).astype(np.uint8) * 255
    predicted_mask = predicted_mask.squeeze()

    # Create the overlaid image.
    overlaid_image = resized_img.copy()
    overlaid_image[predicted_mask > 0] = 255
    overlaid_image = np.clip(overlaid_image, 0, 1)
    
    # Convert to BGR colour space. Required for OpenCV.
    overlaid_image_bgr = cv2.cvtColor((overlaid_image * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

    return overlaid_image_bgr


# Load in model.
print("Loading model...")
model = load_model('model/optimised_model_augmentation.hdf5', custom_objects={'iou': iou})
print("Model loaded.")

# Set folders.
input_folder = 'Input Images/'
output_folder = 'Output Folder/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialise global threshold value.
current_threshold = 0.20

# Create window and trackbar.
cv2.namedWindow('Press S to confirm')
cv2.createTrackbar('Threshold', 'Press S to confirm', int(current_threshold * 100), 100, adjust_threshold)

# Get paths to image files.
print('Reading images.')
for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)
        image = io.imread(image_path)
        
        # Prepare image for model inference.
        processed_image = preprocess_image(image)

        # Feed through model.
        prediction = model.predict(processed_image)

        # Creating a separate folder for each output file.
        output_subfolder = os.path.join(output_folder, os.path.splitext(filename)[0])
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        # Get overlaid image. Used for OpenCV window.
        overlaid_image = get_overlaid_image(image, prediction, current_threshold)
        
        cv2.imshow('Press S to confirm', overlaid_image)

        # Press S key to set threshold value, save images and move onto next image.
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                save_predicted_images(image, prediction, output_subfolder, current_threshold)
                break

cv2.destroyAllWindows()
print("Completed.")