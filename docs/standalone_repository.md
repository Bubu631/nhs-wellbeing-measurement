# Standalone repository layout and preservation

This repository contains the complete NHS wellbeing research direction: the latest measurement-acquisition study at the root and the complete ranking-sensitivity predecessor in `prior_study/`. It does not need the earlier multi-project repository or a sibling research checkout to run the supplied analyses.

## What changed for this repository

The original latest-study tree was copied to the repository root. The predecessor was copied in full to `prior_study/`, with its own experimental code, data tools, data, results, provenance, requirements, manuscript source/PDF and workbook. Existing scientific outputs, source datasets, experiment files and paper files were preserved byte-for-byte. The [source inventory](standalone_migration_source_manifest.json) records the original staged bytes; the [comparison](standalone_verification.json) records the final file-level check and intentionally changed tooling/documentation.

The added JSON profiles map existing runnable commands to the standard-library `scripts/run_profile.py` wrapper. They were added for standalone use and were not used by historical experiments. The default wrapper and default Make target only print information. Actual profile execution requires `--execute`. The full Make workflow now preserves stage ordering explicitly.

Relative links, project navigation and packaging paths were adapted. The main local packager writes `output/release/` under this root and reads the predecessor's existing PDF from `prior_study/paper/main.pdf`. It no longer needs an external delivery directory. The predecessor's optional standalone packager writes `prior_study/output/release/`; its workbook builder/verifier default to `prior_study/artifacts/`. Historical workbook-builder and run-manifest hashes were retained as historical provenance, not replaced with claims that the newly adapted tooling produced the original files.

Citation files identify the two manuscripts separately. `.gitattributes` disables newline conversion to preserve recorded bytes; raw caches, local environments and generated release/verification copies are ignored. Source licences, author-kit notices, negative results and manuscript authorship were preserved. No software licence was invented for third-party material.

## Bounded offline verification

The verification copy was created inside ignored `output/`. All seven JSON profiles were validated with `--dry-run`; all resolved to included Python entry points with existing CLI arguments. The default Make target printed help, both projects' `make -n all` succeeded, and the packager's default invocation listed its assets without writing them.

The existing main and predecessor checks, both supporting-workbook verifiers and the smoke profile were exercised in the disposable copy. Their audit JSON changes remain in that copy; the delivered scientific results and audit files were not overwritten. This is packaging/portability verification, not new experimental evidence or a new full primary study. Exact check status and environment are recorded in the comparison JSON.

The local release builder was also exercised in the disposable copy. It verified ZIP integrity and each member against its source bytes, using this repository's own files. This does not claim a new TeX compilation or server-side arXiv test. Previously recorded paper checks remain available in the historical documentation.

The available audit environment retained NumPy 2.5.3 and SciPy 1.18.1. Missing pandas 3.0.5, openpyxl 3.1.5 and small dependencies were installed only into an ignored verification directory, without upgrading the shared environment. Workbook-only checks also used the available bundled openpyxl runtime. These bounded checks are not a claim that a fresh environment reproduced the complete historical study bit-for-bit.

## Release assets

`python artifact_tools/package_release.py --dry-run` lists planned assets. `python artifact_tools/package_release.py --build` assembles and byte-verifies them locally, without fetching, recomputing studies, contacting a hosting API or publishing:

```text
output/release/
  repository_bundle.zip
  paper.pdf
  paper_source.zip
  anonymous.pdf
  anonymous_source.zip
  supplement.pdf
  decision_brief.pdf
  results.xlsx
  prior_study_paper.pdf
  prior_study_source.zip
  release_manifest.json
  SHA256SUMS.txt
```

`repository_bundle.zip` has one `nhs-wellbeing-measurement/` prefix and includes the complete `prior_study/` tree. It excludes raw third-party download caches, environments, generated release directories and temporary verification artifacts. The predecessor's workbook remains available inside the tree at `prior_study/artifacts/nhs_wellbeing_results.xlsx`. The main source archive renames the unchanged full-paper driver and bibliography output to `main.tex` and `main.bbl` for submission convenience.

## Remaining operational boundaries

Raw-source restoration still requires the recorded official/archive URLs to remain available. The official-source downloaders record new hashes for fresh downloads, so compare those with committed provenance before treating refreshed bytes as original inputs. The historical archive downloader enforces recorded digests. Optional spreadsheet-engine QA needs `@oai/artifact-tool`; the optional discussion-brief builder additionally needs ReportLab. The exploratory memory check uses the Unix `resource` module. These limitations are disclosed in the README; none requires another research repository or private dataset.
