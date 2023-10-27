#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Union
from pathlib import Path

import builtins
import contextlib
import fnmatch
import hashlib
import io
import logging
import os
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import getpass


os.environ['REFINERY_TERM_SIZE'] = '120'

from refinery.lib.meta import SizeInt
from refinery.lib.loader import load_pipeline
from refinery.units import Executable, Unit
from test import SampleStore

logging.disable(logging.CRITICAL)
Executable.Entry = '__DEMO__'

try:
    from IPython.core import magic
except ImportError:
    def register_line_magic(x): return x
    def register_cell_magic(x): return x
else:
    def register_line_magic(f): # noqa
        return magic.register_line_magic(magic.no_var_expand(f))
    def register_cell_magic(f): # noqa
        return magic.register_line_cell_magic(magic.no_var_expand(f))


class FakeTTY:
    def __getattr__(self, k):
        return getattr(sys.stdout, k)

    def isatty(self):
        return True

    def write(self, b: Union[str, bytes]):
        with contextlib.suppress(AttributeError):
            b = b.decode('utf8')
        sys.stdout.write(b)


store = SampleStore()
_open = builtins.open
_stat = os.stat
_root = os.path.abspath(os.getcwd())
_popen = subprocess.Popen


def _virtual_fs_stat(name):
    try:
        data = store.cache[name]
    except KeyError:
        return _stat(name)
    M = stat.S_IMODE(0xFFFF) | stat.S_IFREG
    S = len(data)
    return os.stat_result((
        M,  # ST_MODE
        0,  # ST_INO
        0,  # ST_DEV
        1,  # ST_NLINK
        0,  # ST_UID
        0,  # ST_GID
        S,  # ST_SIZE
        0,  # ST_ATIME
        0,  # ST_MTIME
        0,  # ST_CTIME
    ))


def _virtual_fs_open(name: Union[int, str], mode='r', *args, **kwargs):
    if isinstance(name, int):
        return _open(name, mode, *args, **kwargs)

    path = os.path.abspath(name)
    directory = os.path.abspath(os.path.dirname(path))

    if 'b' not in mode or not directory.startswith(_root):
        return _open(name, mode, *args, **kwargs)

    file_name = path[len(_root):].lstrip(os.path.sep).replace(os.path.sep, '/')

    if 'r' in mode:
        try:
            return io.BytesIO(store.cache[file_name])
        except KeyError:
            return _open(name, mode)

    class VFS(io.BytesIO):
        def close(self) -> None:
            store.cache[file_name] = self.getvalue()
            return super().close()

    return VFS()


def _virtual_fs_popen(*args, **kwargs):
    with tempfile.TemporaryDirectory('.binref') as root:
        root = Path(root)
        for name, data in store.cache.items():
            path = root / name
            os.makedirs(path.parent, exist_ok=True)
            with open(root / name, 'wb') as stream:
                stream.write(data)
        kwargs.update(cwd=root)
        process = _popen(*args, **kwargs)
        process.wait()

        for path in root.glob('**/*'):
            try:
                if not path.is_file():
                    continue
                with open(path, 'rb') as stream:
                    name = path.relative_to(root).as_posix()
                    store.cache[name] = stream.read()
            except Exception:
                pass

    out = process.stdout.read()
    out = out.splitlines(True)
    out = [line for line in out if not getpass.getuser().encode() in line]
    process.stdout = io.BytesIO(b''.join(out))

    return process


subprocess.Popen = _virtual_fs_popen
builtins.open = _virtual_fs_open
os.stat = _virtual_fs_stat
io.open = _virtual_fs_open
sys.stderr = sys.stdout


@register_cell_magic
def emit(line: str, cell=None):
    if cell is not None:
        line = line + re.sub(R'[\r\n]+\s*', '\x20', cell)
        line = re.sub(R'(?<=\[|\])\x20*\|', '|', line)
    load_pipeline.cache_clear()
    load_pipeline(F'emit {line}') | FakeTTY()


class _vef(Unit):
    def __init__(self, *mask):
        pass
    def process(self, data):
        for mask_ in self.args.mask:
            mask = mask_.decode(self.codec)
            for name, data in store.cache.items():
                if not fnmatch.fnmatch(name, mask):
                    continue
                yield self.labelled(data, path=name)


@register_cell_magic
def ef(line: str, cell=None):
    if cell is not None:
        line = line + re.sub(R'[\r\n]+\s*', '\x20', cell)
        line = re.sub(R'(?<=\[|\])\x20*\|', '|', line)
    load_pipeline.cache_clear()
    mask, _, rest = line.partition('|')
    mask = shlex.split(mask)
    vef = _vef.assemble(*mask) 
    vef | load_pipeline(rest) | FakeTTY()


@register_line_magic
def ls(line: str = ''):
    patterns = shlex.split(line)
    for name, data in store.cache.items():
        if patterns and not any(fnmatch.fnmatch(name, p) for p in patterns):
            continue
        print(F'{SizeInt(len(data))!r}', hashlib.sha256(data).hexdigest().lower(), name)


@register_line_magic
def rm(line: str):
    patterns = shlex.split(line, posix=True)
    for name in list(store.cache.keys()):
        if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
            store.cache.pop(name, None)


@register_line_magic
def show(line: str):
    from IPython.display import Image
    return Image(filename=line.strip())


def store_sample(hash: str, name: Optional[str] = None, key: Optional[str] = None):
    store.download(hash, key=key)
    if name is None:
        name = hash
    store.cache[name] = store.cache.pop(hash)


def store_clear():
    store.cache.clear()
