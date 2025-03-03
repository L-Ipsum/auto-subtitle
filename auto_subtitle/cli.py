import logging
import os
import tempfile
import warnings
from pathlib import Path
from typing import Any

import ffmpeg
from utils import filename, write_srt

logger = logging.getLogger(__name__)


def get_audio(paths) -> dict[Any, Any]:
    temp_dir: str = tempfile.gettempdir()

    audio_paths: dict = {}

    for path in paths:
        logger.info(f"Extracting audio from {filename(path)}...")
        output_path: str = str(Path(temp_dir) / f"{filename(path)}.wav")

        # Build ffmpeg command
        logger.debug(f"ffmpeg {path} -acodec pcm_s16le -ac 1 -ar 16k {output_path}")
        ffmpeg_cmd = ffmpeg.input(path).output(
            output_path, acodec="pcm_s16le", ac=1, ar="16k"
        )

        # Print the command for debugging
        logger.debug("FFmpeg command: %s", " ".join(ffmpeg_cmd.get_args()))

        try:
            ffmpeg_cmd.run(quiet=False, overwrite_output=True)  # Show error output
            audio_paths[path] = output_path
        except ffmpeg.Error as e:
            logger.error(
                "FFmpeg error:", e.stderr.decode()
            )  # Show detailed error message

    return audio_paths


def get_subtitles(
    audio_paths: dict,
    output_srt: bool,
    output_dir: Path,
    transcribe: callable,
) -> dict:
    subtitles_path: dict = {}

    for path, audio_path in audio_paths.items():
        srt_path: Path | str = output_dir if output_srt else tempfile.gettempdir()
        srt_path = os.path.join(srt_path, f"{filename(path)}.srt")

        print(f"Generating subtitles for {filename(path)}... This might take a while.")

        warnings.filterwarnings("ignore")
        result = transcribe(audio_path)
        warnings.filterwarnings("default")

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path
