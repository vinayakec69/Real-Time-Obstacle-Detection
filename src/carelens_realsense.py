import pyrealsense2 as rs
import numpy as np
import cv2
from ultralytics import YOLO

def main():
    print("--- CareLens AI: RealSense + YOLOv8 Started ---")
    
    # 1. Load the TensorRT Optimized Model
    # Make sure you run export_tensorrt.py first to generate this!
    try:
        model = YOLO("runs/detect/train-CareLens/weights/best.engine")
        print("Successfully loaded TensorRT engine.")
    except Exception as e:
        print("Could not load best.engine. Falling back to best.pt.")
        model = YOLO("runs/detect/train-CareLens/weights/best.pt")

    # 2. Configure Intel RealSense D435 Streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    
    # Enable Depth and RGB streams
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    profile = pipeline.start(config)

    # 3. Align depth frame to color frame
    # This is CRITICAL so that pixel (x,y) in RGB matches pixel (x,y) in Depth
    align_to = rs.stream.color
    align = rs.align(align_to)

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            
            # Align the depth frame to color frame
            aligned_frames = align.process(frames)
            
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            
            if not aligned_depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 4. Run YOLOv8 Inference on the RGB image
            results = model.predict(source=color_image, verbose=False)
            
            # 5. Process Detections and Calculate Distance
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]

                    # Calculate the center pixel of the bounding box
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    # Get distance in meters from the depth frame at the center pixel
                    distance = aligned_depth_frame.get_distance(center_x, center_y)

                    # 6. Draw on the image
                    # Draw Bounding Box
                    cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Draw center point
                    cv2.circle(color_image, (center_x, center_y), 4, (0, 0, 255), -1)
                    
                    # Create label with Class and Distance
                    label = f"{cls_name} ({conf:.2f}) | {distance:.2f}m"
                    cv2.putText(color_image, label, (x1, max(y1 - 10, 0)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # --- Future Logic for Audio Trigger Here ---
                    # if distance < 1.0 and cls_name == "stairs":
                    #     play_audio("Stairs ahead, less than 1 meter")

            # Show images
            cv2.imshow('CareLens AI - RealSense Vision', color_image)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
