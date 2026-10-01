#!/bin/sh
# Headless Blender wrapper for this container.
#  - LD_PRELOAD: /usr/local/lib/libsqlite3.so.0 shadows the system lib -> libgdal symbol error.
#  - PATH: a uv-managed python3.13 in ~/.local/bin is found first; Blender then lacks apt numpy
#    (glTF importer fails "No module named 'numpy'"). Force system python3.13.
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libsqlite3.so.0
exec blender -b --factory-startup "$@"
