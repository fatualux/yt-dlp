#!/usr/bin/env python3
import os
import re
import sys
import subprocess

# --- Step 1: ensure yt-dlp is installed ---
try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("📦 yt-dlp not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
    from yt_dlp import YoutubeDL


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)


def simplify_title(title, uploader):
    title = re.sub(r'[\s\-–_]+', ' ', title).strip()
    uploader = re.sub(r'[\s\-–_]+', ' ', uploader).strip()
    return f"{uploader} - {title}"


def get_user_choice():
    link = input("Enter YouTube link: ").strip()
    return link


def list_formats(link):
    print("\n🔍 Fetching available formats...\n")
    with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
        info = ydl.extract_info(link, download=False)

    if not info:
        print("❌ Failed to retrieve video info.")
        sys.exit(1)

    formats = info.get("formats", [])
    print(f"📺 Title: {info.get('title', 'Unknown')}")
    print(f"👤 Uploader: {info.get('uploader', 'Unknown')}\n")

    print("Available formats:")
    print("-" * 70)
    for f in formats:
        f_id = f.get("format_id")
        f_ext = f.get("ext")
        f_res = f.get("resolution") or f"{f.get('width')}x{f.get('height')}"
        f_fps = f.get("fps") or ""
        f_abr = f.get("abr")
        f_vbr = f.get("vbr")
        f_note = f.get("format_note", "")
        if f_res and f_fps:
            label = f"{f_res}@{f_fps}fps"
        elif f_abr:
            label = f"{f_abr}kbps audio"
        else:
            label = f_res or "unknown"
        print(f"{f_id:>6} | {f_ext:<4} | {label:<15} | {f_note}")

    print("-" * 70)
    choice = input("\nEnter the format ID to download: ").strip()
    return info, choice


def main():
    link = get_user_choice()
    try:
        info, fmt_id = list_formats(link)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    title = info.get("title", "unknown")
    uploader = info.get("uploader", "unknown")
    simplified = sanitize_filename(simplify_title(title, uploader))

    outtmpl = "%(title)s.%(ext)s"
    ydl_opts = {
        "quiet": False,
        "noplaylist": True,
        "format": fmt_id,
        "addmetadata": True,
        "outtmpl": outtmpl,
        "writethumbnail": True,
        "writeinfojson": True,
        "merge_output_format": None,
    }

    print(f"\n⬇️ Downloading '{title}' using format {fmt_id}...\n")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        sys.exit(1)

    ext = info.get("ext", "mp4")
    old_filename = f"{title}.{ext}"
    new_filename = f"{simplified}.{ext}"

    for file in os.listdir("."):
        if file.lower().startswith(title.lower()) and file.lower().endswith(ext):
            old_filename = file
            break

    if os.path.exists(old_filename):
        os.rename(old_filename, new_filename)
        print(f"\n✅ File renamed to: {new_filename}")
    else:
        print(f"\n⚠️ Could not find downloaded file: {old_filename}")


if __name__ == "__main__":
    main()

