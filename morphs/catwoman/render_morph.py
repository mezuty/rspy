import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_util import *
bpy.ops.wm.open_mainfile(filepath=sys.argv[-3])
out = sys.argv[-2]; views = sys.argv[-1].split(',')
setup_render(samples=64, res=(800, 1000))
# hide legs/head clutter? keep everything visible like the references
V = {
 'front': ((0, 7.5, 3.0), (0, 0, 2.95), 55),
 'q34':   ((4.6, 5.6, 3.5), (0, 0, 2.95), 55),
 'back':  ((-1.2, -7.5, 3.2), (0, 0, 2.95), 55),
 'side':  ((7.5, 0.6, 3.2), (0, 0, 2.95), 55),
 'chest': ((0.6, 3.6, 3.45), (0, 0, 3.2), 50),
 'arm':   ((3.2, 2.6, 2.7), (0.85, 0, 2.6), 50),
 'hand':  ((2.0, 1.6, 1.9), (0.95, 0, 2.0), 60),
 'full':  ((0, 10.5, 2.5), (0, 0, 2.3), 72),
 'full34':((6.2, 8.0, 3.0), (0, 0, 2.3), 72),
 'fullback':((-1.5, -10.5, 2.6), (0, 0, 2.3), 72),
 'legs':  ((2.6, 5.2, 1.5), (0.1, 0, 1.15), 50),
 'boot':  ((2.2, 2.8, 0.85), (0.26, 0, 0.5), 50),
 'bootback': ((1.2, -3.0, 0.7), (0.0, 0, 0.42), 45),
 'hip':   ((2.6, -3.2, 2.4), (0.4, -0.3, 2.05), 55),
}
for v in views:
    loc, tgt, lens = V[v]
    render_view(os.path.join(out, f'cw_{v}.png'), loc, target=tgt, lens=lens)
