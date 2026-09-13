# Dovet owner actions

These actions require the account owner or a final approval that Codex must not infer. Complete them
in order so later approvals are based on finished, reviewable evidence.

## 1. Enable the bounded recovery proof

- Use the already-open Amazon Bedrock Nova Micro playground in `us-east-1`; the old Model access
  page is retired and the console says serverless models activate on first invocation.
- Personally review the linked model EULA. Enter a harmless prompt and choose **Run** once only if
  you accept it; using the model constitutes agreement. Do not send credentials or session data.
- Tell Codex whether the playground returns a model response or an exact error. The live runner will still enforce the two-model
  allowlist, deterministic policy, one-request recovery path, and per-model cost cap.

## 2. Review the finished release

After the live recovery, protected tests, recording, and final video pass:

- Review the exact public repository contents and Apache-2.0 release tag.
- Review the final video, thumbnail, captions, description, chapters, Devpost copy, and three
  Builder.aws stories.
- Confirm the package still matches the release you intend to publish. Publication remains an
  owner action, separate from legal attestations.

## 3. Supply account-owned submission fields

- Provide or enter the AWS Builder ID required by the hackathon form.
- Confirm the eligible participant, authorship, contributors, third-party licenses, and any other
  legal declarations shown by Devpost.
- Upload the finished MP4 through your normal YouTube Studio account and set it to Public.
- Deploy the reviewed marketing build and publish the reviewed source repository and release tag.
- Paste the prepared Builder.aws stories and submit the final Devpost form.
- Verify the YouTube watch URL, source URL, website, and Devpost entry in a signed-out browser, then
  preserve the submission confirmation receipt.

Do not place private legal identifiers, credentials, judge-only access details, or account tokens in
the public repository.
