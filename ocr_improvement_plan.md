# OCR Quality Improvement Plan

## Problem
- Current PaddleOCR with 0.75 threshold filters out too much text
- Chandra OCR requires NVIDIA GPU (not available on this system)

## Options

### Option A: Improve PaddleOCR Configuration (Recommended)
- Lower confidence threshold to 0.5-0.6
- Add smart noise filtering:
  - Filter out text shorter than 3 characters
  - Filter out text with very low character variety (e.g., "و ي ي ي")
  - Keep mathematical symbols and equations
- **Pros**: Works on CPU, quick to implement
- **Cons**: May still have some noise

### Option B: Switch to Tesseract OCR
- Install Tesseract with Arabic language pack
- Use `pytesseract` Python wrapper
- **Pros**: Well-established, CPU-compatible, good Arabic support
- **Cons**: May be less accurate on complex layouts than PaddleOCR

### Option C: Install GPU Drivers for Chandra
- Requires NVIDIA GPU hardware
- Requires `sudo` access to install drivers
- **Pros**: Best OCR quality available
- **Cons**: Requires hardware and system changes

## Recommendation
Start with **Option A** - it's the quickest path to better results without system changes.
