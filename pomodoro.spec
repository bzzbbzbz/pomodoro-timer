# PyInstaller spec. Build from project root:
#   pyinstaller pomodoro.spec
# Output: dist/Pomodoro.exe (onefile)
# Fixes tkinter: include Tcl/Tk DLLs (tcl86t.dll, tk86t.dll) for Windows/Anaconda.

import sys
from pathlib import Path

block_cipher = None

sound_mp3 = Path('sound.mp3')
datas = [(str(sound_mp3), '.')] if sound_mp3.exists() else []

# Tcl/Tk DLLs: _tkinter.pyd loads them at runtime; PyInstaller often misses them (e.g. Anaconda: Library/bin).
tk_dll_names = ('tcl86t.dll', 'tk86t.dll', 'tcl86.dll', 'tk86.dll')
base = Path(sys.base_prefix)
search_dirs = [base, base / 'DLLs', base / 'Library' / 'bin']
tk_binaries = []
for d in search_dirs:
    if not d.is_dir():
        continue
    for name in tk_dll_names:
        p = d / name
        if p.is_file():
            tk_binaries.append((str(p), '.'))
tk_binaries = list(dict.fromkeys(tk_binaries))  # dedupe

a = Analysis(
    ['src/pomodoro/__main__.py'],
    pathex=['src'],
    binaries=tk_binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Pomodoro',
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
