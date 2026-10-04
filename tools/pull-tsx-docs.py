#!/usr/bin/env python3
"""Pull the docs of the tsx repos into docs/crestron/tsx/ and write the Crestron nav.

Usage:
  tools/pull-tsx-docs.py [--local REPO=PATH ...] [--ref REPO=REF ...]

With --local, the script reads the files of REPO from the git repo at PATH
at the ref, with git archive. It never reads a working tree. Without it,
the script clones https://github.com/tsx-mainline/REPO.git (shallow).

The script stops with a non-zero status on a missing file or a broken link.
"""
import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ORG_URL = "https://github.com/tsx-mainline"
SITE = "crestron/tsx"
OUT = DOCS / SITE
# Nav order of the hand-written pages in the base folder. The index is first.
HAND_PAGES = ["models", "getting-started", "install", "home-assistant",
              "updates", "faq"]
NAV_TITLE = "Crestron"
BEGIN = "# tsx-nav:begin (written by tools/pull-tsx-docs.py)"
END = "# tsx-nav:end"

LINK_RE = re.compile(r"(!?\[[^\]]*\]\()(<?)([^)\s>]+)(>?)((?:\s+\"[^\"]*\")?\))")
REF_RE = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)", re.M)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
NAME_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*")


class PullError(Exception):
    pass


def git(*args, cwd=None, binary=False):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    if res.returncode != 0:
        raise PullError("git %s failed: %s" % (" ".join(args),
                        res.stderr.decode(errors="replace").strip()))
    return res.stdout if binary else res.stdout.decode()


def parse_map(items, what):
    out = {}
    for item in items or []:
        if "=" not in item:
            raise PullError("%s needs REPO=VALUE, got %s" % (what, item))
        key, val = item.split("=", 1)
        out[key] = val
    return out


def fetch(src, ref, local, tmp, extra):
    """Return (repo_dir, tree_files). Extract only the listed paths and the
    files in extra."""
    repo = src["repo"]
    if repo in local:
        git_dir = local[repo]
        rev = ref
    else:
        git_dir = str(tmp / (repo + ".git"))
        git("clone", "--quiet", "--depth", "1", "--branch", ref,
            "--no-checkout", "%s/%s.git" % (ORG_URL, repo), git_dir)
        rev = "HEAD"
    files = set(git("-C", git_dir, "ls-tree", "-r", "--name-only", rev)
                .splitlines())
    dest = tmp / repo
    dest.mkdir()
    specs = [p.rstrip("/") for p in src["paths"]]
    specs += [f for f in extra if f not in specs]
    for spec in specs:
        if spec not in files and not any(f.startswith(spec + "/")
                                         for f in files):
            raise PullError("%s: path %s does not exist at ref %s"
                            % (repo, spec, ref))
    data = git("-C", git_dir, "archive", "--format=tar", rev, "--", *specs,
               binary=True)
    tar_path = tmp / (repo + ".tar")
    tar_path.write_bytes(data)
    with tarfile.open(tar_path) as tar:
        tar.extractall(dest, filter="data")
    return dest, files


def build_map(src, files, base, places):
    """Map each source file to its path under docs/crestron/tsx/. A file
    goes to base/target/, or to its place if places has it."""
    mapping = {}
    for spec in src["paths"]:
        if spec.endswith("/"):
            prefix = spec
            for f in sorted(files):
                if f.startswith(prefix):
                    mapping[f] = f[len(prefix):]
        else:
            mapping[spec] = None
    # A root README.md becomes index.md, or readme.md if index.md exists.
    for spec in [s for s, d in mapping.items() if d is None]:
        name = posixpath.basename(spec)
        if name.lower() == "readme.md" and "/" not in spec:
            taken = "index.md" in mapping.values()
            mapping[spec] = "readme.md" if taken else "index.md"
        else:
            mapping[spec] = name
    mapping = {s: posixpath.join(base, src["target"], d)
               for s, d in mapping.items()}
    mapping.update(places)
    return mapping


def gh_url(repo, ref, path, is_dir):
    kind = "tree" if is_dir else "blob"
    return "%s/%s/%s/%s/%s" % (ORG_URL, repo, kind, ref, path)


def rewrite_text(text, src_path, src, ref, files, mapping):
    repo = src["repo"]
    dirs = {posixpath.dirname(f) for f in files}
    for f in list(dirs):
        while f:
            f = posixpath.dirname(f)
            dirs.add(f)
    dirs.add("")
    src_dir = posixpath.dirname(src_path)
    dest_dir = posixpath.dirname(mapping[src_path])
    errors = []

    def fix(target):
        if (not target or target.startswith("#") or target.startswith("/")
                or SCHEME_RE.match(target)):
            return target
        path, hash_, frag = target.partition("#")
        path = path.split("?")[0]
        if not path:
            return target
        joined = posixpath.normpath(posixpath.join(src_dir, path))
        if joined == ".":
            joined = ""
        if joined.startswith(".."):
            errors.append("%s: link %s leaves the repo" % (src_path, target))
            return target
        is_dir = joined in dirs and joined not in files
        if joined not in files and not is_dir:
            errors.append("%s: link %s points to a missing file"
                          % (src_path, target))
            return target
        dest = mapping.get(joined)
        if is_dir:
            prefix = joined + "/" if joined else ""
            hits = [m for s, m in mapping.items() if s.startswith(prefix)]
            idx = next((s for s, m in mapping.items()
                        if posixpath.basename(m) == "index.md"
                        and posixpath.dirname(s) == joined), None)
            dest = mapping[idx] if idx else None
            if not hits:
                dest = None
        if dest is None:
            return gh_url(repo, ref, joined, is_dir) + (hash_ + frag)
        rel = posixpath.relpath(dest, dest_dir or ".")
        return rel + (hash_ + frag)

    out, in_fence, fence = [], False, ""
    for line in text.split("\n"):
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            tok = m.group(1)
            if not in_fence:
                in_fence, fence = True, tok[0]
            elif tok[0] == fence:
                in_fence = False
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        # Hide inline code spans so the link patterns do not read them.
        spans = []

        def hide(mo):
            spans.append(mo.group(0))
            return "\x00%d\x00" % (len(spans) - 1)

        seg = re.sub(r"`[^`]*`", hide, line)
        seg = LINK_RE.sub(lambda mo: mo.group(1) + mo.group(2)
                          + fix(mo.group(3)) + mo.group(4) + mo.group(5), seg)
        seg = REF_RE.sub(lambda mo: mo.group(1) + fix(mo.group(2)), seg)
        out.append(re.sub(r"\x00(\d+)\x00",
                          lambda mo: spans[int(mo.group(1))], seg))
    if errors:
        raise PullError("\n".join(errors))
    return "\n".join(out)


def add_edit_url(text, url):
    line = "edit_url: %s\n" % url
    if text.startswith("---\n"):
        return "---\n" + line + text[4:]
    return "---\n" + line + "---\n\n" + text


def heading(path):
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end > 0:
            text = text[end + 4:]
    in_fence = False
    for line in text.split("\n"):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
        elif not in_fence and line.startswith("# "):
            title = line[2:].strip().rstrip("#").strip()
            title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
            return title.replace("`", "")
    return path.stem


def order_names(names, order):
    """Sort page names: the index first, then the names in order, then the
    rest in alphabetical order. A name in order has no .md suffix."""
    rank = {n + ".md": i for i, n in enumerate(order or [])}
    rest = sorted(n for n in names if n != "index.md" and n not in rank)
    listed = sorted((n for n in names if n in rank), key=rank.get)
    return (["index.md"] if "index.md" in names else []) + listed + rest


def site_path(path):
    """Path of a page relative to docs/, as the nav needs it."""
    return path.relative_to(DOCS).as_posix()


def page_items(folder, order=None, titles=None):
    """Nav entries for the md files in folder. The index comes first and is
    called Overview. A page in titles gets that title, the other pages get
    the first "#" heading."""
    titles = titles or {}
    names = [p.name for p in folder.iterdir() if p.is_file()
             and p.suffix == ".md"]
    items = []
    for name in order_names(names, order):
        path = folder / name
        if name == "index.md":
            title = "Overview"
        else:
            title = titles.get(site_path(path)) or heading(path)
        items.append({title: site_path(path)})
    return items


def nav_dir(folder, order=None, titles=None):
    """Nav entries for the md files below folder. A subfolder becomes a
    section with the folder name."""
    items = page_items(folder, order, titles)
    for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
        inner = nav_dir(sub, titles=titles)
        if inner:
            items.append({sub.name: inner})
    return items


def toml_inline(node, depth=0):
    pad = "  " * depth
    if isinstance(node, dict):
        (key, val), = node.items()
        if isinstance(val, list):
            body = ",\n".join(pad + "  " + toml_inline(v, depth + 1).lstrip()
                              for v in val)
            return "%s{ %s = [\n%s,\n%s] }" % (pad, json.dumps(key), body, pad)
        return "%s{ %s = %s }" % (pad, json.dumps(key), json.dumps(val))
    return pad + json.dumps(node)


def write_nav(sections, base, groups, titles):
    tsx = page_items(OUT, titles=titles)
    for name, title in groups.items():
        if (OUT / name).is_dir():
            inner = nav_dir(OUT / name, titles=titles)
            if inner:
                tsx.append({title: inner})
    main = page_items(OUT / base, HAND_PAGES, titles)
    main += [{title: nav_dir(OUT / base / target, order, titles)}
             for target, title, order in sections]
    tsx.append({base: main})
    crestron = [{"Overview": "crestron/index.md"}, {"TSX": tsx}]
    block = toml_inline({NAV_TITLE: crestron}, 1) + ","
    cfg = ROOT / "zensical.toml"
    text = cfg.read_text(encoding="utf-8")
    pat = re.compile(r"^[ \t]*%s\n.*?^[ \t]*%s\n" % (re.escape(BEGIN),
                                                    re.escape(END)),
                     re.M | re.S)
    new = "  %s\n%s\n  %s\n" % (BEGIN, block, END)
    if not pat.search(text):
        raise PullError("zensical.toml has no tsx-nav markers")
    cfg.write_text(pat.sub(lambda m: new, text, count=1), encoding="utf-8")


def load_layout(cfg):
    """Return (base, groups) from the [site] table."""
    site = cfg.get("site", {})
    base = site.get("base", "")
    groups = site.get("groups", {})
    for name in [base, *groups]:
        if not NAME_RE.fullmatch(name):
            raise PullError("[site]: %r is not a folder name" % name)
    if base in groups:
        raise PullError("[site]: %s is the base and a group" % base)
    return base, groups


def tracked(path):
    """True if git tracks the file at path in this repo."""
    res = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--",
                          str(path)], capture_output=True, text=True)
    return res.returncode == 0 and bool(res.stdout.strip())


def load_places(cfg, base, groups):
    """Return ({repo: {file: dest}}, {page: nav title}) from the [[place]]
    entries. A dest is relative to docs/crestron/tsx/."""
    repos = {s["repo"] for s in cfg["source"]}
    places, titles, seen = {}, {}, set()
    for entry in cfg.get("place", []):
        repo, file, to = entry.get("repo"), entry.get("file"), entry.get("to")
        if repo not in repos or not file or not to:
            raise PullError("[[place]] needs repo, file and to, and the "
                            "repo needs a [[source]]: %r" % entry)
        dest = posixpath.normpath(to)
        parts = dest.split("/")
        ok = (not to.startswith("/") and ".." not in parts
              and (len(parts) == 1 or parts[0] in groups
                   or (parts[0] == base and len(parts) == 2)))
        if not ok:
            raise PullError("[[place]] %s: %s is not in docs/%s/, in a "
                            "group folder or in the base folder"
                            % (file, to, SITE))
        if dest in seen or tracked(OUT / dest):
            raise PullError("[[place]] %s: docs/%s/%s is in use"
                            % (file, SITE, dest))
        seen.add(dest)
        places.setdefault(repo, {})[file] = dest
        if entry.get("title"):
            titles[posixpath.join(SITE, dest)] = entry["title"]
    return places, titles


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--local", action="append", metavar="REPO=PATH",
                    help="read REPO from the git repo at PATH")
    ap.add_argument("--ref", action="append", metavar="REPO=REF",
                    help="use REF for REPO instead of the list file")
    ap.add_argument("--sources", default=str(ROOT / "tsx-sources.toml"))
    args = ap.parse_args()
    local = parse_map(args.local, "--local")
    refs = parse_map(args.ref, "--ref")
    with open(args.sources, "rb") as fh:
        cfg = tomllib.load(fh)
    default_ref = cfg.get("defaults", {}).get("ref", "main")
    base, groups = load_layout(cfg)
    places, titles = load_places(cfg, base, groups)
    sections = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for src in cfg["source"]:
            repo = src["repo"]
            ref = refs.get(repo, src.get("ref", default_ref))
            print("pull %s at %s%s" % (repo, ref,
                  " (local)" if repo in local else ""), flush=True)
            placed = places.get(repo, {})
            tree, files = fetch(src, ref, local, tmp, placed)
            mapping = build_map(src, files, base, placed)
            target = OUT / base / src["target"]
            if target.exists():
                shutil.rmtree(target)
            count = 0
            for spath, dpath in sorted(mapping.items()):
                dest = OUT / dpath
                dest.parent.mkdir(parents=True, exist_ok=True)
                srcfile = tree / spath
                if spath.endswith(".md"):
                    text = srcfile.read_text(encoding="utf-8")
                    text = rewrite_text(text, spath, src, ref, files,
                                        mapping)
                    text = add_edit_url(text, gh_url(repo, ref, spath, False))
                    dest.write_text(text, encoding="utf-8")
                    if spath not in placed:
                        count += 1
                else:
                    shutil.copyfile(srcfile, dest)
            if not count:
                raise PullError("%s: no markdown files copied" % repo)
            print("  %d pages to docs/%s/%s/%s"
                  % (count, SITE, base, src["target"]))
            for spath, dpath in sorted(placed.items()):
                print("  %s to docs/%s/%s" % (spath, SITE, dpath))
            sections.append((src["target"], src["title"], src.get("order")))
        write_nav(sections, base, groups, titles)
    print("nav written to zensical.toml")


if __name__ == "__main__":
    try:
        main()
    except PullError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)
