from roboflow import Roboflow

def download_dataset():
    print("Connecting to Roboflow...")
    # NOTE: You need to put your actual API key here!
    rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY_HERE")
    
    print("Downloading Indoor Obstacles Dataset...")
    # This is an example snippet. 
    # When you click 'Jupyter' on a specific dataset on Roboflow, 
    # replace this block with the code they provide!
    
    # project = rf.workspace("workspace-name").project("project-name")
    # version = project.version(1)
    # dataset = version.download("yolov8")
    
    print("Download complete!")

if __name__ == "__main__":
    download_dataset()
