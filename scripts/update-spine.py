#!/usr/bin/env python3
# Version-Timestamp: 2026-09-16 15:20:39 AST
"""Preview an instruction-spine update from a reviewed local source."""
import argparse
import difflib
import importlib.util
from pathlib import Path
import re
import sys

spec=importlib.util.spec_from_file_location('wizard',Path(__file__).with_name('ide-setup.py'))
w=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

def span(text):
    starts=list(re.finditer(r'^<!-- SPINE:START[^\r\n]*-->\r?\n',text,re.M))
    ends=list(re.finditer(r'^<!-- SPINE:END[^\r\n]*-->(?:\r?\n|$)',text,re.M))
    if len(starts)!=1 or len(ends)!=1 or text.count('<!-- SPINE:START')!=1 or text.count('<!-- SPINE:END')!=1 or starts[0].start()>=ends[0].start():
        raise ValueError('Expected one complete, ordered SPINE marker pair')
    return starts[0].start(),ends[0].end()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1]/'AGENTS.md')
    parser.add_argument('--target',type=Path,default=Path('AGENTS.md'))
    parser.add_argument('--apply',action='store_true');parser.add_argument('--confirm',action='store_true')
    args=parser.parse_args()
    if args.apply and not args.confirm:raise ValueError('--apply requires --confirm after reviewing the diff')
    source=w.safe_path(args.source.absolute());target=w.safe_path(args.target.absolute())
    before=target.read_bytes().decode('utf-8');upstream=source.read_bytes().decode('utf-8')
    a,b=span(before);x,y=span(upstream);after=before[:a]+upstream[x:y]+before[b:]
    if not args.apply:
        print(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(target),tofile='reviewed source')),end='')
        print('PREVIEW ONLY - no files changed')
    elif before!=after:
        w.commit_changes({target:after.encode('utf-8')},target.parent)
        print('UPDATED - backup manifest under target directory .ide-config/backups')
    else:print('UNCHANGED')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError) as error:
        print(f'ERROR - {error}',file=sys.stderr);raise SystemExit(2)
