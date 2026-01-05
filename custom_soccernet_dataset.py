# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from tqdm import tqdm

from ultralytics.data.dataset import YOLODataset
from ultralytics.utils import LOGGER, LOCAL_RANK
from ultralytics.utils.ops import segments2boxes

from .augment import Compose, Format, LetterBox, v8_transforms
from .utils import (
    HELP_URL,
    get_hash,
    load_dataset_cache_file,
    save_dataset_cache_file,
)

# Ultralytics dataset *. cache version
DATASET_CACHE_VERSION = "1.0.3"


class SoccerNetDataset(YOLODataset):
    """
    Custom Dataset class for loading SoccerNet-style annotations from JSON files.

    This dataset expects a directory structure like:
    dataset_dir/
        ├── train/
        │   ├── SNGS-060/
        │   │   ├── SNGS-060.json
        │   │   └── img1/
        │   │       ├── 000001.jpg
        │   │       └── ...
        │   └── SNGS-061/
        │       └── ...
        └── valid/
            └── ...

    Attributes:
        data_root (Path): Root directory containing train/valid folders.
        split_dirs (list): List of sequence directories (e.g., SNGS-060, SNGS-061).

    Examples:
        >>> dataset = SoccerNetDataset(
        ...     img_path="path/to/dataset/train",
        ...     data={"names": {0: "ball", 1: "player", ... }},
        ...     task="detect"
        ... )
    """

    def __init__(self, *args, data: dict | None = None, task: str = "detect", **kwargs):
        """
        Initialize the SoccerNetDataset.

        Args:
            data (dict, optional): Dataset configuration dictionary with class names.
            task (str): Task type, typically 'detect'.
            *args (Any): Additional positional arguments for the parent class.
            **kwargs (Any): Additional keyword arguments for the parent class.
        """
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

    def get_img_files(self, img_path: str) -> list:
        """
        Collect all image files from the SoccerNet directory structure.

        Args:
            img_path (str): Path to the dataset split directory (e.g., train/ or valid/).

        Returns:
            (list): List of image file paths.
        """
        img_path = Path(img_path)
        img_files = []

        # Find all sequence directories (e.g., SNGS-060, SNGS-061)
        sequence_dirs = [d for d in img_path.iterdir() if d.is_dir()]

        for seq_dir in sorted(sequence_dirs):
            # Look for img1 directory inside each sequence
            img_dir = seq_dir / "img1"
            if img_dir.exists():
                # Collect all . jpg files
                images = sorted(img_dir.glob("*.jpg"))
                img_files.extend([str(img) for img in images])

        if not img_files:
            LOGGER.warning(f"No images found in {img_path}")
        else:
            LOGGER.info(f"Found {len(img_files)} images in {img_path}")

        return img_files

    def cache_labels(self, path: Path = Path("./labels.cache")) -> dict:
        """
        Cache dataset labels by reading JSON files from the SoccerNet structure.

        Args:
            path (Path): Path where to save the cache file.

        Returns:
            (dict): Dictionary containing cached labels and related information.
        """
        x = {"labels": []}
        nm, nf, ne, nc, msgs = 0, 0, 0, 0, []  # number missing, found, empty, corrupt, messages

        # Group images by sequence
        img_by_sequence = defaultdict(list)
        json_files = {}

        for img_file in self.im_files:
            img_path = Path(img_file)
            # Get sequence directory (parent of img1)
            seq_dir = img_path.parent.parent
            seq_name = seq_dir.name
            img_by_sequence[seq_name].append(img_file)

            # Store JSON file path
            json_file = seq_dir / f"{seq_name}.json"
            if json_file.exists():
                json_files[seq_name] = json_file

        desc = f"{self.prefix}Loading SoccerNet annotations..."

        # Process each sequence
        for seq_name in tqdm(sorted(img_by_sequence.keys()), desc=desc):
            if seq_name not in json_files:
                msgs.append(f"Missing JSON file for sequence {seq_name}")
                nm += len(img_by_sequence[seq_name])
                continue

            try:
                # Load JSON annotations
                with open(json_files[seq_name], "r") as f:
                    data = json.load(f)

                # Create mapping:  image_id -> annotations
                img_annotations = defaultdict(list)
                for ann in data["annotations"]:
                    img_annotations[ann["image_id"]].append(ann)

                # Create mapping: image_id -> image info
                img_info_map = {img["image_id"]: img for img in data["images"]}

                # Process each image in this sequence
                for img_file in img_by_sequence[seq_name]:
                    img_path = Path(img_file)
                    file_name = img_path.name

                    # Find matching image info
                    img_info = None
                    for info in data["images"]:
                        if info["file_name"] == file_name:
                            img_info = info
                            break

                    if img_info is None:
                        nm += 1
                        continue

                    # Get image dimensions
                    h = img_info["height"]
                    w = img_info["width"]
                    image_id = img_info["image_id"]

                    # Get annotations for this image
                    anns = img_annotations.get(image_id, [])

                    if not anns:
                        ne += 1
                        continue

                    # Process annotations
                    bboxes = []
                    segments = []

                    for ann in anns:
                        # Get category_id (class)
                        cls = ann["category_id"]

                        # Get bbox_image (already in the format we need)
                        bbox = ann.get("bbox_image", {})
                        if not bbox:
                            continue

                        # Extract bbox coordinates (normalized)
                        x_center = bbox.get("x_center", 0.0)
                        y_center = bbox.get("y_center", 0.0)
                        bbox_w = bbox.get("w", 0)
                        bbox_h = bbox.get("h", 0)

                        # Normalize if not already normalized
                        if bbox_w > 1 or bbox_h > 1:
                            x_center = (bbox.get("x", 0) + bbox_w / 2) / w
                            y_center = (bbox.get("y", 0) + bbox_h / 2) / h
                            bbox_w = bbox_w / w
                            bbox_h = bbox_h / h

                        # Skip invalid boxes
                        if bbox_w <= 0 or bbox_h <= 0:
                            continue

                        bboxes.append([cls, x_center, y_center, bbox_w, bbox_h])

                    if not bboxes:
                        ne += 1
                        continue

                    # Convert to numpy array
                    lb = np.array(bboxes, dtype=np.float32)

                    # Add to labels
                    x["labels"].append({
                        "im_file": str(img_file),
                        "shape": (h, w),
                        "cls": lb[:, 0:1],  # n, 1
                        "bboxes": lb[:, 1:],  # n, 4
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
        save_dataset_cache_file(self.prefix, path, x, DATASET_CACHE_VERSION)

        LOGGER.info(
            f"{self.prefix}Successfully loaded {nf} images with annotations, "
            f"{nm} missing, {ne} empty, {nc} corrupt"
        )

        return x

    def get_labels(self) -> list[dict]:
        """
        Return dictionary of labels for YOLO training.

        Returns:
            (list[dict]): List of label dictionaries.
        """
        cache_path = Path(self.img_path).parent / f"{Path(self.img_path).name}_labels.cache"

        try:
            cache, exists = load_dataset_cache_file(cache_path), True
            assert cache["version"] == DATASET_CACHE_VERSION
            assert cache["hash"] == get_hash(self.im_files)
        except (FileNotFoundError, AssertionError, AttributeError):
            cache, exists = self.cache_labels(cache_path), False

        # Display cache info
        nf, nm, ne, nc, n = cache.pop("results")
        if exists and LOCAL_RANK in {-1, 0}:
            d = f"Scanning {cache_path}... {nf} images, {nm + ne} backgrounds, {nc} corrupt"
            LOGGER.info(f"{self.prefix}{d}")
            if cache["msgs"]:
                LOGGER.info("\n".join(cache["msgs"]))

        # Read cache
        [cache.pop(k) for k in ("hash", "version", "msgs")]
        labels = cache["labels"]

        if not labels:
            raise RuntimeError(
                f"No valid images found in {cache_path}.  {HELP_URL}"
            )

        self.im_files = [lb["im_file"] for lb in labels]

        # Check for class distribution
        len_cls = sum(len(lb["cls"]) for lb in labels)
        if len_cls == 0:
            LOGGER.warning(
                f"{self.prefix}No objects found in dataset. Training may not work correctly."
            )

        return labels

    def to_coco(self, save_path: str | Path) -> dict:
        """Convert loaded labels to COCO format and write them to ``save_path``."""
        labels = self.get_labels()

        categories = [
            {
                "id": int(k),
                "name": v,
                "supercategory": "object",
            }
            for k, v in self.data.get("names", {}).items()
        ]

        images = []
        annotations = []
        ann_id = 1

        for img_id, label in enumerate(labels, start=1):
            h, w = label["shape"]
            images.append(
                {
                    "id": img_id,
                    "file_name": Path(label["im_file"]).name,
                    "height": int(h),
                    "width": int(w),
                }
            )

            cls = label["cls"].reshape(-1)
            bboxes = label["bboxes"]
            normalized = label.get("normalized", False)

            for i, class_id in enumerate(cls):
                x_c, y_c, bw, bh = bboxes[i]
                if normalized:
                    x_abs = float((x_c - bw / 2) * w)
                    y_abs = float((y_c - bh / 2) * h)
                    bw_abs = float(bw * w)
                    bh_abs = float(bh * h)
                else:
                    x_abs = float(x_c - bw / 2)
                    y_abs = float(y_c - bh / 2)
                    bw_abs = float(bw)
                    bh_abs = float(bh)

                annotations.append(
                    {
                        "id": ann_id,
                        "image_id": img_id,
                        "category_id": int(class_id),
                        "bbox": [x_abs, y_abs, bw_abs, bh_abs],
                        "area": bw_abs * bh_abs,
                        "iscrowd": 0,
                        "segmentation": [],
                    }
                )
                ann_id += 1

        coco = {
            "info": {
                "description": "SoccerNet converted to COCO",
                "version": DATASET_CACHE_VERSION,
                "date_created": datetime.utcnow().isoformat(),
            },
            "licenses": [],
            "categories": categories,
            "images": images,
            "annotations": annotations,
        }

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(coco, f)

        LOGGER.info(f"Saved COCO annotations to {save_path}")
        return coco

    def visualize_sample(self, index: int = 0, save_path: str | Path | None = None) -> Path | None:
        """Render a single sample with bounding boxes to help spot-check annotations."""
        labels = self.get_labels()
        if not labels:
            LOGGER.warning("No labels available to visualize")
            return None

        label = labels[index % len(labels)]
        img = cv2.imread(label["im_file"])
        if img is None:
            LOGGER.warning(f"Unable to read image {label['im_file']}")
            return None

        h, w = label["shape"]
        cls = label["cls"].reshape(-1)
        bboxes = label["bboxes"]
        normalized = label.get("normalized", False)

        for i, class_id in enumerate(cls):
            x_c, y_c, bw, bh = bboxes[i]
            if normalized:
                x1 = int((x_c - bw / 2) * w)
                y1 = int((y_c - bh / 2) * h)
                x2 = int((x_c + bw / 2) * w)
                y2 = int((y_c + bh / 2) * h)
            else:
                x1 = int(x_c - bw / 2)
                y1 = int(y_c - bh / 2)
                x2 = int(x_c + bw / 2)
                y2 = int(y_c + bh / 2)

            color = tuple(int(c) for c in np.random.randint(0, 255, size=3))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            name = self.data.get("names", {}).get(int(class_id), str(int(class_id)))
            cv2.putText(
                img,
                name,
                (x1, max(y1 - 5, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA,
            )

        save_path = Path(save_path) if save_path is not None else Path(label["im_file"]).with_suffix(".vis.jpg")
        cv2.imwrite(str(save_path), img)
        LOGGER.info(f"Wrote visualization to {save_path}")
        return save_path