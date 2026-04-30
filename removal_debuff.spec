# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['removal_debuff.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'PIL', 'Pillow',
        'setuptools', 'pkg_resources', 'unittest', 'test',
        'xmlrpc', 'pydoc', 'doctest', 'argparse',
        'email', 'html', 'http', 'urllib', 'xml',
        'logging', 'bz2', 'lzma', 'sqlite3',
        'asyncio', 'concurrent', 'multiprocessing',
        'lib2to3', 'distutils', 'ensurepip',
        'tkinter.test', 'idlelib', 'turtledemo',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='removal_debuff',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
