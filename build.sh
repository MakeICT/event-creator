pyinstaller build.spec

rm -rf dist/plugins
mkdir dist/plugins
cp -R plugins/* dist/plugins/
rm -rf dist/plugins/__init__.py* dist/plugins/__pycache__/
rm dist/plugins/*/*.pyc 2>&1
rm -rf dist/plugins/*/__pycache__/ 2>&1

