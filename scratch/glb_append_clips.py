#!/usr/bin/env python3
"""Append named animations from a Blender-exported GLB onto a base GLB without
touching a single pre-existing byte of the base's BIN chunk or JSON entries.

    python3 scratch/glb_append_clips.py BASE.glb SRC.glb OUT.glb NAME [NAME ...]

Each SRC animation's sampler input/output accessors are copied (tightly
packed, 4-byte aligned) onto the END of BASE's BIN; new bufferViews /
accessors / animations are appended to the JSON arrays; channel target nodes
are remapped SRC -> BASE by node name. Asserts afterwards:
  - BASE BIN is a byte prefix of OUT BIN,
  - every pre-existing JSON entry (all top-level arrays) is unchanged,
  - OUT animation names = BASE names + NAMEs.
Plain python (struct/json), no numpy, no Blender.
"""
import hashlib
import json
import struct
import sys

CSIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def load(p):
    b = open(p, "rb").read()
    assert b[:4] == b"glTF"
    off, js, bn = 12, None, b""
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
    el = CSIZE[a["componentType"]] * NC[a["type"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or el
    return b"".join(bn[start + k * stride:start + k * stride + el] for k in range(a["count"]))


def save(path, js, bn):
    j = json.dumps(js, separators=(",", ":")).encode()
    j += b" " * (-len(j) % 4)
    bn += b"\0" * (-len(bn) % 4)
    total = 12 + 8 + len(j) + 8 + len(bn)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<II", len(j), 0x4E4F534A) + j)
        fh.write(struct.pack("<II", len(bn), 0x004E4942) + bn)


def main(base_p, src_p, out_p, names):
    B, bb = load(base_p)
    S, sb = load(src_p)
    base_json = json.loads(json.dumps(B))
    have = [a["name"] for a in B.get("animations", [])]
    clash = [n for n in names if n in have]
    assert not clash, f"base already has {clash} - rebuild from the pre-append base"
    src_anims = {a["name"]: a for a in S["animations"]}
    missing = [n for n in names if n not in src_anims]
    assert not missing, f"src lacks {missing}"
    bidx = {n.get("name"): i for i, n in enumerate(B["nodes"])}
    out = bytearray(bb)
    out += b"\0" * (-len(out) % 4)
    for name in names:
        an = src_anims[name]
        amap = {}

        def copy_acc(i):
            if i in amap:
                return amap[i]
            a = dict(S["accessors"][i])
            data = acc_bytes(S, sb, i)
            while len(out) % 4:
                out.append(0)
            B["bufferViews"].append({"buffer": 0, "byteOffset": len(out), "byteLength": len(data)})
            out.extend(data)
            a["bufferView"] = len(B["bufferViews"]) - 1
            a.pop("byteOffset", None)
            B["accessors"].append(a)
            amap[i] = len(B["accessors"]) - 1
            return amap[i]

        samplers = [{"input": copy_acc(s["input"]), "output": copy_acc(s["output"]),
                     "interpolation": s.get("interpolation", "LINEAR")} for s in an["samplers"]]
        channels = []
        for ch in an["channels"]:
            nname = S["nodes"][ch["target"]["node"]]["name"]
            assert nname in bidx, f"node {nname} not in base"
            channels.append({"sampler": ch["sampler"],
                             "target": {"node": bidx[nname], "path": ch["target"]["path"]}})
        B["animations"].append({"name": name, "channels": channels, "samplers": samplers})
        print(f"appended {name}: {len(channels)} channels, {len(amap)} accessors")
    B["buffers"][0]["byteLength"] = len(out) + (-len(out) % 4)
    save(out_p, B, bytes(out))

    # ---- proof: nothing pre-existing changed
    O, ob = load(out_p)
    assert ob[:len(bb)] == bb, "base BIN is not a byte prefix of OUT BIN"
    ob0 = dict(O["buffers"][0])
    ob0["byteLength"] = base_json["buffers"][0]["byteLength"]
    assert [ob0] + O["buffers"][1:] == base_json["buffers"], "buffers changed beyond byteLength"
    for key, arr in base_json.items():
        if key == "buffers":
            continue
        if isinstance(arr, list):
            assert O[key][:len(arr)] == arr, f"pre-existing JSON entries changed in '{key}'"
        else:
            assert O[key] == arr, f"top-level '{key}' changed"
    assert [a["name"] for a in O["animations"]] == have + list(names)
    print(f"PROOF: base BIN ({len(bb)} B, sha256 {hashlib.sha256(bb).hexdigest()[:16]}) is a byte prefix "
          f"of OUT BIN ({len(ob)} B); all {sum(len(v) for v in base_json.values() if isinstance(v, list))} "
          f"pre-existing JSON entries identical; animations {len(have)} -> {len(O['animations'])}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
