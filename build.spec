# -*- mode: python ; coding: utf-8 -*-
# Spec do PyInstaller para gerar o executável do Tex2HTML.
#
# Uso (no Windows, dentro da pasta do projeto):
#     pip install -r requirements.txt pyinstaller
#     pyinstaller build.spec
#
# O executável final fica em dist/Tex2HTML.exe (arquivo único, sem console).

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

# assets/ traz Header.png e orcid.png (referenciados no HTML gerado).
datas = [("assets", "assets")]
# pypandoc_binary embute o Pandoc dentro do pacote pypandoc; coletamos esses arquivos.
datas += collect_data_files("pypandoc")
binaries = collect_dynamic_libs("pypandoc")
# Garante que todos os submódulos do pacote tex2ojs entrem no executável.
hiddenimports = ["PIL._tkinter_finder"] + collect_submodules("tex2ojs")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    a.binaries,
    a.datas,
    [],
    name="Tex2HTML",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # sem janela de terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
