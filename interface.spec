# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['interface.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [("background_test.png","/Users/ben/Desktop/collage_builder/background_test.png","DATA")]
a.datas += [("main_test.png","/Users/ben/Desktop/collage_builder/main_test.png","DATA")]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='imageMosaic',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
app = BUNDLE(exe,
             name='imageMosaic.app',
             icon=None,
             bundle_identifier=None)
