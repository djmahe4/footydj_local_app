I'll help you understand how to use this `SoccerNetDataset` class for training different models. Let me break down the solutions: 

## Overview

Your current `SoccerNetDataset` class is designed for **object detection** only. To train the three different models you mentioned, you'll need to:

1. **Ball Detection** - Filter for ball class only
2. **Player Detection** - Combine goalkeeper, player, and referee classes
3. **Pitch Lines Segmentation** - This requires a different approach (segmentation task)

## Solution

Here's how to modify and use the dataset for each task:

### 1. Enhanced Dataset Class with Filtering

First, let's create an enhanced version that supports class filtering:

```python name=custom_soccernet_dataset.py
# Add this method to your SoccerNetDataset class

class SoccerNetDataset(YOLODataset):
    # ... existing code ...
    
    def __init__(self, *args, data:  dict | None = None, task: str = "detect", 
                 class_filter: list[int] | None = None, class_mapping: dict[int, int] | None = None, **kwargs):
        """
        Initialize the SoccerNetDataset. 

        Args:
            data (dict, optional): Dataset configuration dictionary with class names. 
            task (str): Task type, 'detect' or 'segment'.
            class_filter (list[int], optional): List of class IDs to keep.  If None, keep all. 
            class_mapping (dict[int, int], optional): Map original class IDs to new ones.
            *args (Any): Additional positional arguments for the parent class.
            **kwargs (Any): Additional keyword arguments for the parent class. 
        """
        self.class_filter = class_filter
        self.class_mapping = class_mapping or {}
        
        # Default class names if not provided
        if data is None:
            data = {
                "names": {
                    0: "ball",
                    1: "player",
                    2: "goalkeeper",
                    3: "referee",
                    4: "staff",
                    5: "other",
                    6: "pitch",
                }
            }

        super().__init__(*args, data=data, task=task, **kwargs)

    def cache_labels(self, path: Path = Path("./labels.cache")) -> dict:
        """
        Cache dataset labels by reading JSON files from the SoccerNet structure. 
        Applies class filtering and remapping if specified.

        Args:
            path (Path): Path where to save the cache file.

        Returns:
            (dict): Dictionary containing cached labels and related information.
        """
        x = {"labels": []}
        nm, nf, ne, nc, msgs = 0, 0, 0, 0, []

        # Group images by sequence
        img_by_sequence = defaultdict(list)
        json_files = {}

        for img_file in self.im_files:
            img_path = Path(img_file)
            seq_dir = img_path.parent.parent
            seq_name = seq_dir.name
            img_by_sequence[seq_name].append(img_file)

            json_file = seq_dir / f"Labels-GameState.json"
            if json_file.exists():
                json_files[seq_name] = json_file

        desc = f"{self.prefix}Loading SoccerNet annotations..."

        for seq_name in tqdm(sorted(img_by_sequence.keys()), desc=desc):
            if seq_name not in json_files:
                msgs.append(f"Missing JSON file for sequence {seq_name}")
                nm += len(img_by_sequence[seq_name])
                continue

            try:
                with open(json_files[seq_name], "r") as f:
                    data = json.load(f)

                img_annotations = defaultdict(list)
                for ann in data["annotations"]:
                    img_annotations[ann["image_id"]].append(ann)

                img_info_map = {img["image_id"]:  img for img in data["images"]}

                for img_file in img_by_sequence[seq_name]:
                    img_path = Path(img_file)
                    file_name = img_path.name

                    img_info = None
                    for info in data["images"]: 
                        if info["file_name"] == file_name:
                            img_info = info
                            break

                    if img_info is None:
                        nm += 1
                        continue

                    h = img_info["height"]
                    w = img_info["width"]
                    image_id = img_info["image_id"]

                    anns = img_annotations.get(image_id, [])

                    if not anns:
                        ne += 1
                        continue

                    bboxes = []

                    for ann in anns: 
                        cls = ann["category_id"]
                        
                        # Apply class filter
                        if self.class_filter is not None and cls not in self.class_filter:
                            continue
                        
                        # Apply class mapping
                        if self.class_mapping: 
                            cls = self.class_mapping.get(cls, cls)

                        bbox = ann.get("bbox_image", {})
                        if not bbox:
                            continue

                        x_center = bbox.get("x_center", 0.0)
                        y_center = bbox.get("y_center", 0.0)
                        bbox_w = bbox.get("w", 0)
                        bbox_h = bbox.get("h", 0)

                        if bbox_w > 1 or bbox_h > 1:
                            x_center = (bbox.get("x", 0) + bbox_w / 2) / w
                            y_center = (bbox.get("y", 0) + bbox_h / 2) / h
                            bbox_w = bbox_w / w
                            bbox_h = bbox_h / h

                        if bbox_w <= 0 or bbox_h <= 0:
                            continue

                        bboxes.append([cls, x_center, y_center, bbox_w, bbox_h])

                    if not bboxes: 
                        ne += 1
                        continue

                    lb = np.array(bboxes, dtype=np.float32)

                    x["labels"].append({
                        "im_file": str(img_file),
                        "shape": (h, w),
                        "cls":  lb[:, 0:1],
                        "bboxes": lb[:, 1:],
                        "segments": [],
                        "keypoints": None,
                        "normalized": True,
                        "bbox_format": "xywh",
                    })
                    nf += 1

            except Exception as e:
                msgs.append(f"Error processing {seq_name}: {str(e)}")
                nc += 1

        if msgs:
            LOGGER.info("\n".join(msgs))

        if nf == 0:
            LOGGER.warning(f"{self.prefix}No labels found in {path}. {HELP_URL}")

        x["hash"] = get_hash(self.im_files)
        x["results"] = nf, nm, ne, nc, len(self.im_files)
        x["msgs"] = msgs
        
        # Include filter info in cache
        cache_suffix = ""
        if self.class_filter:
            cache_suffix = f"_filter_{'_'.join(map(str, self.class_filter))}"
        
        save_dataset_cache_file(self.prefix, path, x, DATASET_CACHE_VERSION)

        LOGGER.info(
            f"{self.prefix}Successfully loaded {nf} images with annotations, "
            f"{nm} missing, {ne} empty, {nc} corrupt"
        )

        return x
```

### 2. Training Configuration Files

Create separate YAML configuration files for each task: 

````yaml name=ball_detection.yaml
# Ball Detection Configuration
path: /path/to/your/soccernet/dataset  # dataset root dir
train: train  # train images (relative to 'path')
val: valid    # val images (relative to 'path')

# Classes
names:
  0: ball

# Training settings
nc: 1  # number of classes
```

```yaml name=player_detection.yaml
# Player Detection Configuration  
path: /path/to/your/soccernet/dataset
train:  train
val: valid

# Classes (remapped)
names:
  0: player  # includes player, goalkeeper, referee

nc: 1
````

````yaml name=pitch_segmentation. yaml
# Pitch Segmentation Configuration
path: /path/to/your/soccernet/dataset
train: train
val: valid

# Classes
names:
  0: pitch

nc: 1
task: segment  # segmentation task
````

### 3. Training Scripts

Create training scripts for each model:

```python name=train_ball_detection.py
from ultralytics import YOLO
from custom_soccernet_dataset import SoccerNetDataset

# Ball detection - class 0 only
def train_ball_detector():
    # Create model
    model = YOLO('yolov8n.pt')  # or yolov8s. pt, yolov8m.pt, etc.
    
    # Train with custom dataset
    results = model.train(
        data='ball_detection.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        name='ball_detection',
        # Custom dataset loader
        dataset_class=SoccerNetDataset,
        # Filter for ball only (class 0)
        class_filter=[0],
        data_dict={
            "names": {0: "ball"}
        }
    )
    
    return results

if __name__ == '__main__':
    train_ball_detector()
```

```python name=train_player_detection.py
from ultralytics import YOLO
from custom_soccernet_dataset import SoccerNetDataset

# Player detection - combine classes 1, 2, 3
def train_player_detector():
    model = YOLO('yolov8n.pt')
    
    # Map goalkeeper (2), player (1), and referee (3) all to class 0 (player)
    class_mapping = {
        0: 0,
        1: 1,  # player -> player
        2: 2,  # goalkeeper -> player
        3: 3,  # referee -> player
    }
    
    results = model.train(
        data='player_detection.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        name='player_detection',
        dataset_class=SoccerNetDataset,
        # Filter for player-related classes
        class_filter=[1, 2, 3],
        class_mapping=class_mapping,
        data_dict={
            "names": {0: "player"}
        }
    )
    
    return results

if __name__ == '__main__':
    train_player_detector()
```

### 4. Alternative: Manual Dataset Creation

If the above integration doesn't work with Ultralytics' training pipeline, create a wrapper script:

```python name=create_filtered_datasets.py
import shutil
from pathlib import Path
from custom_soccernet_dataset import SoccerNetDataset

def create_ball_dataset(source_path, output_path):
    """Create a ball-only detection dataset"""
    
    # Ball detection data config
    ball_data = {"names": {0: "ball"}}
    
    # Create dataset instances
    train_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "train"),
        data=ball_data,
        task="detect",
        class_filter=[0],  # Ball only
    )
    
    val_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "valid"),
        data=ball_data,
        task="detect",
        class_filter=[0],
    )
    
    # Export to COCO format
    output_path = Path(output_path)
    train_dataset.to_coco(output_path / "train_ball.json")
    val_dataset.to_coco(output_path / "val_ball.json")
    
    print(f"Ball detection dataset created at {output_path}")

def create_player_dataset(source_path, output_path):
    """Create a player detection dataset (player + goalkeeper + referee)"""
    
    player_data = {"names": {0: "player"}}
    
    # Mapping:  combine player(1), goalkeeper(2), referee(3) -> player(0)
    class_mapping = {1: 0, 2: 0, 3: 0}
    
    train_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "train"),
        data=player_data,
        task="detect",
        class_filter=[1, 2, 3],
        class_mapping=class_mapping,
    )
    
    val_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "valid"),
        data=player_data,
        task="detect",
        class_filter=[1, 2, 3],
        class_mapping=class_mapping,
    )
    
    output_path = Path(output_path)
    train_dataset.to_coco(output_path / "train_player.json")
    val_dataset.to_coco(output_path / "val_player.json")
    
    print(f"Player detection dataset created at {output_path}")

def create_pitch_dataset(source_path, output_path):
    """Create a pitch segmentation dataset"""
    
    pitch_data = {"names":  {0: "pitch"}}
    
    train_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "train"),
        data=pitch_data,
        task="segment",  # Note: segmentation task
        class_filter=[6],  # Pitch only
    )
    
    val_dataset = SoccerNetDataset(
        img_path=str(Path(source_path) / "valid"),
        data=pitch_data,
        task="segment",
        class_filter=[6],
    )
    
    output_path = Path(output_path)
    train_dataset.to_coco(output_path / "train_pitch.json")
    val_dataset.to_coco(output_path / "val_pitch.json")
    
    print(f"Pitch segmentation dataset created at {output_path}")

if __name__ == '__main__':
    source = "/path/to/soccernet/dataset"
    
    create_ball_dataset(source, "./datasets/ball_detection")
    create_player_dataset(source, "./datasets/player_detection")
    create_pitch_dataset(source, "./datasets/pitch_segmentation")
```

### 5. Simple Training with Standard YOLO

```python name=train_all_models.py
from ultralytics import YOLO

# 1. Train Ball Detector
ball_model = YOLO('yolov8n.pt')
ball_model.train(
    data='ball_detection.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='ball_detector'
)

# 2. Train Player Detector
player_model = YOLO('yolov8n.pt')
player_model.train(
    data='player_detection.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='player_detector'
)

# 3. Train Pitch Segmentation Model
pitch_model = YOLO('yolov8n-seg.pt')  # Note: segmentation model
pitch_model.train(
    data='pitch_segmentation. yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='pitch_segmentation'
)
```

## Key Points

1. **Ball Detection**: Filter `class_filter=[0]`
2. **Player Detection**: Filter `class_filter=[1, 2, 3]` + remap all to class 0
3. **Pitch Segmentation**: Filter `class_filter=[6]` + use `task='segment'`

**Note**: For pitch line segmentation, you need segmentation masks, not just bounding boxes. If your JSON only contains bboxes for pitch, you'll need to either:
- Generate masks from bounding boxes
- Use a different annotation source with actual line masks
- Train a detection model first, then post-process to extract lines

Would you like me to help you implement any specific part of this solution? 
