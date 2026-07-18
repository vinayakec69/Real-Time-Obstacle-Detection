import pyrealsense2 as rs
import numpy as np
import cv2
import pyttsx3
import threading
import time
from ultralytics import YOLO

# --- AUDIO SETUP ---
engine = pyttsx3.init()
engine.setProperty('rate', 110) # Slower, conversational pace
is_speaking = False
last_spoken_time = {}

def speak_warning(text):
    global is_speaking
    if not is_speaking:
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        is_speaking = False

# --- YOLO SETUP ---
# Loading the highly capable base YOLOv8 model for flawless indoor detection
model = YOLO('yolov8s.pt')

# --- REALSENSE SETUP ---
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# --- VIDEO RECORDING SETUP ---
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('real_world_test.mp4', fourcc, 30.0, (640, 480))

print("CareLens AI is running! Press Q to quit.")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
            
        frame = np.asanyarray(color_frame.get_data())
        
        # We set confidence to 0.50 so it only speaks when it is VERY sure
        results = model(frame, conf=0.50, verbose=False)
        annotated_frame = results[0].plot()
        
        # Audio Logic
        current_time = time.time()
        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                # Cooldown of 4 seconds per object so it doesn't spam the speaker
                if class_name not in last_spoken_time or (current_time - last_spoken_time[class_name]) > 4.0:
                    last_spoken_time[class_name] = current_time
                    threading.Thread(target=speak_warning, args=(f"Watch out, there is a {class_name} in front of you.",)).start()
        
        # Save frame to the MP4 file
        out.write(annotated_frame)
        
        # Show on screen
        cv2.imshow("CareLens - Live Detection", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    out.release()
    cv2.destroyAllWindows()
