# Assignment 2 example submission

This is an instructor-requested example using Florence-2-base, in the hand-in format specified by A2.pdf. The identifying header denotes an example rather than a real student. The PDF contains the three required sections, followed by references and the AI-assistance/provenance disclosure outside the executive summary. There is no separate instructor commentary or model-running supplement.

## Files to hand in

The generated `hand-in/` directory mirrors the two submission destinations. Its README gives the exact mapping of section screenshots to Crowdmark questions and the PDF to LEARN Dropbox. The distribution archive contains those destination files and their instructions; unzip it before uploading.

- **LEARN Dropbox:** upload only `hand-in/learn/a2-review.pdf`, the complete report. No supplementary files are included, so the handout does not require a ZIP for LEARN.
- **Crowdmark:** upload the PNG images from `hand-in/crowdmark/` to the corresponding sections, in filename order when a section spans two pages.
- Both destinations are required by the assignment. Its deadline is October 19, 11:59pm ET. No uploads were performed by this task.

The package is intended for distribution after the assignment. Students are responsible for observing the handout's AI policy; the instructor example's provenance is disclosed in the PDF.

## Source and reproducibility files

- `a2-review.tex` and `references.bib`: editable report and bibliography. The original student template in the parent directory is preserved.
- `sources/florence-2-base-model-card.md`: the reviewed README at a pinned revision.
- `sources/provenance.json`: documentation URL, revision, access date and content hash.
- `validation.json`: generated PDF and screenshot checks.
- `local-resources.json`: read-only WSL diagnostics, kept outside the student hand-in.

Build with `latexmk -pdf a2-review.tex`, or `tectonic a2-review.tex`. The report uses the supplied template's 11-point letter-paper layout, 1-inch margins and section styles. References begin after a page break. The temporary compiler and PDF-rendering libraries used for this task are in `/tmp`, outside the repository.
