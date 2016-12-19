# -*- mode: python -*-

import platform

version = '2.0'

if platform.system() == 'Linux':
	platformExt = 'linux.bin'
else:
	platformExt = 'windows.exe'
	
a = Analysis(
	['main.py'],
	pathex=[],
	binaries=None,
	datas=[],
	hiddenimports=[
		'httplib2',
		'apiclient',
		'html2text',
		'meetup', 'meetup.api', 'requests', 'requests.packages', 'requests.packages.urllib3',
		'selenium', 'selenium.webdriver', 'selenium.webdriver.support', 'selenium.webdriver.support.expected_conditions',
		'email', 'email.mime', 'email.mime.text',
	],
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=None
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
	pyz,
	a.scripts,
	a.binaries,
	a.zipfiles,
	a.datas,
	name='makeict-event-creator-app-v%s-%s' % (version, platformExt),
	debug=True,
	strip=False,
	upx=True,
	console=True
)
