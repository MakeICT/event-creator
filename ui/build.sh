#!/bin/bash

line="__all__ = ["
for f in *.ui; do
	name=$(echo $f | cut -d . -f 1)
	pyside-uic -x -i 0 -o $name.py $f
	echo "Found $name"
	uiList+=($name)
	line="$line\"$name\","
done

line="$line]"

#sed -i "s/__all__.*/$line/" __init__.py
