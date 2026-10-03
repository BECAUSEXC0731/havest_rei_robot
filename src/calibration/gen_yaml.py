#!/usr/bin/env python3
"""Generate clean ROS camera_info YAML from npz calibration result."""

import struct
import zipfile


def read_npz_value(filepath, key, idx):
    with zipfile.ZipFile(filepath) as z:
        with z.open(key + '.npy') as f:
            f.read(80)
            data = f.read()
    vals = struct.unpack('<' + 'd' * (len(data) // 8), data)
    return vals[idx]


base = '/home/xuchang/havest_robot/calib_data'

for cam in ['color', 'ir']:
    npz_path = base + '/' + cam + '/calibration_result.npz'
    try:
        fx = read_npz_value(npz_path, 'mtx', 0)
        fy = read_npz_value(npz_path, 'mtx', 4)
        cx = read_npz_value(npz_path, 'mtx', 2)
        cy = read_npz_value(npz_path, 'mtx', 5)
        k1 = read_npz_value(npz_path, 'dist', 0)
        k2 = read_npz_value(npz_path, 'dist', 1)
        p1 = read_npz_value(npz_path, 'dist', 2)
        p2 = read_npz_value(npz_path, 'dist', 3)
        k3 = read_npz_value(npz_path, 'dist', 4)
        w = int(read_npz_value(npz_path, 'image_width', 0))
        h = int(read_npz_value(npz_path, 'image_height', 0))

        lines = []
        lines.append('camera_name: ' + cam)
        lines.append('image_width: ' + str(w))
        lines.append('image_height: ' + str(h))
        lines.append('camera_matrix:')
        lines.append('  rows: 3')
        lines.append('  cols: 3')
        lines.append('  data:')
        lines.append('  - ' + str(fx))
        lines.append('  - 0.0')
        lines.append('  - ' + str(cx))
        lines.append('  - 0.0')
        lines.append('  - ' + str(fy))
        lines.append('  - ' + str(cy))
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 1.0')
        lines.append('distortion_model: rational_polynomial')
        lines.append('distortion_coefficients:')
        lines.append('  rows: 1')
        lines.append('  cols: 8')
        lines.append('  data:')
        lines.append('  - ' + str(k1))
        lines.append('  - ' + str(k2))
        lines.append('  - ' + str(p1))
        lines.append('  - ' + str(p2))
        lines.append('  - ' + str(k3))
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('rectification_matrix:')
        lines.append('  rows: 3')
        lines.append('  cols: 3')
        lines.append('  data:')
        lines.append('  - 1.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 1.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 1.0')
        lines.append('projection_matrix:')
        lines.append('  rows: 3')
        lines.append('  cols: 4')
        lines.append('  data:')
        lines.append('  - ' + str(fx))
        lines.append('  - 0.0')
        lines.append('  - ' + str(cx))
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - ' + str(fy))
        lines.append('  - ' + str(cy))
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 0.0')
        lines.append('  - 1.0')
        lines.append('  - 0.0')
        lines.append('')

        yaml_str = '\n'.join(lines)
        out = base + '/' + cam + '/' + cam + '_camera_info.yaml'
        with open(out, 'w') as f:
            f.write(yaml_str)

        with open(out) as f:
            c = f.read()
        if 'numpy' in c or 'python' in c.lower():
            print('[ERROR] ' + out + ': contains Python objects!')
        else:
            print('[OK] ' + out)
            print('     fx=%.4f  fy=%.4f  cx=%.4f  cy=%.4f' % (fx, fy, cx, cy))
    except Exception as e:
        print('[SKIP] ' + cam + ': ' + str(e))
