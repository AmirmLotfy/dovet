"""Render the concise, evidence-led Dovet submission film."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from render import add_soundtrack, duration, probe, write_captions

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private-artifacts" / "video"
STORY = PRIVATE / "story"
SUBMISSION = ROOT / "submission" / "video"
PLAN = ROOT / "submission" / "video" / "narration-scenes.json"
OUTPUT = SUBMISSION / "dovet-submission-final-disclosed.mp4"

SCENES = [
    ("01", "DOVET", "Keep the work. Change the agent.", "illustration", 0.0, ""),
    ("02", "THE PROBLEM", "Interrupted work loses context.", "marketing", 0.0, ""),
    ("03", "AUTHORIZED BOUNDARY", "Scope comes before autonomy.", "console-still", 0.0, ""),
    (
        "04",
        "OBSERVED",
        "Stop the worker. Confirm it.",
        "evidence",
        0.0,
        "PASS — MANAGED CODEX INTERRUPTION",
    ),
    (
        "05",
        "VERIFIED",
        "Seal a checkpoint by hash.",
        "checkpoint-graphic",
        0.0,
        "PASS — BYTE-IDENTICAL RESTORE",
    ),
    (
        "06",
        "ADVISORY",
        "Let Strands recommend.",
        "provider-still",
        0.0,
        "BLOCKED — 0 SUCCESSFUL BEDROCK REQUESTS",
    ),
    (
        "07",
        "DETERMINISTIC",
        "Let policy decide.",
        "policy-graphic",
        0.0,
        "PASS — LOCAL POLICY TESTS",
    ),
    (
        "08",
        "RESTRICTED WORKER",
        "One writer. Fixed tools.",
        "worker-graphic",
        0.0,
        "LIVE CLOUD EXECUTION NOT RUN",
    ),
    (
        "09",
        "INDEPENDENT VERIFICATION",
        "“Done” is not a test result.",
        "verify-graphic",
        0.0,
        "BASELINE: 13 FAILURES — RECOVERY NOT RUN",
    ),
    (
        "10",
        "CHECKPOINT BUNDLE",
        "Portable recovery, validated first.",
        "marketing",
        5.5,
        "PASS — HASH AND PATH VALIDATION",
    ),
    (
        "11",
        "DURABLE LOCAL DAEMON",
        "The bridge can stop.",
        "daemon-graphic",
        0.0,
        "PASS — SERVICE SURVIVES BRIDGE EXIT",
    ),
    (
        "12",
        "DOVET.SITE",
        "Keep the work. Change the agent.",
        "illustration",
        0.0,
        "PROFESSIONAL AGENTS",
    ),
]


def run(argv: tuple[str, ...]) -> None:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed: {result.stderr[-800:]}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_for(kind: str) -> Path:
    if kind == "illustration":
        return PRIVATE / "dovet-editorial-opener.png"
    return STORY / f"{kind}.webm"


def make_editorial_graphic(kind: str, output: Path) -> None:
    """Draw claim-specific graphics with deterministic product typography."""
    common = [
        "magick",
        "-size",
        "1920x1080",
        "xc:#e8e4da",
        "-font",
        "Helvetica-Bold",
    ]
    if kind == "checkpoint-graphic":
        args = common + [
            "-fill",
            "#171512",
            "-draw",
            "rectangle 72,240 780,900",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "38",
            "-annotate",
            "+126+318",
            "WORKING SET",
            "-pointsize",
            "112",
            "-annotate",
            "+120+470",
            "FILES",
            "-fill",
            "#7b362a",
            "-draw",
            "rectangle 870,366 1040,536",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "72",
            "-annotate",
            "+907+406",
            "#",
            "-fill",
            "#171512",
            "-draw",
            "polygon 1040,422 1150,452 1040,482",
            "-fill",
            "#7b362a",
            "-pointsize",
            "29",
            "-annotate",
            "+1168+270",
            "CONTENT ADDRESSED",
            "-fill",
            "#171512",
            "-pointsize",
            "68",
            "-annotate",
            "+1160+330",
            "IMMUTABLE",
            "-pointsize",
            "68",
            "-annotate",
            "+1160+416",
            "CHECKPOINT",
            "-fill",
            "#ffffff",
            "-draw",
            "rectangle 1160,548 1782,624",
            "-fill",
            "#171512",
            "-pointsize",
            "28",
            "-annotate",
            "+1202+568",
            "PATH  MODE  SIZE  SHA-256",
            "-fill",
            "#7b362a",
            "-pointsize",
            "24",
            "-annotate",
            "+1162+700",
            "SECRETS EXCLUDED",
            "-annotate",
            "+1162+750",
            "HASHES RECHECKED",
            "-annotate",
            "+1162+800",
            "RESTORE ISOLATED",
        ]
    elif kind == "policy-graphic":
        args = common + [
            "-fill",
            "#7b362a",
            "-draw",
            "rectangle 72,242 744,848",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "32",
            "-annotate",
            "+126+322",
            "STRANDS",
            "-pointsize",
            "82",
            "-annotate",
            "+120+412",
            "RECOMMENDS",
            "-fill",
            "#171512",
            "-draw",
            "polygon 780,475 1040,475 1040,410 1155,545 1040,680 1040,615 780,615",
            "-draw",
            "rectangle 1194,242 1848,848",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "32",
            "-annotate",
            "+1250+322",
            "POLICY",
            "-pointsize",
            "90",
            "-annotate",
            "+1244+414",
            "DECIDES",
            "-pointsize",
            "25",
            "-annotate",
            "+1250+596",
            "SNAPSHOT   APPROVAL",
            "-annotate",
            "+1250+654",
            "KNOWN COST   LEASE",
            "-fill",
            "#171512",
            "-pointsize",
            "24",
            "-annotate",
            "+72+914",
            "THE MODEL CANNOT GRANT ITSELF PERMISSION",
        ]
    elif kind == "worker-graphic":
        args = common + [
            "-fill",
            "#171512",
            "-draw",
            "rectangle 0,154 1920,1014",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "27",
            "-annotate",
            "+76+238",
            "AUTHORIZED FALLBACK / CANDIDATE WORKSPACE",
        ]
        boxes = (
            (90, 330, "01", "ONE WRITER"),
            (545, 330, "02", "SOURCE HASH"),
            (1000, 330, "03", "FIXED ARGV"),
            (1455, 330, "04", "ACTIVE LEASE"),
        )
        for x, y, number, label in boxes:
            args += [
                "-fill",
                "#7b362a",
                "-draw",
                f"rectangle {x},{y} {x + 320},{y + 320}",
                "-fill",
                "#f3f1ea",
                "-pointsize",
                "78",
                "-annotate",
                f"+{x + 34}+{y + 34}",
                number,
                "-pointsize",
                "29",
                "-annotate",
                f"+{x + 34}+{y + 230}",
                label,
            ]
        args += [
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "28",
            "-annotate",
            "+90+782",
            "PROMPTS / DIFFS / LOGS / REPOSITORY NOTES",
            "-fill",
            "#d98c75",
            "-pointsize",
            "43",
            "-annotate",
            "+90+838",
            "UNTRUSTED INPUT",
        ]
    elif kind == "verify-graphic":
        args = common + [
            "-fill",
            "#c5bfb1",
            "-pointsize",
            "34",
            "-annotate",
            "+92+290",
            "AGENT REPORT",
            "-fill",
            "#777065",
            "-pointsize",
            "112",
            "-annotate",
            "+86+392",
            "DONE",
            "-fill",
            "#7b362a",
            "-draw",
            "rectangle 70,550 800,570",
            "-fill",
            "#171512",
            "-draw",
            "polygon 840,490 1080,490 1080,430 1190,560 1080,690 1080,630 840,630",
            "-draw",
            "rectangle 1230,226 1848,894",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "160",
            "-annotate",
            "+1300+302",
            "13",
            "-pointsize",
            "38",
            "-annotate",
            "+1302+520",
            "PROTECTED",
            "-pointsize",
            "72",
            "-annotate",
            "+1298+575",
            "CHECKS",
            "-fill",
            "#d98c75",
            "-pointsize",
            "24",
            "-annotate",
            "+1304+740",
            "OUTSIDE WORKER SCOPE",
            "-fill",
            "#171512",
            "-pointsize",
            "27",
            "-annotate",
            "+82+856",
            "A CLAIM IS EVIDENCE. A TEST RESULT IS A DECISION.",
        ]
    elif kind == "daemon-graphic":
        args = common + [
            "-fill",
            "#777065",
            "-draw",
            "rectangle 80,352 590,710",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "31",
            "-annotate",
            "+132+414",
            "CODEX PLUGIN",
            "-pointsize",
            "62",
            "-annotate",
            "+126+485",
            "BRIDGE",
            "-fill",
            "#7b362a",
            "-pointsize",
            "25",
            "-annotate",
            "+132+612",
            "PROCESS EXITS",
            "-fill",
            "#171512",
            "-draw",
            "polygon 640,475 920,475 920,410 1035,545 920,680 920,615 640,615",
            "-draw",
            "rectangle 1080,230 1840,872",
            "-fill",
            "#f3f1ea",
            "-pointsize",
            "30",
            "-annotate",
            "+1140+305",
            "LOCAL DAEMON",
            "-pointsize",
            "78",
            "-annotate",
            "+1134+374",
            "STAYS UP",
            "-fill",
            "#d98c75",
            "-pointsize",
            "27",
            "-annotate",
            "+1140+554",
            "EVENT LEDGER",
            "-annotate",
            "+1140+610",
            "CHECKPOINT STORE",
            "-annotate",
            "+1140+666",
            "APPROVALS / BUDGETS / LEASES",
            "-fill",
            "#171512",
            "-pointsize",
            "25",
            "-annotate",
            "+82+914",
            "DURABILITY LIVES OUTSIDE THE STDIO PROCESS",
        ]
    else:
        raise ValueError(f"unknown editorial graphic: {kind}")
    args.append(str(output))
    run(tuple(args))


def extract_frame(source: Path, seconds: float, output: Path) -> None:
    """Freeze a legible frame from a real Playwright recording."""
    run(
        (
            "ffmpeg",
            "-y",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            str(output),
        )
    )


def make_overlay(
    output: Path,
    number: str,
    eyebrow: str,
    title: str,
    status: str,
    closing: bool,
) -> None:
    args = [
        "magick",
        "-size",
        "1920x1080",
        "xc:none",
        "-fill",
        "#f3f1eae8",
        "-draw",
        "rectangle 0,0 1920,154",
        "-gravity",
        "northwest",
        "-font",
        "Helvetica-Bold",
        "-pointsize",
        "20",
        "-fill",
        "#7b362a",
        "-annotate",
        "+72+38",
        f"{number} / {eyebrow}",
        "-pointsize",
        "48",
        "-fill",
        "#171512",
        "-annotate",
        "+70+74",
        title,
    ]
    if status:
        args.extend(
            [
                "-fill",
                "#171512e8",
                "-draw",
                "rectangle 0,1014 1920,1080",
                "-font",
                "Helvetica-Bold",
                "-pointsize",
                "22",
                "-fill",
                "#f3f1ea",
                "-annotate",
                "+72+1036",
                status,
            ]
        )
    if closing:
        args.extend(
            [
                "-fill",
                "#171512dc",
                "-draw",
                "rectangle 1010,690 1920,1080",
                "-font",
                "Helvetica-Bold",
                "-pointsize",
                "52",
                "-fill",
                "#f3f1ea",
                "-annotate",
                "+1080+760",
                "DOVET.SITE",
                "-font",
                "Helvetica",
                "-pointsize",
                "27",
                "-annotate",
                "+1080+840",
                "Professional Agents",
            ]
        )
    args.append(str(output))
    run(tuple(args))


def render_scene(
    source: Path,
    overlay: Path,
    audio: Path,
    output: Path,
    seconds: float,
    start: float,
    illustration: bool,
) -> None:
    source_args = (
        ("-loop", "1", "-i", str(source))
        if illustration
        else (
            "-stream_loop",
            "-1",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(source),
        )
    )
    if illustration:
        base_filter = (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,zoompan=z='min(zoom+0.00018,1.035)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,setsar=1[base]"
        )
    else:
        base_filter = "[0:v]scale=1920:1080,fps=30,setsar=1[base]"
    filters = (
        f"{base_filter};"
        "[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[label];"
        "[base][label]overlay=0:0:format=auto[v];"
        f"[2:a]aformat=channel_layouts=stereo,apad=pad_dur={seconds:.3f},"
        f"atrim=duration={seconds:.3f}[a]"
    )
    run(
        (
            "ffmpeg",
            "-y",
            *source_args,
            "-loop",
            "1",
            "-i",
            str(overlay),
            "-i",
            str(audio),
            "-filter_complex",
            filters,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            f"{seconds:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
        )
    )


def make_thumbnail(frame: Path, output: Path) -> None:
    run(
        (
            "magick",
            str(frame),
            "-resize",
            "1280x720^",
            "-gravity",
            "center",
            "-extent",
            "1280x720",
            "-fill",
            "#f3f1eaf2",
            "-draw",
            "rectangle 0,0 1280,206",
            "-gravity",
            "northwest",
            "-font",
            "Helvetica-Bold",
            "-pointsize",
            "64",
            "-fill",
            "#171512",
            "-annotate",
            "+52+42",
            "KEEP THE WORK.",
            "-pointsize",
            "34",
            "-fill",
            "#7b362a",
            "-annotate",
            "+56+132",
            "CHANGE THE AGENT.",
            "-fill",
            "#171512e8",
            "-draw",
            "rectangle 0,660 1280,720",
            "-pointsize",
            "20",
            "-fill",
            "#f3f1ea",
            "-annotate",
            "+54+680",
            "REAL LOCAL EVIDENCE  /  AWS LIMITATION DISCLOSED",
            str(output),
        )
    )


def main() -> int:
    plan: dict[str, Any] = json.loads(PLAN.read_text(encoding="utf-8"))
    narration = plan.get("scenes")
    if not isinstance(narration, list) or len(narration) != len(SCENES):
        raise RuntimeError("narration plan does not match concise film scenes")
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    soundtrack = PRIVATE / "sound" / "dovet-bed.wav"
    captions: list[tuple[float, float, str]] = []
    records: list[dict[str, object]] = []
    offset = 0.0
    with tempfile.TemporaryDirectory(prefix="dovet-story-") as temporary:
        work = Path(temporary)
        graphics = STORY / "graphics"
        graphics.mkdir(parents=True, exist_ok=True)
        for kind in (
            "checkpoint-graphic",
            "policy-graphic",
            "worker-graphic",
            "verify-graphic",
            "daemon-graphic",
        ):
            make_editorial_graphic(kind, graphics / f"{kind}.png")
        extract_frame(STORY / "console.webm", 4.0, graphics / "console-still.png")
        extract_frame(STORY / "provider-status.webm", 5.0, graphics / "provider-still.png")
        rendered: list[Path] = []
        for index, ((number, eyebrow, title, kind, start, status), scene) in enumerate(
            zip(SCENES, narration, strict=True), start=1
        ):
            audio = PRIVATE / "higgsfield" / "narration" / f"scene-{index:02d}.wav"
            seconds = duration(audio) + 0.2
            source = (
                graphics / f"{kind}.png"
                if kind.endswith("-graphic") or kind.endswith("-still")
                else source_for(kind)
            )
            if not source.is_file():
                raise FileNotFoundError(f"story source is missing: {source}")
            overlay = work / f"overlay-{number}.png"
            make_overlay(overlay, number, eyebrow, title, status, index == 12)
            clip = work / f"scene-{number}.mp4"
            render_scene(
                source,
                overlay,
                audio,
                clip,
                seconds,
                start,
                kind == "illustration" or kind.endswith("-graphic") or kind.endswith("-still"),
            )
            rendered.append(clip)
            captions.append((offset, offset + duration(audio), str(scene["text"])))
            records.append(
                {
                    "id": scene["id"],
                    "seconds": seconds,
                    "source": str(source.relative_to(ROOT)),
                    "source_sha256": sha256(source),
                    "source_start": start,
                    "audio_sha256": sha256(audio),
                    "status_label": status,
                }
            )
            offset += seconds
        concat = work / "concat.txt"
        concat.write_text("".join(f"file '{clip.name}'\n" for clip in rendered), encoding="utf-8")
        joined = work / "joined.mp4"
        run(
            (
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "1",
                "-i",
                str(concat),
                "-c",
                "copy",
                str(joined),
            )
        )
        add_soundtrack(joined, soundtrack, OUTPUT, offset)
        thumbnail_frame = work / "thumbnail-frame.png"
        run(
            ("ffmpeg", "-y", "-ss", "52", "-i", str(OUTPUT), "-frames:v", "1", str(thumbnail_frame))
        )
        make_thumbnail(thumbnail_frame, SUBMISSION / "thumbnail-final.png")

    write_captions(captions, SUBMISSION)
    (SUBMISSION / "captions.srt").replace(SUBMISSION / "captions-final.srt")
    (SUBMISSION / "captions.vtt").replace(SUBMISSION / "captions-final.vtt")
    media = probe(OUTPUT)
    final_seconds = float(media["format"]["duration"])
    if not 174 <= final_seconds < 180:
        raise RuntimeError(f"concise film duration is outside 2:54-3:00: {final_seconds}")
    manifest = {
        "schema_version": "1",
        "status": "READY_WITH_DISCLOSED_AWS_BLOCKER",
        "path": str(OUTPUT.relative_to(ROOT)),
        "sha256": sha256(OUTPUT),
        "duration_seconds": final_seconds,
        "viewport": {"width": 1920, "height": 1080},
        "voice": "Higgsfield Dylan preset; 12 previously timing-gated scenes",
        "generated_visual": {
            "provider": "OpenAI built-in image generation",
            "purpose": "opening and closing editorial illustration only",
            "path": "private-artifacts/video/dovet-editorial-opener.png",
        },
        "native_graphics": (
            "Five deterministic ImageMagick diagrams for checkpoint, policy, worker, "
            "verification, and daemon concepts"
        ),
        "recording": "Four Playwright captures of the actual local console and site",
        "scenes": records,
        "limitations": [
            "AWS authorization blocked all Bedrock model invocations.",
            "The film claims no successful Strands/Bedrock recovery or AgentCore deployment.",
            "The owner must perform a normal-speed playback review before upload.",
        ],
    }
    (SUBMISSION / "final-film-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
