import pyrealsense2 as rs
import numpy as np
import pyttsx3
import threading
import time
import argparse
from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument('--target', type=str, default="cell phone", help='Target object to navigate towards')
args = parser.parse_args()

# --- AUDIO SETUP ---
engine = pyttsx3.init()
engine.setProperty('rate', 110)
is_speaking = False
last_spoken_time = 0

def speak_navigation(text):
    global is_speaking
    if not is_speaking:
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        is_speaking = False

# --- YOLO SETUP ---
model = YOLO('yolov8s.pt')

# --- REALSENSE SETUP ---
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30) # Enable depth sensor!
pipeline.start(config)

print(f"CareLens Navigation Mode running! Searching for: {args.target}")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        
        if not color_frame or not depth_frame:
            continue
            
        frame = np.asanyarray(color_frame.get_data())
        
        # Run YOLO Detection
        results = model(frame, conf=0.45, verbose=False)
        
        current_time = time.time()
        
        # Audio cooldown logic: only speak directions every 3 seconds
        if (current_time - last_spoken_time) > 3.0:
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                # Check if this object is the one we are looking for!
                if class_name == args.target:
                    # GTA 5 Spatial Logic (Left, Right, Center)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    center_x = (x1 + x2) / 2
                    center_y = int((y1 + y2) / 2)
                    
                    # Calculate distance in meters using the RealSense Depth Sensor
                    distance_meters = depth_frame.get_distance(int(center_x), center_y)
                    
                    if distance_meters > 0 and distance_meters < 0.6:
                        threading.Thread(target=speak_navigation, args=(f"You have reached your {args.target}.",)).start()
                    elif center_x < 213:
                        threading.Thread(target=speak_navigation, args=(f"{args.target} detected. Turn left.",)).start()
                    elif center_x > 426:
                        threading.Thread(target=speak_navigation, args=(f"{args.target} detected. Turn right.",)).start()
                    else:
                        threading.Thread(target=speak_navigation, args=(f"{args.target} is straight ahead.",)).start()
                    
                    last_spoken_time = current_time
                    break # Stop looping over boxes once we find the target
finally:
    pipeline.stop()
