#!/bin/bash

function makePackage(){
	zip=$1; shift
	echo
	echo "*** Zipping $zip..."
	cd dist
	zip -r $zip plugins/ $*
	cd ..
}

echo "*** Building Linux binary"
linuxBinary=$(pyinstaller build.spec)
echo 
if [ $? -ne 0 ]; then
	echo "*** Build failed :("
	exit 1
fi

echo "*** Building Windows binary"
windowsBinary=$(wine pyinstaller build.spec | tr -d "[:space:]")
if [ $? -ne 0 ]; then
	echo "*** Build failed :("
	exit 1
fi

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


makePackage ${linuxBinary%.*}.zip $linuxBinary
makePackage ${windowsBinary%.*}.zip $windowsBinary
makePackage ${linuxBinary%-*}-all.zip $linuxBinary $windowsBinary
