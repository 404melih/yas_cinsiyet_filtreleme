import cv2

cap = cv2.VideoCapture("1.mp4.mp4")
if not cap.isOpened():
    print("Failed to open video source")
else:
    print("Video source opened successfully")
cap.release()
