pyinstaller build.spec

rm -rf dist/plugins
mkdir dist/plugins
cp -R plugins/* dist/plugins/
rm -rf dist/plugins/__init__.py* dist/plugins/__pycache__/
rm dist/plugins/*/*.pyc
rm -rf dist/plugins/*/__pycache__/

