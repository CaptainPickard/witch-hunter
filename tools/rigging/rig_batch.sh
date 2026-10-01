#!/usr/bin/env bash
# Rigs frozen races_regen meshes. Every Blender process goes through bl.sh.
set -u -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
src_dir=art-direction/3d/assets/races_regen
out_dir="$src_dir/rigged"
rig_dir=tools/rigging
script_dir="$rig_dir/scripts"
manifest="$rig_dir/rig-manifest.md"
mkdir -p "$out_dir" "$rig_dir/blends" "$rig_dir/logs" "$rig_dir/previews"
if [[ ! -f "$manifest" ]]; then
    printf '# whanim1 rig manifest (append-only run log)\n\n' > "$manifest"
fi
stems=(dwarf-female dwarf-male-smith elf-dawn-refuser-male human-hunter-female
       human-hunter-male orc-female orc-male-warrior undead-ghoul-male
       vampire-female vampire-male-noble)
failures=0
for stem in "${stems[@]}"; do
    if [[ $# -eq 2 && $1 == --only && $2 != "$stem" ]]; then continue; fi
    src="$src_dir/$stem.glb"
    out="$out_dir/$stem.rigged.glb"
    blend="$rig_dir/blends/$stem.rigged.blend"
    preview="$rig_dir/previews/$stem"
    rig_log="$rig_dir/logs/$stem.rig.log"
    verify_log="$rig_dir/logs/$stem.verify.log"
    # Parse only the two documented landmark overrides; no eval or shell injection.
    mapfile -t args < <(python3 - "$rig_dir/char-overrides.json" "$stem" <<'PY'
import json, sys
params = json.load(open(sys.argv[1]))[sys.argv[2]]
assert set(params) <= {'hip-ratio', 'knee-ratio'}, params
for key, value in params.items():
    assert 0 < float(value) < 1, (key, value)
    print('--' + key)
    print(str(value))
PY
)
    override_display=$(python3 - "$rig_dir/char-overrides.json" "$stem" <<'PY'
import json, sys
print(json.dumps(json.load(open(sys.argv[1]))[sys.argv[2]], sort_keys=True))
PY
)
    printf '\n## %s — attempt %s\n- Overrides: `%s`\n' "$stem" "$(date -u +%FT%TZ)" "$override_display" >> "$manifest"
    rig_cmd=("$script_dir/bl.sh" --python "$script_dir/rig_wh_humanoid.py" -- "$src" "$out" --save-blend "$blend" "${args[@]}")
    { printf 'RIG '; printf '%q ' "${rig_cmd[@]}"; printf '\n'; } | tee "$rig_log"
    if ! "${rig_cmd[@]}" >> "$rig_log" 2>&1 || ! test -s "$out" || ! \
        python3 - "$rig_log" <<'PY'
import sys
s=open(sys.argv[1]).read()
raise SystemExit(0 if '[WH] exported ' in s and 'Traceback (most recent call last)' not in s else 1)
PY
    then
        printf '%s\n' "- FAIL: rig command failed or produced no valid export; exact diagnostic: $rig_log" \
                        "- Preview: not produced; $preview" >> "$manifest"
        printf 'RIG FAIL %s (see %s)\n' "$stem" "$rig_log"
        failures=$((failures + 1))
        continue
    fi
    verify_cmd=("$script_dir/bl.sh" --python "$script_dir/verify_wh_glb.py" -- "$out" "$src" \
                --render "$preview" \
                --frames REST:1,WH_Walk:8,WH_Walk:23,WH_Attack1:5,WH_Attack1:9,WH_Death:36)
    { printf 'VERIFY '; printf '%q ' "${verify_cmd[@]}"; printf '\n'; } | tee "$verify_log"
    if "${verify_cmd[@]}" >> "$verify_log" 2>&1 && \
       python3 - "$verify_log" <<'PY'
import sys
s=open(sys.argv[1]).read()
raise SystemExit(0 if s.rstrip().endswith('VERIFY PASS') and 'VERIFY FAIL ' not in s else 1)
PY
    then
        printf '%s\n' '- PASS: `VERIFY PASS`' "- Preview: $preview (REST/Walk/Attack/Death front+side)" \
                        "- Verify log: $verify_log (excursion report, texture and mesh checks)" \
                        "- Anomalies: pending preview inspection; geometry/texture checks passed." >> "$manifest"
        printf 'PASS %s\n' "$stem"
    else
        printf '%s\n' "- FAIL: verifier did not end in VERIFY PASS; exact diagnostic: $verify_log" \
                        "- Preview: $preview (may be incomplete)" >> "$manifest"
        printf 'VERIFY FAIL %s (see %s)\n' "$stem" "$verify_log"
        failures=$((failures + 1))
    fi
done
printf 'BATCH RESULTS: %s failures\n' "$failures"
exit "$failures"
