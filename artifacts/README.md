# Evidence artifacts

This directory contains sanitized, synthetic evidence suitable for review. Private raw traces, recordings, account identifiers and secrets stay under ignored private artifact paths.

Every generated report records its source commit when one exists, command, tested versions, timestamp and unresolved blockers. A handoff example is not execution evidence.

`ui-evidence-rail-fixture.png` is deterministic browser-layout evidence. It is not a live provider
run. The recording pipeline accepts only a separate validated PASS receipt from the live recovery.

`higgsfield-media-evidence.json` records generation IDs, local checksums, and the observed aggregate
credit change. Generated media remains in the ignored private artifact directory. It is production
material, not evidence that the blocked cloud recovery passed.

`video-style-preview.json` validates the local 8.6-second H.264/AAC production look test. The MP4
itself remains private and visibly says that it is not recovery evidence.

`portable-bundle-cli.json` records an end-to-end CLI verify and separate-directory restore using
temporary owner data. The restored Unicode payload is byte-identical and no temporary data remains.
