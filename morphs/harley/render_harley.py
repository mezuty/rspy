"""Preview renders: python render_harley.py <morph.blend> <out_dir> view1,view2,..."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'toolkit'))
import bpy
import morph_toolkit as mt
bpy.ops.wm.open_mainfile(filepath=sys.argv[-3])
out = sys.argv[-2]; views = sys.argv[-1].split(',')
mt.COLL = bpy.data.collections.get('Harley Quinn Morph')
V = {   # rig faces +Y
 'full':     ((0, 10.5, 2.5), (0, 0, 2.3), 72),
 'full34':   ((6.2, 8.0, 3.0), (0, 0, 2.3), 72),
 'full34L':  ((-6.2, 8.0, 3.0), (0, 0, 2.3), 72),
 'fullback': ((-1.5, -10.5, 2.6), (0, 0, 2.3), 72),
 'chest':    ((0.4, 3.6, 3.35), (0, 0, 3.15), 50),
 'hips':     ((0.6, 3.2, 2.2), (0, 0, 2.05), 50),
 'armR':     ((3.0, 2.4, 2.6), (0.8, 0, 2.5), 50),
 'armL':     ((-3.0, 2.4, 2.6), (-0.8, 0, 2.4), 50),
 'legs':     ((1.2, 5.0, 1.3), (0, 0, 1.1), 50),
 'shoes':    ((1.4, 2.8, 0.75), (0, 0, 0.45), 50),
 'back':     ((-0.8, -4.2, 3.0), (0, 0, 2.9), 50),
 'stripe':   ((-2.2, 1.6, 3.0), (-0.75, 0, 2.95), 45),
 'holster':  ((-2.6, -0.6, 2.95), (-0.55, -0.05, 2.95), 50),
 'top34':    ((3.2, 4.2, 3.3), (0, 0, 2.95), 55),
 'topback':  ((-1.0, -4.6, 3.2), (0, 0, 2.95), 55),
 'hipsback': ((0.6, -3.2, 2.15), (0, 0, 2.05), 50),
 'heel':     ((1.2, -2.6, 0.6), (0, 0, 0.35), 50),
 'printzoom': ((0.15, 2.2, 3.42), (0, 0.3, 3.3), 50),
 'neck':     ((0.3, 2.0, 3.75), (0, 0, 3.6), 50),
}
for v in views:
    loc, tgt, lens = V[v]
    mt.render_view(os.path.join(out, f'hq_{v}.png'), loc, tgt, lens=lens, res=tuple(int(x) for x in os.environ.get('RES', '800,1000').split(',')), samples=int(os.environ.get('SAMPLES', 32)))
