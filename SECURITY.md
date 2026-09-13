# Security policy

Please report security issues privately to the repository owner before opening a public issue.
Include the affected version, reproduction steps, and the least sensitive evidence needed to
confirm the problem. Do not include credentials, private repositories, raw model transcripts, or
user data.

Dovet controls only runs it starts through a supported adapter. Its local API binds to loopback and
requires a one-use pairing exchange or an owner-only bridge credential. Recovery proposals from
Strands are advisory: deterministic policy, budget, approval, snapshot, and lease checks decide
whether an action may execute.

Checkpoint selection excludes credential-like filenames and common dependency, build, and VCS
directories. Users must still review a project policy before enabling managed work. A local machine
must remain awake for local execution; Dovet does not provide remote access to arbitrary local
repositories.

Supported security updates currently target the latest tagged release. Until a first public tag
exists, this repository is pre-release and no supported release is claimed.
