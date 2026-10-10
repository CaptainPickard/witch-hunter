import re


def orphan_removal():
    """Remove the orphan 'g), handle' fragment after drain_sampler."""
    p = pathlib.Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
    t = p.read_text()
    lines = t.split('\n')
    print('line count before:', len(lines))
    orphan_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == 'g), handle':
            orphan_idx = i
            break
    print('orphan at index:', orphan_idx)
    if orphan_idx is not None:
        del lines[orphan_idx]
        p.write_text('\n'.join(lines))
        print('removed. new count:', len(lines))
    else:
        print('no orphan found')


if __name__ == '__main__':
    orphan_removal()