import pyrealsense2 as rs
import numpy as np
import pyttsx3
import threading
import time
import argparse
import cv2
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
        print(f"\n[AUDIO SIMULATION] AI whispers: '{text}'")
        engine.say(text)
        engine.runAndWait()
        is_speaking = False

# --- YOLO SETUP ---
model = YOLO('yolov8s.pt')

# --- REALSENSE SETUP ---
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
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
        annotated_frame = frame.copy()
        
        # Run YOLO Detection
        results = model(frame, conf=0.45, verbose=False)
        
        current_time = time.time()
        
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Check if this object is the one we are looking for!
            if class_name == args.target:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                # Get distance
                distance_meters = depth_frame.get_distance(center_x, center_y)
                
                # --- GTA 5 VISUAL WAYPOINT ---
                # Draw a bright blue dot (BGR format: Blue is 255, Green 0, Red 0)
                cv2.circle(annotated_frame, (center_x, center_y), 15, (255, 0, 0), -1)
                cv2.circle(annotated_frame, (center_x, center_y), 25, (255, 255, 255), 3) # White border
                cv2.putText(annotated_frame, f"TARGET: {distance_meters:.1f}m", (center_x - 60, center_y - 35), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Audio cooldown logic: only speak directions every 3 seconds
                if (current_time - last_spoken_time) > 3.0:
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
                
        # Show the video window with the Blue Dot
        cv2.imshow(f"CareLens - Navigating to {args.target}", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
