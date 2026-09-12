#!/usr/bin/env python3
"""Assemble local standalone release files; default lists assets, never uploads."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output" / "release"
REPO_NAME = "nhs-wellbeing-measurement"
COPIES = {
    "paper.pdf": "paper/full.pdf",
    "anonymous.pdf": "paper/anonymous.pdf",
    "supplement.pdf": "paper/supplement.pdf",
    "decision_brief.pdf": "docs/nhs_decision_brief.pdf",
    "results.xlsx": "results/nhs_aisi_results.xlsx",
    "prior_study_paper.pdf": "prior_study/paper/main.pdf",
}
ARCHIVES = ["paper_source.zip", "anonymous_source.zip", "prior_study_source.zip", "repository_bundle.zip"]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for source, member in sorted(entries, key=lambda item: item[1]):
            info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        for source, member in entries:
            assert hashlib.sha256(archive.read(member)).hexdigest() == sha(source)


def shared_sources(paper):
    names = ["main_content.tex", "extended_content.tex", "supplement_content.tex",
             "theory_sections.tex", "theory_proofs.tex", "references.bib"]
    entries = [(paper / name, name) for name in names]
    entries += [(p, str(p.relative_to(paper))) for folder in ["figures", "tables"]
                for p in (paper / folder).glob("*") if p.suffix in {".pdf", ".tex"}]
    return entries


def repository_entries():
    excluded_parts = {".git", ".venv", ".venv-data", "node_modules", "__pycache__", "raw", "output", "preview", "qa"}
    excluded_suffixes = {".pyc", ".aux", ".log", ".blg", ".fls", ".fdb_latexmk", ".out"}
    entries = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(ROOT)
        if any(p in excluded_parts for p in rel.parts) or path.suffix in excluded_suffixes:
            continue
        if path.name == ".DS_Store" or "_local_check" in path.name or "_smoke" in path.name:
            continue
        if "vintage_data" in rel.parts and path.suffix in {".xlsx", ".zip", ".pdf", ".html", ".gz"}:
            continue
        if "data" in rel.parts and "extracted" in rel.parts and path.name != "extraction_manifest.json":
            continue
        entries.append((path, str(Path(REPO_NAME) / rel)))
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Write and byte-verify archives inside output/release")
    parser.add_argument("--dry-run", action="store_true", help="List release files without writing them (default)")
    args = parser.parse_args()
    if args.build and args.dry_run:
        parser.error("Choose --build or --dry-run")
    names = [*COPIES, *ARCHIVES, "release_manifest.json", "SHA256SUMS.txt"]
    for name in names:
        print(f"output/release/{name}")
    if not args.build:
        print("Planning only. No archive, upload or scientific rerun was performed.")
        return
    for name in COPIES.values():
        assert (ROOT / name).is_file(), name
    DEST.mkdir(parents=True, exist_ok=True)
    for name, source in COPIES.items():
        shutil.copyfile(ROOT / source, DEST / name)
    paper = ROOT / "paper"
    shared = shared_sources(paper)
    write_zip(DEST / "paper_source.zip", [(paper / "full.tex", "main.tex"), (paper / "full.bbl", "main.bbl")] + shared)
    anon_names = ["anonymous.tex", "anonymous.bbl", "supplement.tex", "supplement.bbl", "aaai2027.sty", "aaai2027.bst", "author_kit_manifest.json"]
    write_zip(DEST / "anonymous_source.zip", [(paper / name, name) for name in anon_names] + shared)
    prior = ROOT / "prior_study" / "paper"
    prior_sources = [(p, str(p.relative_to(prior))) for p in prior.rglob("*")
                     if p.is_file() and (p.name in {"main.tex", "main.bbl", "references.bib"}
                        or p.parent.name == "figures" and p.suffix == ".pdf"
                        or p.parent.name == "tables" and p.suffix == ".tex")]
    write_zip(DEST / "prior_study_source.zip", prior_sources)
    entries = repository_entries()
    write_zip(DEST / "repository_bundle.zip", entries)
    outputs = {name: {"bytes": (DEST / name).stat().st_size, "sha256": sha(DEST / name)} for name in [*COPIES, *ARCHIVES]}
    manifest = {"version": "1.0.0", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "repository_url": "https://github.com/Bubu631/nhs-wellbeing-measurement",
                "scope": "Local standalone packaging and byte verification only; historical scientific outputs are preserved, no new experiment or publication is represented.",
                "builder_sha256": sha(Path(__file__)), "archive_prefix": REPO_NAME + "/",
                "repository_files": len(entries), "outputs": outputs}
    (DEST / "release_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    checks = [*outputs, "release_manifest.json"]
    (DEST / "SHA256SUMS.txt").write_text("".join(f"{sha(DEST / name)}  {name}\n" for name in checks))
    print(json.dumps({"status": "packaged_and_byte_verified", "files": len(names), "uploaded": False}, indent=2))


if __name__ == "__main__":
    main()
