"""Quick or final preview renders for any morph on a rig that faces +Y.

    python render_views.py <morph.blend> <out_dir> view1,view2,...  [RES=420,520 SAMPLES=10 env vars]

Quick checks: RES=420,520 SAMPLES=10 (seconds). Finals: RES=800,1000 SAMPLES=48."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import morph_toolkit as mt
bpy.ops.wm.open_mainfile(filepath=sys.argv[-3])
out = sys.argv[-2]; views = sys.argv[-1].split(',')
RES = tuple(int(x) for x in os.environ.get('RES', '420,520').split(','))
SAMPLES = int(os.environ.get('SAMPLES', 10))
V = {
 'full':      ((0, 10.5, 2.5), (0, 0, 2.3), 72),
 'full34':    ((6.2, 8.0, 3.0), (0, 0, 2.3), 72),
 'fullback':  ((-1.5, -10.5, 2.6), (0, 0, 2.3), 72),
 'chest':     ((0.4, 3.6, 3.35), (0, 0, 3.15), 50),
 'top34':     ((3.2, 4.2, 3.3), (0, 0, 2.95), 55),
 'top34L':    ((-3.2, 4.2, 3.3), (0, 0, 2.95), 55),
 'topback':   ((-1.0, -4.6, 3.2), (0, 0, 2.95), 55),
 'armR':      ((3.0, 2.4, 2.6), (0.8, 0, 2.5), 50),
 'armL':      ((-3.0, 2.4, 2.6), (-0.8, 0, 2.4), 50),
 'hips':      ((0.6, 3.2, 2.2), (0, 0, 2.05), 50),
 'hipsback':  ((0.6, -3.2, 2.15), (0, 0, 2.05), 50),
 'legs':      ((1.2, 5.0, 1.3), (0, 0, 1.1), 50),
 'shoes':     ((1.4, 2.8, 0.75), (0, 0, 0.45), 50),
 'heel':      ((1.2, -2.6, 0.6), (0, 0, 0.35), 50),
 'forearmL':  ((-2.0, 1.6, 2.7), (-0.8, 0, 2.6), 50),
 'neck':      ((0.3, 2.0, 3.75), (0, 0, 3.6), 50),
}
for v in views:
    loc, tgt, lens = V[v]
    mt.render_view(os.path.join(out, f'{v}.png'), loc, tgt, lens=lens, res=RES, samples=SAMPLES)
