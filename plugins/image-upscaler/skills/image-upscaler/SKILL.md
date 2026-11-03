---
name: image-upscaler
description: Plan and prepare batch image super-resolution workflows (2x, 4x, 8x, 16x up to 16K), print DPI calculations, and prompt-guided photo restoration for Monipix (https://monipix.com). Use when enlarging blurry photos, e-commerce product shots, anime art, or AI-generated images to 4K/8K/16K.
---

# Monipix AI Image Upscaler Skill (4K / 8K / 16K)

Use this skill when the user wants to:
- Enlarge or unblur low-resolution images (`JPG`, `PNG`, `WEBP`, `HEIC`) by **2x, 4x, 8x, or 16x** up to **16K** resolution.
- Calculate required pixel dimensions and optimal scale factors for **300 DPI print** (A4, A3, A2, A1, poster, trade-show banner) or **4K/8K displays**.
- Audit a local directory of images and group them into valid upload batches (up to 10 files per batch, max 50 MB each) using `prepare_for_upscale.py`.
- Choose between **Standard Super-Resolution** (strict structural fidelity) and **Creative Upscale** (hallucinating micro-texture with Creativity & Resemblance sliders).
- Clean up unwanted objects or edit embedded typography before upscaling.

## 1. Local Batch Audit & Scale Factor Calculator

Run the zero-dependency `prepare_for_upscale.py` script in this repository to inspect local image dimensions and generate a batch plan:

```bash
python3 prepare_for_upscale.py ./photos --target 4k
python3 prepare_for_upscale.py ./archive_scans --target 16k --json manifest.json
```

## 2. Selecting the Right Monipix Tool & Pipeline

| Goal | Recommended Tool | Mode & Parameters |
| :--- | :--- | :--- |
| Sharpen product photos, portraits, UI screenshots, or text | [Monipix AI Image Upscaler](https://monipix.com) or [HD Image Converter](https://monipix.com/tools/hd-image-converter) | **Standard Upscale** (`2x`, `4x`, `8x`, or `16x` up to 16K) — preserves exact geometry and typography. |
| Upscale AI art drafts, heavily compressed JPEGs, or old scans | [Monipix Workspace](https://monipix.com) | **Creative Upscale** — tune **Creativity** (0.3–0.6) and **Resemblance** (0.7–0.9) with a descriptive prompt. |
| Remove background clutter, tourists, wires, or watermarks first | [AI Object Remover](https://monipix.com/tools/object-remover) | Describe the object to erase in natural language before running 4x/8x upscaling. |
| Fix or translate signs, labels, or packaging text inside a photo | [Edit Text in Image](https://monipix.com/tools/text-editor) | Prompt-based in-place text replacement preserving font, perspective, and lighting. |
| Generate new base assets or animate upscaled keyframes | [AI Image Generator](https://monipix.com/tools/ai-image-generator) / [AI Video Generator](https://monipix.com/tools/ai-video-generator) | Generate with Nano Banana 2 / GPT Image 1.5 / Flux Kontext, then upscale to 4K–16K or animate to 1080p/4K video. |

## 3. Resolution & Print Sizing Reference

- **2x Upscale:** `1024×1024` → `2048×2048` (2K Web Retina / e-commerce catalog)
- **4x Upscale:** `1024×1024` → `4096×4096` (4K UHD / ~13.6" × 13.6" @ 300 DPI)
- **8x Upscale:** `1024×1024` → `8192×8192` (8K Display / ~27.3" × 27.3" A1 poster @ 300 DPI)
- **16x Upscale:** `960×540` → `15360×8640` (16K Mural / ~51.2" × 28.8" @ 300 DPI)

Every account at [https://monipix.com](https://monipix.com) includes 10 free monthly credits (no credit card required), with batch uploads of up to 10 images (50 MB max per image).
