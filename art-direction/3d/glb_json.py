#!/usr/bin/env python3
"""Parse GLB JSON chunk directly: check TEXCOORD_0 presence, primitives, materials."""
import struct, json, sys

def parse(path):
    with open(path, "rb") as f:
        magic, ver, length = struct.unpack("<III", f.read(12))
        clen, ctype = struct.unpack("<II", f.read(8))
        j = json.loads(f.read(clen))
    print("=", path)
    print("meshes:", [(m.get("name"), len(m["primitives"])) for m in j.get("meshes", [])])
    for i, m in enumerate(j.get("meshes", [])):
        for p in m["primitives"]:
            attrs = p.get("attributes", {})
            print("  mesh%d prim: attrs=%s mode=%s material=%s indices=%s" % (
                i, list(attrs.keys()), p.get("mode"), p.get("material"), p.get("indices")))
    print("materials:", [
        {k: v for k, v in mm.items() if k in ("name", "pbrMetallicRoughness", "doubleSided", "alphaMode")}
        for mm in j.get("materials", [])])
    print("textures:", len(j.get("textures", [])), "images:", [
        (im.get("mimeType"), im.get("name")) for im in j.get("images", [])])
    print("accessors count:", len(j.get("accessors", [])))
    # TEXCOORD_0 accessor stats
    meshes = j.get("meshes", [])
    for mi, m in enumerate(meshes):
        for p in m["primitives"]:
            t = p.get("attributes", {}).get("TEXCOORD_0")
            if t is not None:
                acc = j["accessors"][t]
                print("  mesh%d TEXCOORD_0: count=%s min=%s max=%s" % (mi, acc.get("count"), acc.get("min"), acc.get("max")))
            pos = p.get("attributes", {}).get("POSITION")
            if pos is not None:
                acc = j["accessors"][pos]
                print("  mesh%d POSITION: count=%s min=%s max=%s" % (mi, acc.get("count"), acc.get("min"), acc.get("max")))
    # nodes/skin
    print("nodes:", [(n.get("name"), "mesh" in n, "skin" in n) for n in j.get("nodes", [])][:20])
    print("skins:", len(j.get("skins", [])))
    print("animations:", len(j.get("animations", [])))

parse(sys.argv[1] if len(sys.argv) > 1 else "art-direction/3d/assets/races/human-hunter-male.glb")
if len(sys.argv) > 2:
    parse(sys.argv[2])