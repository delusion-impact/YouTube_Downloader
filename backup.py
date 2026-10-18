#!/usr/bin/env python3
"""Бэкап YouTube канала/плейлиста через yt-dlp + ffmpeg.

Инкрементальные повторные запуски: уже скачанные видео пропускаются
через --download-archive. Вместе с видео сохраняются метаданные
(info-json, описание, обложка).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ========== НАСТРОЙКИ ПО УМОЛЧАНИЮ ==========
DEFAULT_OUTPUT_DIR = "backup_channel"
MIN_YTDLP_VERSION = 20250101  # yt-dlp старше этой даты почти наверняка сломан YouTube
# ================================================


def reconfigure_console() -> None:
    """Гарантируем UTF-8 вывод, чтобы эмодзи не роняли скрипт на старых консолях Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def check_ytdlp_freshness() -> None:
    try:
        from yt_dlp.version import __version__ as raw_version
    except ImportError:
        print("❌ yt-dlp не установлен. Выполните: pip install -r requirements.txt")
        sys.exit(1)

    digits = re.sub(r"\D", "", str(raw_version))[:8]  # "2026.8.19" -> "20260819"
    if int(digits or 0) < MIN_YTDLP_VERSION:
        print(f"⚠️  yt-dlp {raw_version} устарел — обновите: pip install -U yt-dlp")


def resolve_ffmpeg() -> str | None:
    """Ищет ffmpeg: PATH -> встроенный в imageio-ffmpeg (ffmpeg_zip не нужен)."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def build_command(args: argparse.Namespace, output_dir: Path, ffmpeg_path: str) -> list[str]:
    output_template = str(output_dir / "%(playlist_index)03d_%(id)s_%(title)s.%(ext)s")
    archive = output_dir / "archive.txt"
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--ffmpeg-location", ffmpeg_path,
        "-f", f"bv*[height<={args.quality}]+ba/b[height<={args.quality}]",
        "--merge-output-format", "mp4",
        "-o", output_template,
        "--download-archive", str(archive),
        "--continue",
        "--no-overwrites",
        "--ignore-errors",
        "--retries", "10",
        "--fragment-retries", "10",
        "--concurrent-fragments", "4",
        "--write-info-json",
        "--write-description",
        "--write-thumbnail",
        "--yes-playlist",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        args.url,
    ]
    if args.sleep:
        cmd += ["--sleep-requests", "1", "--limit-rate", "10M"]
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="Бэкап YouTube канала/плейлиста через yt-dlp + ffmpeg")
    parser.add_argument("url", help="URL канала, плейлиста или видео")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                        help="папка для сохранения (по умолчанию: %(default)s)")
    parser.add_argument("--quality", default="1080", metavar="PX",
                        help="максимальная высота видео, напр. 720/1080/2160 (по умолчанию: %(default)s)")
    parser.add_argument("--no-sleep", dest="sleep", action="store_false", default=True,
                        help="не делать паузы между запросами (быстрее, но выше риск троттлинга)")
    args = parser.parse_args()

    reconfigure_console()
    check_ytdlp_freshness()

    ffmpeg_path = resolve_ffmpeg()
    if not ffmpeg_path:
        print("❌ ffmpeg не найден. Установите пакет со встроенным ffmpeg:")
        print("   pip install imageio-ffmpeg")
        sys.exit(1)
    print(f"🔧 ffmpeg: {ffmpeg_path}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_command(args, output_dir, ffmpeg_path)
    print(f"🚀 Начинаю бэкап: {args.url}")
    print(f"📁 Сохраняю в: {output_dir.resolve()}")
    print(f"🎞️  Максимальное качество: {args.quality}p")
    if args.sleep:
        print("😴 Паузы между запросами: включены (отключить: --no-sleep)")

    process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=subprocess.STDOUT,
                               encoding="utf-8", errors="replace")
    returncode = process.wait()

    if returncode == 0:
        print(f"\n✅ Готово: {output_dir.resolve()}")
    else:
        print(f"\n❌ Загрузка завершилась с ошибкой (код {returncode})")
    sys.exit(returncode)


if __name__ == "__main__":
    main()
