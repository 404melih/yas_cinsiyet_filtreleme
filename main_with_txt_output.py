import cv2
import argparse
import warnings
import numpy as np

from models import SCRFD, Attribute
from utils.helpers import Face, draw_face_info

warnings.filterwarnings("ignore")

def load_models(detection_model_path: str, attribute_model_path: str):
    """Loads the detection and attribute models.
    Args:
        detection_model_path (str): Path to the detection model file.
        attribute_model_path (str): Path to the attribute model file.
    Returns
        tuple: A tuple containing the detection model and the attribute model.

    """
    try:
        detection_model = SCRFD(model_path=detection_model_path)
        attribute_model = Attribute(model_path=attribute_model_path)
    except Exception as e:
        print(f"Error loading models: {e}")
        raise
    return detection_model, attribute_model

def inference_image(detection_model, attribute_model, image_path, save_output, output_txt_path=None):
    """Processes a single image for face detection and attributes.
    Args:
        detection_model (SCRFD): The face detection model.
        attribute_model (Attribute): The attribute detection model.
        image_path (str): Path to the input image.
        save_output (str): Path to save the output image.
        output_txt_path (str): Path to save detection results in a text file.
    """
    frame = cv2.imread(image_path)
    if frame is None:
        print("Failed to load image")
        return

    process_frame(detection_model, attribute_model, frame, output_txt_path)
    if save_output:
        cv2.imwrite(save_output, frame)
    cv2.imshow("FaceDetection", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def inference_video(detection_model, attribute_model, video_source, save_output, output_txt_path=None):
    """Processes a video source for face detection and attributes.
    Args:
        detection_model (SCRFD): The face detection model.
        attribute_model (Attribute): The attribute detection model.
        video_source (str or int): Path to the input video file or camera index.
        save_output (str): Path to save the output video.
        output_txt_path (str): Path to save detection results in a text file.
    """
    if video_source.isdigit() or video_source == '0':
        cap = cv2.VideoCapture(int(video_source))
    else:
        cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Failed to open video source")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second
    frame_count = 0  # Initialize frame counter

    out = None
    if save_output:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(save_output, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    global_results = []  # Global list to store unique results

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_count / fps  # Calculate the timestamp in seconds
        process_frame(detection_model, attribute_model, frame, output_txt_path, current_time, global_results)

        if save_output:
            out.write(frame)

        frame_count += 1  # Increment frame count
        cv2.imshow("FaceDetection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    if save_output:
        out.release()
    cv2.destroyAllWindows()

    # Write final unique results to txt file
    if output_txt_path:
        with open(output_txt_path, "w") as f:
            for res in global_results:
                f.write(f"{res}\n")

def is_nearby(bbox1, bbox2, threshold=50):
    """Checks if two bounding boxes are nearby based on a distance threshold.
    Args:
        bbox1 (list): First bounding box [x1, y1, x2, y2].
        bbox2 (list): Second bounding box [x1, y1, x2, y2].
        threshold (int): Distance threshold to consider as nearby.
    Returns:
        bool: True if bounding boxes are nearby, False otherwise.
    """
    center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
    center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
    distance = np.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
    return distance < threshold

def process_frame(detection_model, attribute_model, frame, output_txt_path=None, current_time=None, global_results=None):
    """Detects faces and attributes in a frame and draws the information.
    Args:
        detection_model (SCRFD): The face detection model.
        attribute_model (Attribute): The attribute detection model.
        frame (np.ndarray): The image frame to process.
        output_txt_path (str): Path to save detection results in a text file.
        current_time (float): The timestamp of the current frame in seconds.
        global_results (list): Global list to store unique results.
    """
    boxes_list, points_list = detection_model.detect(frame)

    for boxes, keypoints in zip(boxes_list, points_list):
        *bbox, conf_score = boxes
        gender, age = attribute_model.get(frame, bbox)
        face = Face(kps=keypoints, bbox=bbox, age=age, gender=gender)
        draw_face_info(frame, face)

        # Check if this face is already in global results
        is_duplicate = False
        for cached_result in global_results:
            if is_nearby(bbox, cached_result['bbox']):
                is_duplicate = True
                break

        if not is_duplicate:
            result = {
                "bbox": bbox,
                "confidence": conf_score,
                "age": age,
                "gender": gender,
                "time": current_time  # Add timestamp here
            }
            global_results.append(result)

def run_face_analysis(detection_weights, attribute_weights, input_source, save_output=None, output_txt_path=None):
    """Runs face detection on the given input source.
    Args:
        detection_weights (str): Path to the detection model weights.
        attribute_weights (str): Path to the attribute model weights.
        input_source (str): Path to the input image, video, or camera index.
        save_output (str): Path to save the output image or video.
        output_txt_path (str): Path to save the detection results in a text file.
    """
    detection_model, attribute_model = load_models(detection_weights, attribute_weights)

    if isinstance(input_source, str) and input_source.lower().endswith(('.jpg', '.png', '.jpeg')):
        inference_image(detection_model, attribute_model, input_source, save_output, output_txt_path)
    else:
        inference_video(detection_model, attribute_model, input_source, save_output, output_txt_path)

def main():
    """Main function to run face detection from command line."""
    parser = argparse.ArgumentParser(description="Run face detection on an image or video")
    parser.add_argument(
        '--detection-weights',
        type=str,
        default="weights/det_10g.onnx",
        help='Path to the detection model weights file'
    )
    parser.add_argument(
        '--attribute-weights',
        type=str,
        default="weights/genderage.onnx",
        help='Path to the attribute model weights file'
    )
    parser.add_argument(
        '--source',
        type=str,
        default="assets/in_image.jpg",
        help='Path to the input image or video file or camera index (0, 1, ...)'
    )
    parser.add_argument('--output', type=str, help='Path to save the output image or video')
    parser.add_argument('--output-txt', type=str, help='Path to save output results in a text file')
    args = parser.parse_args()

    run_face_analysis(
        args.detection_weights,
        args.attribute_weights,
        args.source,
        args.output,
        args.output_txt
    )

if __name__ == "__main__":
    main()
