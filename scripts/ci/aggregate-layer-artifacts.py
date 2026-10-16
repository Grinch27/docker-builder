#!/usr/bin/env python3
"""Create stable per-image and unique OCI layer reports from workflow artifacts.

Input is the already-fetched `layer-<image>.json` artifact schema, not a
container registry request. This script never publishes images.
"""
import json
import sys
from pathlib import Path

def aggregate(root: Path):
    result = {}
    files = list(sorted(root.glob("**/layer-*.json")))
    if not files:
        raise ValueError("No per-image layer artifacts")
    for path in files:
        item=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(item,dict) or not isinstance(item.get("image_name"),str):
            raise ValueError(f"Invalid layer record: {path}")
        name=item["image_name"]
        layers=item.get("Layers")
        if not isinstance(layers,list) or not all(isinstance(x,str) for x in layers):
            raise ValueError(f"Malformed Layers for {name}")
        if not layers:
            raise ValueError(f"No layers for {name}")
        if name in result and result[name] != layers:
            raise ValueError(f"Conflicting layer artifacts for {name}")
        result[name]=layers
    return result

def main():
    if len(sys.argv)!=3:
        raise SystemExit("Usage: aggregate-layer-artifacts.py DIR OUTPUT_DIR")
    root,out=Path(sys.argv[1]),Path(sys.argv[2])
    per_image=aggregate(root)
    out.mkdir(parents=True,exist_ok=True)
    unique=sorted(set(layer for layers in per_image.values() for layer in layers))
    (out/"base_layers.json").write_text(json.dumps(per_image,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"aggregated_layers.json").write_text(json.dumps({"Layers":unique},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"images":len(per_image),"unique_layers":len(unique)}))

if __name__=="__main__":
    main()
