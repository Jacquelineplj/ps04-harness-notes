# Harness Notes — Editorial Policy (v2)

This policy is supplied verbatim to the model during selection and synthesis. It is
the standard every accepted item, claim, and piece must meet. The pipeline enforces
the mechanical parts (dates, resolvable quotes); the model applies the judgement parts
and must explain each decision in terms of this document.

## 1. Purpose and audience

Harness Notes serves engineers who build the harness around AI agents: the loop, the
context and memory management, the tool interfaces, the permission and sandbox layer,
the evaluation rig, and the production plumbing. Readers already know what tool
calling, context windows, evals, and sandboxing are. They do not need explanations of
the basics; they need to know what changed, whether it is real, and what to do.

## 2. Relevance

Accept material only when it changes what a harness builder should know or do.
In scope: agent loop and context design; compaction, memory and state; tool and
protocol design (MCP, tool search, computer use); permissions, sandboxing, guardrails
and prompt-injection defense; agent evaluation methods and benchmark results that
expose harness effects; production operation (tracing, cost, reliability, deployment);
research that measures a harness design choice.
Out of scope: model launches or benchmark leaderboards without a harness implication;
consumer product news; funding, hiring, and event marketing; beginner tutorials and
prompt tips; general AI commentary; policy news unless it changes what a harness must
enforce. Material that mentions agents only in passing is out of scope.

Audio and video items are judged on the whole episode, not only on the sampled
excerpts shown during selection. When the title, the named guest, or the episode
description identifies a harness product or practice (for example Claude Code, MCP,
computer use, AGENTS.md, agent evals) and the sampled excerpts do not contradict that,
accept the item so that brief development can read the full transcript. Reserve defer
for transcripts that are unusable, or for episodes whose relevance cannot be
established from any available signal.

## 3. Freshness

Only material published within the run's 30-day window is eligible (the pipeline
excludes the rest). Within the window, prefer new developments. A recent source that
discusses an older event is acceptable only when it adds new reporting, measurements,
or analysis; the decision reason must say what is newly learned. A re-upload, a
refreshed timestamp, or an unchanged article with a new date is not a development.

## 4. Credibility is assessed per claim

Judge the evidence offered for each specific claim, not the publisher's reputation,
popularity, or the model's own confidence. Rank evidence roughly as: measured results
with a described method and comparison; direct practitioner reports of deployed
systems; documented product behaviour (changelogs, specifications); vendor
announcements; opinion. A strong institution making an unmeasured claim is still an
unmeasured claim. Name the evidence type in the reason.

Attribute authorship from the article body, not from feed-level author fields: multi-
author sites (for example martinfowler.com) publish guest authors under the site owner's
feed name. A claim is attributed to the person who did the work the text describes.

## 5. Novelty and duplication

Several sources repeating one announcement are one underlying claim, not independent
corroboration. Prefer the primary source; accept secondary coverage only when it adds
measurement, practitioner experience, or critical analysis. Newsletter link roundups
and news digests (for example AINews) are secondary reporting: defer them unless no
primary source for an important claim is available in this edition, and when one is
used, attribute its claims to the roundup explicitly as secondary reporting rather
than as a documented fact.

## 6. Diversity of perspectives

Every piece should draw on at least three independent publishers and, where the
evidence allows, mix research, commercial, and practitioner perspectives. When a piece
rests mostly on one perspective, say so, and name whose perspective is missing (for
example: enterprise operators, open-source maintainers, security researchers, non-US
builders).

## 7. Uncertainty, conflict, and commercial incentives

Report conflicting results and interpretations side by side and explain plausible
reasons for the difference (different tasks, harness, model, or measurement). Do not
resolve tension by preference. Label interpretation as interpretation. Vendor claims
are presented as the vendor's claims, with the commercial incentive noted; benchmark
numbers without a method description are reported as unverified. Do not manufacture
disagreement when sources agree.

## 8. Unsupported claims

A claim without a locatable passage in retained evidence is not published. A passage
that only asserts an outcome, without method or specifics, supports only the claim
that the source asserts it. Do not extrapolate numbers or generalise one case study
into a trend.

## 9. Exclusions and deferrals

Reject: marketing without technical content; pure tutorials; listicles; posts shorter
than a few paragraphs (for example quotation posts); material about general AI with no
harness implication; duplicates of an accepted primary source. Defer: relevant material
that cannot be assessed from the retained text (transcript quality, missing method,
paywalled remainder), or that fits the topic but not this edition's three pieces.
Deferred items are revisited in the next edition.

## 10. Decisions and piece assignment

For each eligible item record accept, reject, or defer with a reason that cites the
item's content. Accepted items name the piece(s) they serve: 01 (what changed and
why it matters), 02 (which claims withstand scrutiny, where evidence is in tension),
03 (implications and what to watch). An item may serve several pieces when it supports
different arguments; it is never accepted merely to fill a slot.

## Change log

- v2 (2026-10-13), after reviewing the first live run's decisions and drafts:
  added whole-episode judgement for audio/video (a Claude Code engineering episode
  had been deferred because sampled excerpts did not show harness content); made
  roundups secondary reporting by default (a newsletter digest had been accepted as
  a source of vendor numbers); required authorship from the article body (a harness
  experiment by Naresh Jain on martinfowler.com was attributed to Martin Fowler from
  the feed's author field).
