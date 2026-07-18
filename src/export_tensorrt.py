from ultralytics import YOLO

def main():
    print("--- CareLens AI: TensorRT Export ---")
    print("Loading the trained model...")
    # Point this to wherever the 300-epoch training saved its best weights
    model = YOLO("runs/detect/train-CareLens/weights/best.pt")
    
    print("Exporting model to TensorRT engine format for the Orin Nano GPU...")
    # This will generate a 'best.engine' file in the same directory
    # It might take 10-15 minutes on the Orin Nano to compile the TensorRT graph!
    model.export(format="engine", device=0, half=True)
    
    print("Export complete! You can now use best.engine for ultra-fast inference.")

if __name__ == "__main__":
    main()
