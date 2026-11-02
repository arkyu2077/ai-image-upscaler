#!/usr/bin/env python3
"""
prepare_for_upscale.py — Zero-dependency batch image auditor and scale calculator for Monipix (https://monipix.com).

Inspects a folder of JPG, PNG, and WEBP files, verifies the 50 MB upload cap,
calculates the recommended multiplier (2x, 4x, 8x, 16x) to reach 4K, 8K, or 16K,
reports 300-DPI print dimensions, and splits valid files into 10-file upload batches.
"""

import argparse
import json
import math
import os
import struct
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_FILE_MB = 50.0
MAX_BATCH_SIZE = 10

TARGET_LONG_EDGE = {
    "4k": 3840,
    "8k": 7680,
    "16k": 15360,
}


def read_image_dimensions(path: Path):
    """Read (width, height) from PNG, JPEG, or WEBP headers without external libraries."""
    try:
        with path.open("rb") as f:
            head = f.read(64)
            if len(head) < 24:
                return None

            # PNG
            if head.startswith(b"\x89PNG\r\n\x1a\n") and head[12:16] == b"IHDR":
                w, h = struct.unpack(">II", head[16:24])
                return int(w), int(h)

            # RIFF WEBP
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                chunk = head[12:16]
                if chunk == b"VP8 ":
                    w, h = struct.unpack("<HH", head[26:30])
                    return int(w & 0x3FFF), int(h & 0x3FFF)
                elif chunk == b"VP8L":
                    b0, b1, b2, b3 = head[21:25]
                    w = 1 + (((b1 & 0x3F) << 8) | b0)
                    h = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
                    return int(w), int(h)
                elif chunk == b"VP8X":
                    w = 1 + int.from_bytes(head[24:27], "little")
                    h = 1 + int.from_bytes(head[27:30], "little")
                    return int(w), int(h)

            # JPEG
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2:
                        break
                    while marker[1] == 0xFF:
                        b = f.read(1)
                        if not b:
                            return None
                        marker = bytes([0xFF, b[0]])
                    m = marker[1]
                    if m in (0xD8, 0xD9):
                        continue
                    size_bytes = f.read(2)
                    if len(size_bytes) < 2:
                        break
                    seg_size = struct.unpack(">H", size_bytes)[0]
                    if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        sof = f.read(5)
                        if len(sof) == 5:
                            _, h, w = struct.unpack(">BHH", sof)
                            return int(w), int(h)
                        break
                    f.seek(seg_size - 2, os.SEEK_CUR)
    except Exception:
        return None
    return None


def recommend_scale(width: int, height: int, target_key: str) -> int:
    target_edge = TARGET_LONG_EDGE[target_key]
    long_edge = max(width, height, 1)
    ratio = target_edge / float(long_edge)
    for factor in (2, 4, 8, 16):
        if factor >= ratio:
            return factor
    return 16


def audit_directory(input_dir: Path, target_key: str):
    files = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    records = []
    for p in files:
        size_mb = p.stat().st_size / (1024 * 1024)
        dims = read_image_dimensions(p)
        w, h = dims if dims else (0, 0)
        scale = recommend_scale(w, h, target_key) if w and h else 4
        out_w, out_h = w * scale, h * scale
        print_w_in = round(out_w / 300.0, 1) if out_w else None
        print_h_in = round(out_h / 300.0, 1) if out_h else None
        records.append({
            "file": str(p),
            "format": p.suffix.lower().lstrip("."),
            "size_mb": round(size_mb, 2),
            "within_50mb_limit": size_mb <= MAX_FILE_MB,
            "input_dimensions": f"{w}x{h}" if w else "unknown",
            "recommended_scale": f"{scale}x",
            "output_dimensions": f"{out_w}x{out_h}" if out_w else "unknown",
            "print_size_300dpi_inches": f"{print_w_in}x{print_h_in} in" if print_w_in else "unknown",
        })
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Audit images and calculate 2x/4x/8x/16x super-resolution batches for Monipix (https://monipix.com)."
    )
    parser.add_argument("directory", type=Path, help="Folder containing images to inspect")
    parser.add_argument("--target", choices=["4k", "8k", "16k"], default="4k", help="Target output tier (default: 4k)")
    parser.add_argument("--json", type=Path, help="Optional path to save JSON batch manifest")
    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: directory '{args.directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    records = audit_directory(args.directory, args.target)
    valid = [r for r in records if r["within_50mb_limit"]]
    num_batches = math.ceil(len(valid) / MAX_BATCH_SIZE) if valid else 0

    print(f"=== Monipix Super-Resolution Batch Plan (Target: {args.target.upper()}) ===")
    print(f"Total supported images found : {len(records)}")
    print(f"Eligible (<= 50 MB)          : {len(valid)}")
    print(f"10-file upload batches       : {num_batches}")
    print(f"Upload workspace             : https://monipix.com/tools/hd-image-converter\n")

    for idx, r in enumerate(records, 1):
        status = "OK" if r["within_50mb_limit"] else "OVERSIZE (>50MB)"
        print(
            f"[{idx:02d}] {Path(r['file']).name:<28} | {r['size_mb']:>6.2f} MB ({status}) | "
            f"{r['input_dimensions']:<11} -> {r['recommended_scale']:<3} -> {r['output_dimensions']:<13} "
            f"({r['print_size_300dpi_inches']})"
        )

    if args.json:
        payload = {
            "target": args.target,
            "workspace_url": "https://monipix.com",
            "hd_converter_url": "https://monipix.com/tools/hd-image-converter",
            "total_files": len(records),
            "batches": [valid[i:i + MAX_BATCH_SIZE] for i in range(0, len(valid), MAX_BATCH_SIZE)],
        }
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nSaved JSON manifest to {args.json}")


if __name__ == "__main__":
    main()
