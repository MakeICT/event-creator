#!/bin/bash

function makePackage(){
	binary=$1
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
	zip -r ${binary%.*}.zip $binary plugins/
	cd ..
	
	echo
	echo "*** Done!"
}

echo "*** Building Linux binary"
linuxBinary=$(pyinstaller build.spec)
if [ $? -eq 0 ]; then
	makePackage $linuxBinary
else
	echo
	echo "*** Build failed :("
fi

echo
echo "*** Building Windows binary"
windowsBinary=$(wine pyinstaller build.spec)
if [ $? -eq 0 ]; then
	makePackage $windowsBinary
else
	echo
	echo "*** Build failed :("
fi
echo
echo "*** Zipping combined package..."
cd dist
zip -r ${linuxBinary%-*}-all.zip $linuxBinary $windowsBinary plugins/
cd ..
