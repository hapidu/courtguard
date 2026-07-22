# CourtGuard — Manual Test Cases (AI Detection Modules)

Since the image, video, and audio detection modules rely on pretrained deep
learning models rather than deterministic logic, they are validated through
manual black-box test cases rather than pytest unit tests (which cover the
combined risk-scoring and security logic instead — see
`tests/test_combined_scoring.py` and `tests/test_api_endpoints.py`).

| Test ID | Module | Input | Expected Behaviour | Actual Result | Status |
|---|---|---|---|---|---|
| TC-01 | Image | Uploaded a real, unedited JPEG photo | System returns a verdict (real/fake) with a confidence score | Verdict: REAL, Confidence: 44.76% | PASS |
| TC-02 | Video | 3-4 second video recorded via Photo Booth | System extracts frames and returns an averaged verdict | Verdict: REAL, Confidence: 81.28%, 8 frames analyzed | PASS |
| TC-03 | Audio | WAV file generated via macOS `say` (synthetic TTS voice) | System returns a verdict with confidence score | Verdict: REAL, Confidence: 100% | PASS |
| TC-04 | Security | API request to `/history` with no API key header | Request rejected | HTTP 401/422 returned | PASS |
| TC-05 | Security | API request to `/history` with incorrect API key | Request rejected | HTTP 401 returned | PASS |
| TC-06 | Security | API request to `/history` with correct API key | Request succeeds | HTTP 200, analyses list returned | PASS |
| TC-07 | Database | Perform an image analysis, then call `/history` | New entry appears with matching evidence name, verdict, and timestamp | Entry appeared correctly | PASS |
| TC-08 | PDF Report | Click "Download PDF Report" after an analysis | A downloadable PDF is generated containing verdict and confidence | PDF downloaded successfully | PASS |
| TC-09 | Combined Scoring | Submit fake verdicts (90%+) for video/image/audio | Overall risk score should be high (>70) and labelled "high risk" | Confirmed via automated test | PASS |
| TC-10 | Combined Scoring | Submit real verdicts (90%+) for video/image/audio | Overall risk score should be low (<40) and labelled "low risk" | Confirmed via automated test | PASS |
| TC-11 | Frontend | Switch tabs after viewing a result | Previous result should clear/hide | Result box hides on tab switch | PASS |
| TC-12 | Frontend | Click Analyze on video (longest-running module) | Loading spinner should display during processing | Spinner displayed correctly | PASS |

## Notes on limitations (for your evaluation/limitations chapter)

- The bundled sample dataset for what was originally the text/phishing module
  was intentionally small (~24 rows) for demonstration purposes; a production
  system would need a dataset with thousands of labelled examples for
  reliable accuracy reporting.
- Pretrained models (image/audio) were evaluated qualitatively here (does the
  system produce a sensible verdict?) rather than against a large labelled
  benchmark dataset (e.g. FaceForensics++), since assembling and running such
  a benchmark was outside the time/compute scope of this project. This is a
  reasonable and explicit limitation to state in your dissertation.
- Video analysis is the slowest module (multiple frame-level inferences per
  video) and would benefit from GPU acceleration in a production deployment.