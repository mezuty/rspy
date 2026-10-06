"""Minimal end-to-end example using morph_toolkit (a leather vest + belt +
coiled rope on the hip + gloves with claws). Copy this as the starting
template for a new morph.

    python example_build.py <rig.blend> <out_dir>
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import morph_toolkit as mt

RIG, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=RIG)

# 1. map rig parts (fill this in from mt.survey_rig() output - names differ per rig)
PARTS = {'torso': 'Robloxian2014', 'hips': 'Robloxian2013',
         'hand_R': 'Robloxian2010', 'foot_R': 'Robloxian203'}
mt.set_front(mt.detect_front(bpy.data.objects[PARTS['foot_R']]))
print('FRONT =', tuple(mt.FRONT), 'RIGHT =', tuple(mt.RIGHT))
mt.new_collection('Example Morph')

LEATHER = mt.principled('EX_Leather', (0.05, 0.025, 0.015), 0.4, coat=0.25, bump=(260, 0.08))
PIPING = mt.principled('EX_Piping', (0.03, 0.015, 0.01), 0.3, coat=0.4)
STITCH = mt.principled('EX_Stitch', (0.35, 0.28, 0.18), 0.6)
METAL = mt.principled('EX_Brass', (0.75, 0.55, 0.25), 0.25, metal=1.0)
TAPE = mt.principled('EX_Tape', (0.02, 0.02, 0.02), 0.6)

# 2. shell + opening + folds
vest = mt.world_copy(PARTS['torso'], 'EX_Vest', level=1)
mt.offset_shell(vest, 0.016)
zb, zt, half = 3.15, 3.80, 0.2
F, Rt = mt.FRONT, mt.RIGHT
planes = []
for s in (-1, 1):
    a = Rt * (s * half) + Vector((0, 0, zt)); b = Vector((0, 0, zb))
    d = (a - b).normalized()
    planes.append((b, (d.cross(F)).normalized() * s))
mt.cut_opening(vest, planes, lambda c: c.dot(F) > 0 and c.z > zb
               and abs(c.dot(Rt)) < half * (c.z - zb) / (zt - zb))
vest.data.materials.append(LEATHER); mt.smooth(vest)
for s in (-1, 1):
    mt.add_folds(vest, Rt * (s * 0.37) + Vector((0, 0, 2.68)), (0.14, 0.32, 0.16), (0, 0, 1), 0.005, 0.05,
                 face_dir=tuple(Rt * s), min_dot=0.35)
bvh = mt.bvh_of(vest)

# 3. details projected on the surface
objs = []
for s in (-1, 1):
    objs += mt.seam(f'EX_Seam{s}', [(s * 0.32, 3.58), (s * 0.24, 3.3), (s * 0.18, 2.9), (s * 0.22, 2.25)],
                    'front', bvh, (PIPING, STITCH))
zp = mt.project(bvh, mt.catmull([(0, zb), (0, 2.7), (0, 2.22)], 60), 'front')
objs += mt.zipper('EX_Zip', zp, TAPE, METAL)
objs += mt.zipper_pull('EX_ZipPull', zp[0][0], zp[0][1], Vector((0, 0, -1)), METAL)

# 4. belt (band + buckle) on hips, and a braided coil hanging on the right hip
hips = mt.world_copy(PARTS['hips'], 'EX_HipsRef', level=1); mt.offset_shell(hips, 0.016)
hb = mt.bvh_of(hips); bpy.data.objects.remove(hips)
belt = mt.band_ring('EX_Belt', hb, (0, 0), 2.12, 0.05, 0.006, 0.013, LEATHER)
mt.add_bevel(belt, 0.003)
objs += [belt] + mt.buckle('EX_Buckle', hb, (0, 0), 2.12, 90, 0.05, METAL, LEATHER)
side = mt.RIGHT
hit = hb.ray_cast(Vector((0, 0, 2.05)) + side * 5, -side)[0]
assert hit is not None, 'ray missed - check the height against slice_report()'
C = hit + side * 0.09 - Vector((0, 0, 0.17)); fwd = mt.FRONT
coil = [C + fwd * math.cos(t) * 0.13 + Vector((0, 0, 1)) * math.sin(t) * 0.14 + side * (0.05 * t / 25 - 0.025)
        for t in [2 * math.pi * 4 * i / 900 for i in range(900)]]
objs += mt.braid('EX_Rope', coil, 0.013, 0.011, 0.04, PIPING, scale_fn=lambda f: 1 - 0.4 * f)

# 5. glove claws
hand = bpy.data.objects[PARTS['hand_R']]
gl = mt.world_copy(PARTS['hand_R'], 'EX_Glove', level=2); mt.offset_shell(gl, 0.011)
gl.data.materials.append(LEATHER); mt.smooth(gl)
gb = mt.bvh_of(gl)
mn, mx = mt.world_bounds(gl)
for k, f in enumerate((0.2, 0.4, 0.6, 0.8)):
    y = mn.y + (mx.y - mn.y) * f
    h = gb.ray_cast(Vector(((mn.x + mx.x) / 2 + 0.08, y, mn.z - 1)), Vector((0, 0, 1)))
    if h[0]: objs.append(mt.claw(f'EX_Claw{k}', h[0], Vector((0, 0, -1)), -mt.RIGHT, METAL))

# 6. finish: thickness + smoothing, parent, look, save, render
for ob in (vest, gl):
    mt.add_solidify(ob, 0.01); mt.add_subsurf(ob, 2 if ob is vest else 1)
for ob in [vest] + objs[:]:
    if ob.name.startswith(('EX_Belt', 'EX_Buckle', 'EX_Rope')):
        mt.parent_to_part(ob, PARTS['hips'])
    elif ob.name.startswith('EX_Claw'):
        mt.parent_to_part(ob, PARTS['hand_R'])
    else:
        mt.parent_to_part(ob, PARTS['torso'])
mt.parent_to_part(gl, PARTS['hand_R'])
mt.add_studio_look()
mt.render_view(os.path.join(OUT, 'example_front.png'), mt.FRONT * 7.5 + Vector((0.8, 0, 3.0)),
               (0, 0, 2.7), lens=55, samples=24)
mt.render_view(os.path.join(OUT, 'example_side.png'), mt.RIGHT * 6 + mt.FRONT * 2 + Vector((0, 0, 2.6)),
               (0, 0, 2.4), lens=55, samples=24)
mt.add_studio_look()   # restore EEVEE + viewport settings after Cycles renders
mt.save_deliverables(OUT, 'Example_Morph')
print('DONE')
