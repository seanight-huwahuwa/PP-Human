#!/usr/bin/env python3
"""Convert MP4 to GIF at specified size (defaults to 1280x720).

This script prefers `ffmpeg` (palettegen + paletteuse) for quality and speed.
If `ffmpeg` is not available it will try to use `moviepy` as a fallback.

Usage examples:
  # convert full file to 1280x720 gif
  python3 scripts/mp4_to_gif.py /workspace/output_result/real_test.mp4 -o /workspace/output_result/real_test.gif

  # convert 4 seconds starting at 74s at 15 fps
  python3 scripts/mp4_to_gif.py input.mp4 -s 74 -d 4 -f 15 -o out.gif

Requirements:
  - ffmpeg recommended (in PATH)
  - If ffmpeg unavailable, install moviepy (`pip install moviepy`) and ffmpeg for moviepy to work
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_ffmpeg(input_path: str, output_path: str, width: int, height: int, start: float | None, duration: float | None, fps: int):
    # Create palette and use it for high-quality GIF
    with tempfile.TemporaryDirectory() as td:
        palette = Path(td) / "palette.png"
        vf_scale = f"scale={width}:{height}:flags=lanczos"
        fps_filter = f"fps={fps}"

        ss_args = (["-ss", str(start)] if start is not None else [])
        t_args = (["-t", str(duration)] if duration is not None else [])

        cmd_palette = [
            "ffmpeg", "-v", "warning", *ss_args, "-i", input_path,
            "-vf", f"{fps_filter},{vf_scale},palettegen",
            "-y", str(palette)
        ]
        subprocess.run(cmd_palette, check=True)

        cmd_gif = [
            "ffmpeg", "-v", "warning", *ss_args, *([] if start is None else []), "-i", input_path,
            "-i", str(palette),
            "-filter_complex", f"{fps_filter},{vf_scale}[x];[x][1:v]paletteuse=dither=sierra2_4a",
            "-y", output_path
        ]
        # If duration specified, insert -t before first -i input in the second command
        if duration is not None:
            # place -t before first -i by injecting after ss_args
            if start is not None:
                # rebuild with -ss START -t DURATION -i input
                cmd_gif = [
                    "ffmpeg", "-v", "warning", "-ss", str(start), "-t", str(duration), "-i", input_path,
                    "-i", str(palette),
                    "-filter_complex", f"{fps_filter},{vf_scale}[x];[x][1:v]paletteuse=dither=sierra2_4a",
                    "-y", output_path
                ]
            else:
                # no start, just -t
                cmd_gif = [
                    "ffmpeg", "-v", "warning", "-t", str(duration), "-i", input_path,
                    "-i", str(palette),
                    "-filter_complex", f"{fps_filter},{vf_scale}[x];[x][1:v]paletteuse=dither=sierra2_4a",
                    "-y", output_path
                ]

        subprocess.run(cmd_gif, check=True)


def run_moviepy(input_path: str, output_path: str, width: int, height: int, start: float | None, duration: float | None, fps: int):
    try:
        from moviepy.editor import VideoFileClip
    except Exception:
        # try alternate import path
        from moviepy.video.io.VideoFileClip import VideoFileClip

    clip = VideoFileClip(input_path)
    s = start or 0
    e = (s + duration) if duration is not None else None
    if e is not None:
        # some moviepy versions use subclip or subclipped
        if hasattr(clip, 'subclip'):
            clip = clip.subclip(s, e)
        elif hasattr(clip, 'subclipped'):
            clip = clip.subclipped(s, e)
        else:
            raise RuntimeError('moviepy VideoFileClip has no subclip method')
    if (clip.w, clip.h) != (width, height):
        clip = clip.resize((width, height))
    clip.write_gif(output_path, fps=fps)


def parse_args():
    p = argparse.ArgumentParser(description='Convert MP4 to GIF (defaults to 1280x720).')
    p.add_argument('input', help='Input mp4 file')
    p.add_argument('-o', '--output', required=True, help='Output gif path')
    p.add_argument('--width', type=int, default=1280, help='Output width (default: 1280)')
    p.add_argument('--height', type=int, default=720, help='Output height (default: 720)')
    p.add_argument('-s', '--start', type=float, default=None, help='Start time in seconds')
    p.add_argument('-d', '--duration', type=float, default=None, help='Duration in seconds')
    p.add_argument('-f', '--fps', type=int, default=15, help='Output gif fps (default: 15)')
    p.add_argument('--force-moviepy', action='store_true', help='Force use of moviepy fallback')
    return p.parse_args()


def main():
    args = parse_args()
    inp = args.input
    out = args.output
    width = args.width
    height = args.height
    start = args.start
    duration = args.duration
    fps = args.fps

    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path and not args.force_moviepy:
        try:
            print('Using ffmpeg at', ffmpeg_path)
            run_ffmpeg(inp, out, width, height, start, duration, fps)
            print('GIF created at', out)
            return
        except subprocess.CalledProcessError as e:
            print('ffmpeg failed:', e, file=sys.stderr)
            print('Falling back to moviepy...')

    # fallback to moviepy
    try:
        run_moviepy(inp, out, width, height, start, duration, fps)
        print('GIF created at', out)
    except Exception as e:
        print('moviepy fallback failed:', e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
