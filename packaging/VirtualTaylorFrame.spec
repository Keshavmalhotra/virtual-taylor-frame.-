# PyInstaller build definition for the existing GUI launcher.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("accessible_output2")

a = Analysis(
    ["..\\main.pyw"],
    pathex=["."],
    binaries=[],
    datas=[("..\\USER_GUIDE.md", ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    [],
    name="VirtualTaylorFrame",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    exclude_binaries=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="VirtualTaylorFrame",
)
