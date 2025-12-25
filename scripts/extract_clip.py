#!/usr/bin/env python3
"""Extract a short clip from a video file.

Usage examples:
  python3 scripts/extract_clip.py TrainStation.mp4 -s 12 -d 7 -o train_clip.mp4
  python3 scripts/extract_clip.py TrainStation.mp4 --start 30 --duration 7

Requirements:
  pip install moviepy
"""
import argparse
import os
try:
    # Some moviepy installs don't provide moviepy.editor; import directly from video.io
    from moviepy.editor import VideoFileClip
except Exception:
    from moviepy.video.io.VideoFileClip import VideoFileClip


def parse_args():
    p = argparse.ArgumentParser(description="Extract a clip from a video file")
    p.add_argument("input", help="Input video file (e.g., TrainStation.mp4)")
    p.add_argument("-s", "--start", type=float, default=0.0, help="Start time in seconds (default: 0)")
    p.add_argument("-d", "--duration", type=float, default=7.0, help="Duration in seconds (default: 7)")
    p.add_argument("-o", "--output", help="Output filename (default: <input>_clip_<start>_<dur>.mp4)")
    p.add_argument("--fps", type=int, default=None, help="Optional output fps")
    return p.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        raise SystemExit(f"Input file not found: {args.input}")

    start_t = max(0.0, args.start)
    end_t = start_t + max(0.0, args.duration)

    print(f"Loading {args.input}...")
    with VideoFileClip(args.input) as vid:
        if end_t > vid.duration:
            end_t = vid.duration
            print(f"Requested end time exceeds video length; trimming to {end_t:.2f}s")

        print(f"Extracting clip: {start_t:.2f}s -> {end_t:.2f}s ({end_t-start_t:.2f}s)")
        # moviepy API may provide either subclip or subclipped depending on version
        if hasattr(vid, 'subclip'):
            clip = vid.subclip(start_t, end_t)
        elif hasattr(vid, 'subclipped'):
            clip = vid.subclipped(start_t, end_t)
        else:
            raise RuntimeError('moviepy VideoFileClip has no subclip/subclipped method')

        out = args.output
        if not out:
            base = os.path.splitext(os.path.basename(args.input))[0]
            out = f"{base}_clip_{int(start_t)}_{int(end_t-start_t)}.mp4"

        write_kwargs = dict(codec="libx264", audio_codec="aac", threads=4)
        if args.fps:
            write_kwargs["fps"] = args.fps

        print(f"Writing output to {out} ...")
        clip.write_videofile(out, **write_kwargs)

    print("Done.")


if __name__ == "__main__":
    main()
