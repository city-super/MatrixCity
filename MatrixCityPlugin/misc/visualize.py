from pathlib import Path
from typing import Callable, List, Optional

import cv2
from tqdm import tqdm

import vis_exr


class Visualizer:
    """Declare operators for visualization like the following class methods.
    """
    __slots__ = ()

    # @classmethod
    # def rgb(cls, img_path: Path, out_path: Path) -> None:
    #     img = vis_exr.get_rgb_exr(str(img_path), bgr=True)
    #     img = vis_exr.float2int(img)
    #     cv2.imwrite(str(out_path), img)

    @classmethod
    def mask(cls, img_path: Path, out_path: Path) -> None:
        img = vis_exr.get_rgb_exr(str(img_path), bgr=True)
        img = vis_exr.float2int(img)
        cv2.imwrite(str(out_path), img)

    @classmethod
    def flow(cls, img_path: Path, out_path: Path) -> None:
        img = vis_exr.get_flow_exr(str(img_path), bgr=True)
        cv2.imwrite(str(out_path), img)

    @classmethod
    def depth(cls, img_path: Path, out_path: Path) -> None:
        img = vis_exr.get_depth_exr(str(img_path), 5000)
        # img = get_depth_exr(str(img_path))
        cv2.imwrite(str(out_path), img)


# all supported annotation types
VIS_TYPES = tuple(k for k in Visualizer.__dict__.keys() if not k.startswith("_"))
TYPE2DIRNAME = {
    "mask": "mask",
    "depth": "depth",
    "flow": "optical_flow"
}


def guess_type(name):
    if 'mask' in name:
        return 'mask'
    elif 'depth' in name:
        return 'depth'
    elif 'velocity' in name:
        return 'flow'
    else:
        return 'rgb'


def visualize(image_paths: List[Path], out_dir: Path, vis_type: str, out_format: str = '.png', overwrite=False):
    visualizer: Optional[Callable[[Path, Path], None]] = getattr(Visualizer, vis_type, None)
    if visualizer is None:
        raise ValueError(f"Not visualizer for vis_type={vis_type}")

    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for img_path in tqdm(image_paths, desc=f"{vis_type}"):
        out_path = out_dir / f"{img_path.stem}{out_format}"
        if out_path.exists() and not overwrite:
            continue
        visualizer(img_path, out_path)
        count += 1
    print(f'{vis_type}: saved {count} images to {out_dir}')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', '-i', type=str, help='img path')
    parser.add_argument('--img_pattern', type=str, default="*.png")
    parser.add_argument('--out_dir', '-o', type=str, default="", help='output path')
    parser.add_argument('--type', '-t', type=str, default='', help='type: rgb, flow, depth, mask')

    args = parser.parse_args()

    def main():
        type_ = args.type
        if not type_:
            type_ = guess_type(args.img_pattern)
            print(f"Guess type: {type_}")

        if args.out_dir:
            out_dir = Path(args.out_dir)
        else:
            out_dir = Path(args.img_dir) / type_
        out_dir.mkdir(exist_ok=True, parents=True)

        image_paths = list(Path(args.img_dir).glob(args.img_pattern))
        visualize(image_paths, out_dir, type_)

    main()
