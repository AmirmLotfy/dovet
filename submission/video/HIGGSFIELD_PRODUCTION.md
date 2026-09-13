# Dovet Higgsfield production record

Status: **TIMING PASS — opening, full narration, and blocked review edit prepared; final evidence cut remains gated.**

## Direction

The working application remains the film's primary image. Higgsfield assets are limited to a short
opening motif, restrained motion bridges, a consistent synthetic voice, and post-production. They
must not depict a fake Dovet interaction or replace the actual managed interruption, Strands trace,
worker changes, or protected test result.

The visual motif is one warm mineral paper surface joined by a small dark oxide square. It translates
the product promise without robots, fake terminals, people, stock offices, glowing effects, or
unlicensed reference artwork.

## Verified production choices

- Higgsfield balance checked before generation: 1,262.8 credits.
- Higgsfield balance after the opening and voice audition, before the 12-scene batch: 1,249.3
  credits; observed aggregate change at that checkpoint: 13.5 credits. The exact post-batch balance
  was not observed, so the batch record uses the provider's per-job cost estimates.
- Six-second Seedance 2.5 at 1080p estimated cost: 54 credits.
- Six-second Kling 3.0 Pro at 16:9 with sound disabled estimated cost: 9 credits.
- Kling 3.0 Pro was selected because the validated estimate was one sixth of the Seedance option for
  this simple physical insert.
- Generated job: `05e03908-b293-4786-8fa2-711bf9a3a49c`.
- Output probe: H.264, 1920×1080, 6.041667 seconds.
- Local private asset: `private-artifacts/video/higgsfield/dovet-opening-05e03908.mp4`.
- SHA-256: `99bf785845152e91b49142acfb9f668b5728f0d83149f866da346bd05f9c0cf2`.
- Contact-sheet inspection passed: paper and join remain coherent across the sampled frames; no
  generated lettering, logos, people, glow, or obvious geometry break was observed.

## Voice direction

The first candidate, Higgsfield preset voice `Grady`, was rejected after three bounded attempts:
speech ran 9.81–11.67 seconds, retained an internal pause of at least 0.81 seconds, and the shorter
rewrite measured slow. The current locked candidate is preset voice `Dylan` with Text to Speech V2
and the ElevenLabs variant. Delivery direction stays identical for every take: `neutral American product narrator,
clear dry timbre, calm authority, conversational pace, no trailer voice, starts immediately`.

The accepted timing audition is job `d735e7fd-9d84-4b0f-a3a6-d7acfaff5d41`: 7.89 seconds of speech,
zero internal pauses of 0.8 seconds or longer, 2.79 words per second, and rate `ok`. Its normalized
WAV SHA-256 is `32e720304df287605ddbd7de508182fbca30d703e6a2052c3cfdaaf14ca7f8d4`.
The user can hear the rendered audition in the generation result; accent and timbre still require
normal-speed listening review. The complete 12-scene first pass cost an estimated 10.8 credits.
Eleven takes passed immediately. Scene 12 was rejected at 9.57 seconds, rewritten, and regenerated
once for an estimated 0.9 credits. The accepted replacement is job
`3675851d-ceaa-4bdc-b989-318b511c9218`; it measures 13.57 seconds, 2.73 words per second, and no
internal pause of 0.8 seconds or longer. All twelve accepted takes use the same `voice_id`,
`voice_type`, model, variant, and direction. They pass the measurable duration, rate, and pause
gates. Audio is never time-stretched. Accent and timbre remain pending until the owner listens to
`private-artifacts/video/higgsfield/dovet-narration-review.wav` at normal speed.

## Edit and sound

- Use the generated shot only for the opening and, if useful, a short closing match cut.
- Use restrained deterministic post-production motion for title cards, evidence labels, and UI
  moves so interface text and geometry remain exact.
- Keep screen recording at 1920×1080 and show an on-screen `intentional interruption` label.
- Show `time compressed` only where actual waiting is shortened; preserve source event times.
- Use a low, original procedural bed under narration. Higgsfield's exposed speech tool does not
  generate music or sound effects, so no speech result will be mislabelled as a soundtrack.
- Keep narration intelligible around -16 LUFS integrated, place the bed at least 16 dB below speech,
  and use sparse paper/relay accents only at scene boundaries.
- The deterministic style preview passed H.264/AAC, 1920×1080, 48 kHz stereo, and 8.6-second
  duration checks. It is stored at `private-artifacts/video/dovet-style-preview.mp4` with SHA-256
  `7bfa8d292a25fc7c463d240046ad9d2514f6347564ce24414ad827b91b52b431` and carries a persistent
  `NOT RECOVERY EVIDENCE` label.
- The review-only picture edit uses the complete locked narration, original deterministic music
  bed, actual product/architecture images, and a 4:40 scene plan. Every live-dependent scene carries
  a persistent `CLOUD PROOF BLOCKED — AWS ACCOUNT PROVISIONING` label. Its private manifest records
  hashes and limitations. It is composition evidence, never a substitute for the final live cut.

## Current official guidance reviewed

- Higgsfield's current workflow guide recommends locking the reference image and audio before video
  assembly, then using a traditional timeline editor for compositing and final post-production:
  https://higgsfield.ai/blog/generate-voice-edit-ai-video-one-place
- Its camera-control guide recommends specifying start/end framing, movement speed, easing, lens,
  focus, and lighting rather than relying on a vague cinematic prompt:
  https://higgsfield.ai/blog/ai-video-camera-control
- Its audio guide covers separate voice, music, and sound-effect roles:
  https://higgsfield.ai/blog/higgsfield-audio

No media is uploaded or published by Codex. The owner receives the final local MP4, captions,
thumbnail, and exact metadata for their own YouTube and Devpost submission.
