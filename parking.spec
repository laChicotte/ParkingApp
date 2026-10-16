# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH)
datas = [
    (str(root / 'logo.png'), '.'),
    (str(root / 'resources' / 'icons'), 'resources/icons'),
    (str(root / 'resources' / 'profil.jpeg'), 'resources'),
    (str(root / 'resources' / 'ukag_bg.png'), 'resources'),
    (str(root / 'resources' / 'config' / 'config.json.template'), 'resources/config'),
]

a = Analysis(
    [str(root / 'run.py')], pathex=[str(root)], binaries=[], datas=datas,
    hiddenimports=['pymysql._auth', 'cryptography.hazmat.primitives.asymmetric.rsa'],
    hookspath=[], hooksconfig={'matplotlib': {'backends': ['TkAgg', 'Agg']}},
    runtime_hooks=[], excludes=['IPython', 'pytest', 'tkinter.test'], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='UKAGParking',
    debug=False, strip=False, upx=False, console=False,
    icon=str(root / 'build' / 'ukag.ico'),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='UKAGParking')
