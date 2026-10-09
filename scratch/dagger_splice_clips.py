#!/usr/bin/env python3
"""Splice the Blender-authored dagger clips into the SOURCE rig bytes (A2).

    python3 scratch/dagger_splice_clips.py SOURCE.rigged.glb BLENDER_EXPORT.glb OUT.glb

Why: a Blender glTF re-export re-splits WH_Body (25805 -> 25812 verts, same as
the shipped combat-chain / combat-sword GLBs). The dagger law is "node / mesh /
skin structure IDENTICAL to the source, adding ONLY the 3 clips", so OUT is the
SOURCE json + binary verbatim with the 3 WH_Dag* animations appended: their
sampler input/output data is copied byte-for-byte from the Blender export
(scratch/blender_dagger_clips.py, export_force_sampling=False) into new
bufferViews/accessors at the end of the BIN chunk, channel targets remapped by
node NAME. Every pre-existing byte range (mesh, skin, images, the 6 original
clips) is untouched. Reads SOURCE only; never writes it.
"""
import json
import struct
import sys

NEW = ["WH_DagSlashR2L", "WH_DagSlashL2R", "WH_DagSlashR2Lb"]
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
CS = {5126: 4, 5123: 2, 5125: 4, 5121: 1}


def load(p):
    b = open(p, "rb").read()
    assert b[:4] == b"glTF"
    off, js, bn = 12, None, None
    while off < len(b):
        ln, ty = struct.unpack_from("<II", b, off)
        off += 8
        if ty == 0x4E4F534A:
            js = json.loads(b[off:off + ln])
        elif ty == 0x004E4942:
            bn = b[off:off + ln]
        off += ln
    return js, bn


def acc_bytes(js, bn, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    n = NC[a["type"]] * CS[a["componentType"]]
    assert bv.get("byteStride", n) == n, "strided animation accessor"
    o = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    return bn[o:o + a["count"] * n]


def main(src, blend, out):
    S, sb = load(src)
    E, eb = load(blend)
    assert len(S["buffers"]) == 1
    assert not any(a["name"] in NEW for a in S.get("animations", [])), "source already has dagger clips"
    sidx = {n.get("name"): i for i, n in enumerate(S["nodes"])}
    bin_ = bytearray(sb)
    added = {}
    for an in E["animations"]:
        if an["name"] not in NEW:
            continue
        samplers, cache = [], {}
        for sm in an["samplers"]:
            ids = []
            for key in ("input", "output"):
                ei = sm[key]
                if ei not in cache:
                    data = acc_bytes(E, eb, ei)
                    while len(bin_) % 4:
                        bin_.append(0)
                    S["bufferViews"].append({"buffer": 0, "byteOffset": len(bin_), "byteLength": len(data)})
                    bin_ += data
                    ea = E["accessors"][ei]
                    na = {"bufferView": len(S["bufferViews"]) - 1, "componentType": ea["componentType"],
                          "count": ea["count"], "type": ea["type"]}
                    for k in ("min", "max", "normalized"):
                        if k in ea:
                            na[k] = ea[k]
                    S["accessors"].append(na)
                    cache[ei] = len(S["accessors"]) - 1
                ids.append(cache[ei])
            samplers.append({"input": ids[0], "output": ids[1],
                             "interpolation": sm.get("interpolation", "LINEAR")})
        channels = []
        for ch in an["channels"]:
            nm = E["nodes"][ch["target"]["node"]]["name"]
            channels.append({"sampler": ch["sampler"],
                             "target": {"node": sidx[nm], "path": ch["target"]["path"]}})
        S.setdefault("animations", []).append({"name": an["name"], "channels": channels, "samplers": samplers})
        added[an["name"]] = len(channels)
    assert sorted(added) == sorted(NEW), f"missing clips in export: {added}"
    while len(bin_) % 4:
        bin_.append(0)
    S["buffers"][0]["byteLength"] = len(bin_)
    js = json.dumps(S, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(out, "wb") as f:
        f.write(b"glTF" + struct.pack("<II", 2, total))
        f.write(struct.pack("<I", len(js)) + b"JSON" + js)
        f.write(struct.pack("<I", len(bin_)) + b"BIN\x00" + bin_)
    print("spliced", added, "src BIN", len(sb), "-> out BIN", len(bin_), "file", total, "bytes")
    assert bytes(bin_[:len(sb)]) == sb, "source byte range changed"
    print("source BIN prefix byte-identical:", len(sb), "bytes")


if __name__ == "__main__":
    main(*sys.argv[1:4])
