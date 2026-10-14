# Editorial review — run 20261013T213636Z-podcasts-expanded (as of 2026-10-13)

Reviewer: Lingjie Pan (student). Decisions reviewed in `decisions.jsonl`; drafts in
`articles/` and `video_scripts/`; every correction made to the drafts and briefs is
recorded with before/after text and a reason in `corrections.jsonl` (43 entries).
The content checks were rerun after the corrections (`review.json`, passed, 0 errors).

## 1. Accepted items (4 of 27 reviewed)

| Item | AI decision and reason (abridged) | My judgement |
| --- | --- | --- |
| **AWS Has 16,000 APIs. Can MCP Handle It?** (MLOps Community podcast, 2026-09-28) | accept 01/02/03: direct practitioner discussion of MCP at scale — version negotiation, code-mode review difficulty, tool search, injection risk from markdown docs; evidence type: practitioner report from MCP implementers, some commercial incentive. | **Agree.** The transcript substantiates the reason (segments at 15:01 and 30:48 are cited in piece 03). The AI correctly flagged that the speakers build MCP tooling. |
| **Are Harnesses Worth the Cost?** (martinfowler.com, 2026-10-13) | accept 01/02/03: controlled comparison with/without a behavioural harness across two models, 10 runs per condition, 178 acceptance tests, counter-intuitive result; evidence type: measured experiment with described method, limited generalisation. | **Agree on acceptance; one factual error.** The AI's reason says "Martin Fowler reports". The retained text opens "Naresh Jain compares coding agents..." (the site's feed lists the site owner as author). The error propagated into the brief and the piece-02 draft and script ("Fowler's harness experiment"); corrected in all three (see corrections.jsonl) and addressed in policy v2 (attribution from the body, not the feed). |
| **The Agent Said It Was Done. The Database Disagreed.** (ThinkingBox, Hugging Face blog, 2026-10-03) | accept 01/02: benchmark grading terminal database state; 121,680 trials, 67.24% of failures look clean by trajectory proxies; reproducible via OpenEnv; joint Microsoft/HF, vendor-affiliated. | **Agree.** The numbers quoted in the drafts (67.24%, 241 tasks, 67.16% vs 66.50%) were checked against the retained text. I would label the perspective "mixed" rather than "research" because the authors are a vendor team; the drafts already say so. |
| **How Anthropic's Dynamic Workflows Coordinate Claude Agents** (Latent Space, 2026-10-12) | accept 01: reports a vendor presentation with Q&A; presenters' own caveats on budget and cost. | **Agree, with the caveat the draft already carries:** this is secondary reporting of a vendor talk, not a measurement; piece 01 says so explicitly and quotes the presenters' cost caveat rather than the announcement. |

## 2. Rejected or deferred items (5 of 40 reviewed)

| Item | AI decision and reason (abridged) | My judgement |
| --- | --- | --- |
| **Claude Code's Next Era — Thariq Shihipar, Anthropic** (Latent Space podcast, 2026-09-29) | defer: excerpts are "too conversational/fragmentary to extract specific, checkable claims"; transcript capped at 1:00:00 of 1:32:29. | **Disagree.** An Anthropic engineer on the design of a major coding-agent harness is primary practitioner evidence squarely in scope. The selection stage only sees the opening plus three sampled excerpts; the full transcript is only read at the brief stage, which deferred items never reach. This is a sampling limitation, not an editorial one. Policy v2 now says to judge audio/video on the whole episode when title, guest or description name a harness product. |
| **[AINews] TypeSafe/Jev at >$100M ARR...** (Latent Space roundup, 2026-10-10) | reject: a link digest of launches and valuations; the one harness-relevant figure (LangChain's 64% cost cut) is an unverified vendor number buried in a roundup. | **Agree.** In the earlier pass of the same day (run 20261013T212217Z) this item had been *accepted* and its numbers were cited; the policy text was identical, so the difference is model variance. Policy v2 makes roundups secondary by default so the outcome no longer depends on the sample. |
| **Developing Gemini 4 Argon responsibly and safely** (DeepMind, 2026-10-13) | defer: safety layers are harness-relevant, but the page is a vendor announcement citing internal results ("violations reduced nearly twofold") without method. | **Agree.** Correct application of sections 4 and 7: a strong institution making an unmeasured claim is still an unmeasured claim. |
| **Noam Brown — Agent swarms, alignment, & recursive self-improvement** (Dwarkesh podcast, 2026-09-17) | defer: one notable data point (10,000 agents, 130 billion tokens over 88 hours) but mostly reasoning-model scaling and alignment; the swarm claim has no method detail. | **Mostly agree.** The data point would have fitted piece 03's "what to watch" as an attributed source claim; deferring is defensible because nothing in the retained hour describes how the swarm was engineered. Worth revisiting next edition. |
| **Narrative intelligence and the human advantage** (Practical AI, 2026-10-08) | reject: career identity and "narrative intelligence" — workplace commentary with no harness content. | **Agree.** This and the other off-topic podcast rejections in the earlier pass are what triggered the podcast-discovery change (keyword pre-filter, two new sources); the policy was right, the source list was too broad. |

Agreement overall: of the nine decisions examined I agree with seven, partly agree with
one (Noam Brown), and disagree with one (Claude Code episode). The AI's reasons cite
the items' content and name the evidence type, as the policy requires; the two
weaknesses are an attribution taken from feed metadata and the excerpt-sampling limit
for long transcripts.

## 3. Draft review and corrections

- **Attribution (factual):** "Fowler's harness experiment" / "Fowler reports" / "Fowler's
  conditional" changed to Naresh Jain in `briefs.jsonl` (pieces 01, 02, 03 prose and
  claim statements; evidence locators untouched), `articles/02.md` and
  `video_scripts/02.md`. Reason: the retained text and summary identify Naresh Jain as
  the author; martinfowler.com publishes guest authors under the site feed.
- **Cross-reference (factual):** piece 03 referred to "our last edition"; there is no
  previous edition. Changed to "the second piece in this series".
- **Length (editorial):** piece 02 (961 words) and piece 03 (975) were above the 900-word
  target and script 02 narration (793) above 750; trimmed restatements and framing
  sentences only. No claim, marker or number was removed. Final counts: 870 / 895 / 896
  words; narration 644 / 750 / 746.
- **Normalised quotes (2):** `[01-c6]` and `[02-c5]` quote the snapshot paper's PDF
  text, where line-break hyphenation ("pre- registered", "suffi- cient") differs from
  the model's quote; the retained wording is now used verbatim and supports the claims.
- **Numbers spot-checked against retained passages:** ThinkingBox 67.24% / 241 tasks /
  67.16% vs 66.50%; Jellyfish 2.5%, 26%, 83%, 60x; RATED 86.2% to 2.9%; snapshot 4/5 vs
  0/5 and 17/25 vs 6/25; Arize $11.85 to $8.34 and 51 to 0. All present in the sources.

## 4. Remaining limitations

- Podcast evidence is thin in the published series: one episode is cited (piece 03)
  although 14 podcast items were eligible and four were accepted; the writers preferred
  written sources with numbers. The next edition should push the brief stage to use at
  least one audio passage per piece where the evidence supports it.
- Anthropic's own perspective is absent (its YouTube channel yielded no eligible
  long-form video in the window; the Claude Code episode was deferred, see above).
- Every measured result cited is a single study without independent replication; the
  drafts say so in their limitation sections.

## 5. Approval

The drafts, with the corrections above, are ready for publication subject to the
student's sign-off. The current `review_id` after corrections is recorded in
`review.json`; `approval.json` must carry that value.
