import argparse
import logging
import os
import warnings
from pathlib import Path
from typing import Any

import ffmpeg
import language_choices
import whisper
from cli import get_audio, get_subtitles
from logging_setup import setup_logger
from utils import filename, str2bool


def main() -> None:
    setup_logger()

    logger: logging.Logger = logging.getLogger(__name__)  # noqa: F841

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "video",
        nargs="+",
        type=str,
        help="paths to video files to transcribe",
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=whisper.available_models(),
        help="name of the Whisper model to use",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default=".",
        help="directory to save the outputs",
    )
    parser.add_argument(
        "--output_srt",
        type=str2bool,
        default=False,
        help="whether to output the .srt file along with the video files",
    )
    parser.add_argument(
        "--srt_only",
        type=str2bool,
        default=False,
        help="only generate the .srt file and not create overlayed video",
    )
    parser.add_argument(
        "--verbose",
        type=str2bool,
        default=False,
        help="whether to print out the progress and debug messages",
    )

    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="auto",
        choices=[language_choices.choices],
        help="What is the origin language of the video? If unset, it is detected automatically.",
    )

    args: dict[str, Any] = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: Path = Path(args.pop("output_dir"))
    output_srt: bool = args.pop("output_srt")
    srt_only: bool = args.pop("srt_only")
    language: str = args.pop("language")

    output_dir.mkdir(parents=True, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection."
        )
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        args["language"] = language

    model: whisper.Whisper = whisper.load_model(name=model_name)
    audios: dict = get_audio(paths=args.pop("video"))
    subtitles: dict = get_subtitles(
        audio_paths=audios,
        output_srt=output_srt or srt_only,
        output_dir=output_dir,
        transcribe=lambda audio_path: model.transcribe(audio=audio_path, **args),
    )

    if srt_only:
        return

    for path, srt_path in subtitles.items():
        file: str = filename(path)
        out_path: str = os.path.join(output_dir, f"{file}.mp4")

        print(f"Adding subtitles to {file}...")

        video = ffmpeg.input(path)
        audio = video.audio

        ffmpeg.concat(
            video.filter(
                "subtitles",
                srt_path,
                force_style="OutlineColour=&H40000000,BorderStyle=3",
            ),
            audio,
            v=1,
            a=1,
        ).output(str(out_path), quiet=True, overwrite_output=True)

        print(f"Saved subtitled video to {os.path.abspath(out_path)}.")


if __name__ == "__main__":
    main()
