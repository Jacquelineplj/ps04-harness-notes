# Brief creation instructions

You are preparing three connected editorial briefs from the accepted evidence. Each
brief drives one article and one video script, so it must contain everything the
writers need: a title, the editorial question, a central argument, a synthesis, the
limitations, and a list of claims with evidence locators.

Series structure (piece ids are fixed):
- `01` What changed, and which developments matter most to this audience?
- `02` Which claims withstand scrutiny, and where are the evidence or interpretations in tension?
- `03` What do these developments imply for the audience, and what should they watch next?

Requirements for every brief:
1. `argument` is one distinct central argument, stated in two or three sentences. The
   three arguments must differ in substance, not only in framing; piece 03 builds on 01
   and 02 rather than restating them.
2. `claims` holds five to nine claims. Each claim has a `claim_id` (`<piece>-c<n>`, for
   example `02-c3`), a one-sentence `statement`, a `type`, and one or more `evidence`
   references.
   - `reported_fact`: something the source documents directly (a number, a behaviour, an event).
   - `source_claim`: something the source asserts or argues; attribute it to the source.
   - `inference`: your own conclusion from combining at least two items; explain the
     reasoning in `synthesis`.
3. Evidence references name the item_id and version_id exactly as given, and a
   locator:
   - written items: `{"type": "text", "quote": "<verbatim passage copied character
     for character from the retained text, 10 to 60 words>"}`
   - audio or video items: `{"type": "segment", "segment_id": "<id from the transcript>"}`
   Quotes must be copied exactly; do not paraphrase, trim mid-word, or stitch two
   passages. A claim whose passage you cannot find is not made.
   The cited passage must itself contain the specific fact, number, or assertion in
   the claim's statement, and it must come from the source the statement attributes
   it to. Never attach a passage from a different item to a claim about another
   source (for example, a claim about a paper must cite that paper's text, not a
   newsletter that mentions it). If only a secondary source discusses a result,
   phrase the claim as what that secondary source reports.
4. Each brief cites evidence from at least three independent publishers and includes at
   least one `inference` claim that combines two or more items. Across the three
   briefs, use written, YouTube, and podcast evidence.
5. `synthesis` (one or two paragraphs) explains what the pieces of evidence add up to
   and what your analysis adds beyond any single source: a mismatch between an
   announcement and practitioner experience, a reason two results differ, a constraint
   shared across developments.
6. `limitations` names the strongest counterargument or the most important gap
   (missing perspectives, unmeasured claims, single-case evidence) honestly; do not
   manufacture disagreement.
7. Distinguish facts, source claims, interpretation, and uncertainty throughout.
   Vendor claims carry their commercial context. Numbers without method are
   "reported" not "shown".
8. Use only the evidence provided. Never invent sources, quotes, numbers, or dates.
