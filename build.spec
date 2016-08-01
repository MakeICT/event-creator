# -*- mode: python -*-

import platform

version = '1.5'
if platform.system() == 'Linux':
     platformExt = 'linux.bin'
else:
     platformExt = 'windows.exe'

block_cipher = None

a = Analysis(['main.py'],
             pathex=['./'],
             binaries=None,
             datas=[
				('chromedriver', '.'),
				('chromedriver.exe', '.'),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='makeict-event-creator-app-v%s-%s' % (version, platformExt),
          debug=True,
          strip=False,
          upx=True,
          console=True )
