#!/bin/bash

function makePackage(){
	zip=$1; shift
	echo
	echo "*** Zipping $zip..."
	cd dist
	zip -r $zip plugins/ $*
	cd ..
}

if [ $# -eq 0 ] || [ "$1" == "linux" ]; then
	echo "*** Building Linux binary"
	linuxBinary=$(pyinstaller build.spec)
	if [ $? -ne 0 ]; then
		echo 
		echo "*** Build failed :("
		exit 1
	fi
fi

if [ $# -eq 0 ] || [ "$1" == "windows" ]; then
	echo "*** Building Windows binary"
	windowsBinary=$(wine pyinstaller build.spec | tr -d "[:space:]")
	if [ $? -ne 0 ]; then
		echo 
		echo "*** Build failed :("
		exit 1
	fi
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


echo
echo "*** Bundling..."
if [ $# -eq 0 ] || [ "$1" == "linux" ]; then
	makePackage ${linuxBinary%.*}.zip $linuxBinary
fi
if [ $# -eq 0 ] || [ "$1" == "windows" ]; then
	makePackage ${windowsBinary%.*}.zip $windowsBinary
fi
makePackage ${linuxBinary%-*}-all.zip $linuxBinary $windowsBinary
