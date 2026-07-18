import os
import shutil
import yaml

DATA_DIR = r"E:\CareLens_AI\data"
MERGED_DIR = os.path.join(DATA_DIR, "merged_dataset")
DATASETS = ["indoor_obstacles", "stairs", "clutter", "medicine"]
SPLITS = ["train", "valid", "test"]

def main():
    print("--- Starting Dataset Merging Process ---")
    
    # 1. Collect all classes and create a global mapping
    global_classes = []
    dataset_class_maps = {} # maps dataset_name -> {local_id: global_id}
    
    for ds_name in DATASETS:
        yaml_path = os.path.join(DATA_DIR, ds_name, "data.yaml")
        if not os.path.exists(yaml_path):
            print(f"Warning: {yaml_path} not found.")
            continue
            
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            
        local_classes = data.get('names', [])
        local_map = {}
        
        for i, cls_name in enumerate(local_classes):
            if isinstance(cls_name, int) or isinstance(local_classes, dict):
                # Handle different YAML formats if it's a dict instead of list
                if isinstance(local_classes, dict):
                    cls_name = local_classes[i]
                    
            if cls_name not in global_classes:
                global_classes.append(cls_name)
            
            global_id = global_classes.index(cls_name)
            local_map[i] = global_id
            
        dataset_class_maps[ds_name] = local_map
        print(f"Mapped {len(local_classes)} classes for '{ds_name}'")

    print(f"\nTotal unique classes across all datasets: {len(global_classes)}")
    
    # 2. Create merged directory structure
    if os.path.exists(MERGED_DIR):
        print("Clearing existing merged_dataset directory...")
        shutil.rmtree(MERGED_DIR)
        
    for split in SPLITS:
        os.makedirs(os.path.join(MERGED_DIR, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(MERGED_DIR, split, "labels"), exist_ok=True)
        
    # 3. Copy files and remap labels
    total_images_copied = 0
    for ds_name in DATASETS:
        print(f"\nProcessing dataset: {ds_name}...")
        local_map = dataset_class_maps.get(ds_name)
        if not local_map:
            continue
            
        for split in SPLITS:
            img_dir = os.path.join(DATA_DIR, ds_name, split, "images")
            lbl_dir = os.path.join(DATA_DIR, ds_name, split, "labels")
            
            if not os.path.exists(img_dir):
                continue
                
            for img_file in os.listdir(img_dir):
                # Ensure unique filenames by prefixing dataset name
                new_basename = f"{ds_name}_{img_file}"
                src_img = os.path.join(img_dir, img_file)
                dst_img = os.path.join(MERGED_DIR, split, "images", new_basename)
                
                # Copy Image
                shutil.copy2(src_img, dst_img)
                total_images_copied += 1
                
                # Process Label
                base_name_no_ext = os.path.splitext(img_file)[0]
                src_lbl = os.path.join(lbl_dir, f"{base_name_no_ext}.txt")
                dst_lbl = os.path.join(MERGED_DIR, split, "labels", f"{ds_name}_{base_name_no_ext}.txt")
                
                if os.path.exists(src_lbl):
                    with open(src_lbl, 'r') as f_in, open(dst_lbl, 'w') as f_out:
                        for line in f_in:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                local_id = int(parts[0])
                                global_id = local_map[local_id]
                                new_line = f"{global_id} " + " ".join(parts[1:]) + "\n"
                                f_out.write(new_line)
                else:
                    # Create empty label file if none exists
                    open(dst_lbl, 'w').close()

    # 4. Generate master data.yaml
    master_yaml = {
        'train': '../train/images',
        'val': '../valid/images',
        'test': '../test/images',
        'nc': len(global_classes),
        'names': global_classes
    }
    
    yaml_path = os.path.join(MERGED_DIR, "data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(master_yaml, f, sort_keys=False)
        
    print(f"\n--- Merge Complete ---")
    print(f"Total images merged: {total_images_copied}")
    print(f"Master dataset saved to: {MERGED_DIR}")

if __name__ == "__main__":
    main()
