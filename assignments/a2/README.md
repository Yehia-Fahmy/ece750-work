# ECE 750T Assignment 2 — Documentation audit

Completed example submission: **Florence-2-base**, assessed for creating searchable records from digitized historical posters and flyers.

The submission uses the supplied template's three sections, 11-point text and 1-inch margins. The executive summary occupies pages 1–2, including its identifying header. References and the AI-assistance disclosure occupy page 3. The report retains the supplied student-identification header.

## Hand-in files

| Destination | Files to upload |
| --- | --- |
| **LEARN Dropbox** | [`a2-yfahmy.pdf`](a2-yfahmy.pdf), the complete three-page report |
| **Crowdmark — Question 1: Context** | [`crowdmark/q1-context.png`](crowdmark/q1-context.png) |
| **Crowdmark — Question 2: Critique** | [`crowdmark/q2-critique-01.png`](crowdmark/q2-critique-01.png), then [`crowdmark/q2-critique-02.png`](crowdmark/q2-critique-02.png) |
| **Crowdmark — Question 3: Proposed changes** | [`crowdmark/q3-proposed-changes.png`](crowdmark/q3-proposed-changes.png) |

The critique continues on page 2, so both Question 2 images are required. Screenshots were rendered from the final PDF; every section word is covered exactly once, in reading order.

The handout requires both submission destinations, by **October 19 at 11:59pm ET**. No supplemental files are needed for this submission: upload the PDF directly to LEARN. LaTeX source is not required. No course-site uploads have been performed.

[`a2-yfahmy.zip`](a2-yfahmy.zip) contains the PDF, four section images and these instructions for convenient distribution. Unzip it and upload the destination-specific files above; the archive itself is not the LEARN submission.

## Editable source and assignment materials

- [`a2-yfahmy.tex`](a2-yfahmy.tex): completed executive summary and disclosure.
- [`references.bib`](references.bib): the six cited references.
- [`A2.pdf`](A2.pdf): assignment handout.
- [`a2-template.zip`](a2-template.zip): unchanged released template.

Build from this directory:

```sh
latexmk -pdf a2-yfahmy.tex
```

Alternatively, use `tectonic a2-yfahmy.tex`, or upload the source and bibliography to Overleaf. References remain after the page break; do not shrink the font or margins.

[`notes/`](notes/) contains research provenance, validation and local-resource diagnostics. Those working notes are not part of the student hand-in. AI assistance is fully allowed under the updated assignment policy communicated on October 14, 2026. The disclosure describes its use for research, analysis, drafting, revision and preparation of the submission files. This policy update supersedes the prose-editing-only restriction printed in the original handout; the released handout itself is preserved.
