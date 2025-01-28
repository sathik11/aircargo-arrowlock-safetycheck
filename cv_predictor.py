import os
import cv2
import numpy as np
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from skimage.metrics import structural_similarity as compare_ssim
from msrest.authentication import ApiKeyCredentials
from PIL import Image, ImageDraw

from dotenv import load_dotenv
#load_dotenv(dotenv_path='/home/sathik/code/sats/sats-cargo-belly/.env.local')
load_dotenv()

cv_endpoint = os.getenv("CV_ENDPOINT")
cv_key = os.getenv("CV_PREDICTION_KEY")
cv_prediction_id = os.getenv("CV_PREDICTION_RESOURCE_ID")
cv_iteration = os.getenv("CV_ITERATION_NAME")

cv_creds = {"endpoint": cv_endpoint, 
        "key": cv_key,
        "pred_resource": cv_prediction_id,
        "pred_iteration": cv_iteration}


def predict_annotation_cv(cv_creds, img_fullpath):
    print(cv_creds)
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": cv_creds["key"]})
    predictor = CustomVisionPredictionClient(cv_creds["endpoint"], prediction_credentials)
    # print(img_fullpath)
    with open(img_fullpath,"rb") as img_data:
        results = predictor.detect_image(cv_creds["pred_resource"], cv_creds["pred_iteration"], img_data)

    bounding_boxes = []    
    for prediction in results.predictions:
        if prediction.probability > 0.95:
            bbox = {'bbox_left': prediction.bounding_box.left, 
                    'bbox_top': prediction.bounding_box.top, 
                    'bbox_width': prediction.bounding_box.width, 
                    'bbox_height': prediction.bounding_box.height}
            bounding_boxes.append(bbox)
    return bounding_boxes

def get_combined_bbox(bboxes):
    x_min = min([bbox[0] for bbox in bboxes])
    y_min = min([bbox[1] for bbox in bboxes])
    x_max = max([bbox[2] for bbox in bboxes])
    y_max = max([bbox[3] for bbox in bboxes])
    return (x_min, y_min, x_max, y_max)

def crop_region(img, combined_bbox, zoom=True, zoom_factor=2):
    x1, y1, x2, y2 = combined_bbox
    cropped_img = img[y1:y2, x1:x2]
        # Resize (zoom) the cropped image
    if zoom:
        height, width = cropped_img.shape[:2]
        zoomed_img = cv2.resize(cropped_img, (width * zoom_factor, height * zoom_factor), interpolation=cv2.INTER_LINEAR)
        enhance_img = enhance_colors(zoomed_img, enhance_factor=2)
    return enhance_img

def convert_bboxes(normalized_bboxes, img_width, img_height):
    bboxes = []
    for bbox in normalized_bboxes:
        x1 = int(bbox['bbox_left'] * img_width)
        y1 = int(bbox['bbox_top'] * img_height)
        x2 = int((bbox['bbox_left'] + bbox['bbox_width']) * img_width)
        y2 = int((bbox['bbox_top'] + bbox['bbox_height']) * img_height)
        bboxes.append((x1, y1, x2, y2))
    return bboxes


def enhance_colors(img, enhance_factor=1.5):
    # Convert the image to HSV color space
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Split the HSV channels
    h, s, v = cv2.split(hsv_img)
    # Enhance the saturation and value channels
    s = cv2.multiply(s, enhance_factor)
    v = cv2.multiply(v, enhance_factor)
    # Merge the channels back
    enhanced_hsv = cv2.merge([h, s, v])
    # Convert back to BGR color space
    enhanced_img = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
    return enhanced_img

def sharpen_image(img):
    # Define the sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    # Apply the sharpening kernel to the image
    sharpened_img = cv2.filter2D(img, -1, kernel)
    return sharpened_img

def denoise_image(img):
    # Apply the denoising function
    denoised_img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    return denoised_img


def overlay_bbox_on_image(img_path, imgfile, output_img_path, bbox_list):
    image = Image.open(os.path.join(img_path,imgfile))
    # Convert hex color to BGR
    hex_color = "#0BFC86"
    bgr_color = tuple(int(hex_color[i:i+2], 16) for i in (5, 3, 1))
    # Get image dimensions
    image_width, image_height = image.size
    draw = ImageDraw.Draw(image)
    print(bbox_list)
    for bbox_coords in bbox_list:
        # Calculate the bounding box coordinates in pixel values
        x1 = int(bbox_coords['bbox_left'] * image_width)
        y1 = int(bbox_coords['bbox_top'] * image_height)
        x2 = int((bbox_coords['bbox_left'] + bbox_coords['bbox_width']) * image_width)
        y2 = int((bbox_coords['bbox_top'] + bbox_coords['bbox_height']) * image_height)

        # Draw the bounding box
        draw.rectangle([x1, y1, x2, y2], outline=bgr_color , width=2)

    # Save the image with all bounding boxes
    image.save(os.path.join(output_img_path, "bound_"+imgfile))
    
    img = cv2.imread(os.path.join(output_img_path, "bound_"+imgfile))

    bboxes = convert_bboxes(bbox_list, image_width, image_height)
    combined_bbox = get_combined_bbox(bboxes)
    cropped_img = crop_region(img, combined_bbox)

    cv2.imwrite(os.path.join(output_img_path, "cropped_"+imgfile), cropped_img)



# def sharpen_image(image_fullpath):
#     # Load the image
#     img = cv2.imread(image_fullpath)

#     # Define the sharpening kernel
#     kernel = np.array([[0, -1, 0],
#                     [-1, 5,-1],
#                     [0, -1, 0]])

#     # Apply the sharpening kernel to the image
#     sharpened = cv2.filter2D(img, -1, kernel)

#     # sr = cv2.dnn_superres.DnnSuperResImpl_create()
#     # sr.readModel('EDSR_x4.pb')
#     # sr.setModel('edsr', 4)
#     # sharpened = sr.upsample(img)

#     # # Apply the denoising function
#     # sharpened = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
#     # Save the result
#     cv2.imwrite(image_fullpath.replace('.jpg','_sharp.jpg'), sharpened)

def render_bbox_aoai_img(raw_img_path = "./uploads", aoai_img_path="./uploads"):
    # print(cv_creds)
    for imgfile in os.listdir(raw_img_path):
        if imgfile.endswith(('.png', '.jpg', '.jpeg')):
            img_fullpath = os.path.join(raw_img_path,imgfile)

            # Enhance the image colors
            # Load the image
            img = cv2.imread(img_fullpath)

            # Step 1: Denoise the image
            # denoised_img = denoise_image(img)

            # Step 2: Enhance the colors
            # enhanced_img = enhance_colors(img, enhance_factor=1.5)

            # Step 3: Sharpen the image
            final_img = sharpen_image(img)

            # Save the final result
            cv2.imwrite(img_fullpath.replace('.jpg','_sharp.jpg'), final_img)

            bbox_list = predict_annotation_cv(cv_creds,img_fullpath.replace('.jpg','_sharp.jpg'))

            if bbox_list:
                overlay_bbox_on_image(raw_img_path, imgfile, aoai_img_path, bbox_list)
            else:
                image = Image.open(img_fullpath)
                image.save(os.path.join(aoai_img_path, imgfile))

        crop_img = "cropped_"+imgfile
        bbox_img = "bound_"+imgfile
        return bbox_img,crop_img
# render_bbox_aoai_img(cv_creds, raw_img_path, aoai_img_path)


# def compare_ssim_images(highres_imgs, output_dir):

#     img_old_cv = cv2.imread(highres_imgs[0])
#     img_new_cv = cv2.imread(highres_imgs[1])

#     grayA = cv2.cvtColor(img_old_cv, cv2.COLOR_BGR2GRAY)
#     grayB = cv2.cvtColor(img_new_cv, cv2.COLOR_BGR2GRAY)
#     (score, diff) = compare_ssim(
#         grayA,
#         grayB,
#         full=True,
#         gaussian_weights=True,
#         sigma=1.5,
#         use_sample_covariance=False,
#     )
#     diff = (diff * 255).astype("uint8")

#     kernel = np.ones((5, 5), np.uint8)
#     diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel, iterations=2)
#     diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel, iterations=2)
#     thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
#     thresh = cv2.dilate(thresh, kernel, iterations=2)

#     # Create a mask for the pink overlay
#     pink_overlay = np.zeros_like(img_new_cv)
#     pink_overlay[thresh == 255] = [255, 0, 255]  # BGR color for pink

#     # Blend the original image with the pink overlay to highlight differences
#     img_new_cv_writable = cv2.addWeighted(img_new_cv, 0.7, pink_overlay, 0.3, 0)
#     comparison_path = os.path.join(output_dir, "ssim_comparison.png")
#     cv2.imwrite(comparison_path, img_new_cv_writable, [cv2.IMWRITE_PNG_COMPRESSION, 70])
#     return comparison_path