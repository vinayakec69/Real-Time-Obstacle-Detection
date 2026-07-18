from ultralytics import YOLO
import os

def main():
    print("--- Starting YOLOv8 Training Pipeline ---")
    
    # 1. Load the pre-trained YOLOv8 nano model
    model = YOLO("yolov8n.pt") 
    
    # 2. Define the path to our merged dataset YAML file
    yaml_path = os.path.abspath(r"E:\CareLens_AI\data\merged_dataset\data.yaml")
    
    print(f"Training on dataset configuration: {yaml_path}")
    
    # 3. Start Training
    # We set epochs=5 just to do a fast run and generate the graphs. 
    # You can change this to 50 or 100 later for high accuracy!
    results = model.train(
        data=yaml_path,
        epochs=5,
        imgsz=640,
        batch=16,
        plots=True, # This forces the generation of Confusion Matrix and PR curves
        project=r"E:\CareLens_AI\runs\detect", # Force output location
        name="train-CareLens"
    )
    
    print("\n--- Training Complete! ---")
    print("Check the 'runs/detect/train' folder for your confusion_matrix.png and results.png!")

if __name__ == "__main__":
    main()
