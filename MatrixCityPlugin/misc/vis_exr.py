from typing import List

import cv2
import Imath
import OpenEXR  # pip install openexr
import numpy as np


def float2int(array):
    array = np.round(array * 255)
    array = np.clip(array, 0, 255)
    return array.astype(np.uint8)


def openexr_to_array(file: OpenEXR.InputFile, channel: str) -> np.ndarray:
    channel_type = file.header()['channels'][channel]

    if channel_type == Imath.Channel(Imath.PixelType(Imath.PixelType.HALF)):
        pix_type = Imath.PixelType(Imath.PixelType.HALF)
        dtype = np.float16
    elif channel_type == Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)):
        pix_type = Imath.PixelType(Imath.PixelType.FLOAT)
        dtype = np.float32
    else:
        print('please specify PixelType')
        return

    img = np.frombuffer(file.channel(channel, pix_type), dtype=dtype)
    return img


def openexr_to_img(file: OpenEXR.InputFile, channel: str, size: tuple) -> np.ndarray:
    img = openexr_to_array(file, channel)  # shape: (height * width)
    img = np.reshape(img, (size[1], size[0])).astype(np.float32)  # shape: (height, width)
    return img


def openexr_read(path: str, channel: str) -> np.ndarray:
    file = OpenEXR.InputFile(path)
    DW = file.header()['dataWindow']
    size = (DW.max.x - DW.min.x + 1, DW.max.y - DW.min.y + 1)
    img = openexr_to_img(file, channel, size)
    return img


def openexr_read_channels(path: str, channels: List[str]) -> np.ndarray:
    file = OpenEXR.InputFile(path)
    DW = file.header()['dataWindow']
    size = (DW.max.x - DW.min.x + 1, DW.max.y - DW.min.y + 1)
    imgs = [openexr_to_img(file, channel, size) for channel in channels]
    img = np.stack(imgs, axis=2)
    return img


def get_rgb_exr(path, bgr=False):
    if bgr:
        img = openexr_read_channels(path, ['B', 'G', 'R'])
    else:
        img = openexr_read_channels(path, ['R', 'G', 'B'])
    return img


def get_flow_exr(path, bgr=False):
    import flow_vis     # pip install flow_vis

    flow = openexr_read_channels(path, ['R', 'G'])
    img = flow_vis.flow_to_color(flow, convert_to_bgr=bgr)
    return img


def get_depth_exr(img_path, depth_rescale=1.0):
    depth = get_rgb_exr(img_path)
    # depth[depth>100] = 0.
    img = float2int(depth / depth_rescale)

    img[img == 0] = 255
    return img


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', '-i', type=str, help='img path')
    parser.add_argument('--out_path', '-o', type=str, help='output path')
    parser.add_argument('--type', '-t', type=str, help='type: rgb, flow, depth, mask')

    args = parser.parse_args()

    if args.type == 'rgb':
        img = get_rgb_exr(args.img_path, bgr=True)
        img = float2int(img)
        cv2.imwrite(args.out_path, img)
    elif args.type == 'mask':
        img = get_rgb_exr(args.img_path, bgr=True)
        img = float2int(img)
        cv2.imwrite(args.out_path, img)
    elif args.type == 'flow':
        img = get_flow_exr(args.img_path, bgr=True)
        cv2.imwrite(args.out_path, img)
    elif args.type == 'depth':
        img = get_depth_exr(args.img_path)
        cv2.imwrite(args.out_path, img)
    else:
        img = cv2.imread(args.img_path)
        cv2.imwrite(args.out_path, img)

    print(f'{args.type} saved to {args.out_path}')


if __name__ == "__main__":
    main()
