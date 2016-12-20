#!/bin/bash
echo "*** Building Binary"
binary=$(pyinstaller build.spec)

if [ $? -eq 0 ]; then
	echo
	echo "*** Copying plugins..."
	rm -rf dist/plugins
	mkdir dist/plugins
	cp -R src/plugins dist/

	echo
	echo "*** Cleaning up..."
	rm -rf dist/plugins/__init__.py* dist/plugins/__pycache__/
	rm -rf dist/plugins/*/*.pyc
	rm -rf dist/plugins/*/__pycache__/
	rm -rf dist/plugins/GoogleApps/credentials.dat

	echo
	echo "*** Zipping..."
	cd dist
	zip ${binary%.*}.zip $binary plugins/
	cd ..
	
	echo
	echo "*** Done!"
	exit 0
else
	echo
	echo "*** Build failed :("
	
	exit 1
fi
