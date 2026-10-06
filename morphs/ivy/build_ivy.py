"""Poison Ivy morph for the Starter 2.0 Rig, built with morph_toolkit.

    python build_ivy.py <rig.blend> <out_dir>
    blender -b --python build_ivy.py -- <rig.blend> <out_dir>

TOP pass: strapless leaf-tipped sweetheart bodice with vine panel lines,
leaf-vein cups and small leaves; opera gloves with a pointed leaf top, veins,
finger lines and elbow creases; vines with leaves and tendrils spiralling down
both arms and curling over her left shoulder onto the chest.
LOWER pass (later): leotard legs, thigh vines with thorns, leaf-topped boots.
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'toolkit'))
import bpy, bmesh
from mathutils import Vector
import morph_toolkit as mt

RIG, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=RIG)
random.seed(5)
BUILD_LOWER = False

PARTS = {
    'torso': 'Robloxian2014', 'hips': 'Robloxian2013',
    'upperarm_R': 'Robloxian2012', 'lowerarm_R': 'Robloxian2011', 'hand_R': 'Robloxian2010',
    'upperarm_L': 'Robloxian209', 'lowerarm_L': 'Robloxian208', 'hand_L': 'Robloxian207',
    'upperleg_R': 'Robloxian201', 'lowerleg_R': 'Robloxian202', 'foot_R': 'Robloxian203',
    'upperleg_L': 'Robloxian204', 'lowerleg_L': 'Robloxian205', 'foot_L': 'Robloxian206',
}
mt.set_front(mt.detect_front(bpy.data.objects[PARTS['foot_R']]))
F, RT, UP = mt.FRONT, mt.RIGHT, mt.UP
mt.new_collection('Poison Ivy Morph')
GROUPS = {k: [] for k in PARTS}
SIDES = (('R', 1), ('L', -1))


def add(group, *obs):
    for o in obs:
        if isinstance(o, (list, tuple)): GROUPS[group].extend(x for x in o if x is not None)
        elif o is not None: GROUPS[group].append(o)


# ------------------------------------------------------------------ materials
M_SUIT = mt.principled('IV_Suit_Green', (0.018, 0.105, 0.028), 0.36, coat=0.35, coat_rough=0.2, bump=(240, 0.05))
M_SUIT_DARK = mt.principled('IV_Suit_DarkGreen', (0.006, 0.04, 0.01), 0.32, coat=0.4, coat_rough=0.15)
M_GLOVE = mt.principled('IV_Glove_Green', (0.018, 0.1, 0.026), 0.36, coat=0.4, coat_rough=0.15, bump=(300, 0.05))
M_LEAF_A = mt.principled('IV_Leaf_Bright', (0.12, 0.40, 0.05), 0.45, coat=0.25, coat_rough=0.2, bump=(320, 0.04))
M_LEAF_B = mt.principled('IV_Leaf_Mid', (0.06, 0.27, 0.04), 0.42, coat=0.25, coat_rough=0.2, bump=(320, 0.04))
M_VEIN = mt.principled('IV_Vein', (0.012, 0.07, 0.016), 0.5)
M_CUP = mt.principled('IV_Cup_Leaf', (0.03, 0.15, 0.035), 0.34, coat=0.4, coat_rough=0.15, bump=(260, 0.05))
M_STEM = mt.principled('IV_Vine_Stem', (0.05, 0.11, 0.025), 0.55, coat=0.1, bump=(180, 0.2))


def leaf_on(name, co, n, along, group, length=0.06, width=0.034, kind='pointed', side=1, lift=0.01,
            out_angle=55, curl=0.06):
    """Leaf growing off a surface point: rises out of the surface at out_angle
    from the 'along' direction, tilted to one side."""
    a = math.radians(out_angle)
    t = (along - n * along.dot(n)).normalized()
    b = n.cross(t) * side
    direction = (t * math.cos(a) * 0.5 + b * math.sin(a) + n * 0.32).normalized()   # mostly flat but clear of the surface
    normal = (n - direction * n.dot(direction)).normalized()
    m = M_LEAF_A if random.random() < 0.55 else M_LEAF_B
    add(group, mt.leaf(name, co + n * lift, direction, normal, m, length=length, width=width, kind=kind,
                       curl=curl, twist=random.uniform(-15, 15), vein_mat=M_VEIN))


# =========================================================== 1. BODICE (strapless, leaf-tipped sweetheart)
bod = mt.world_copy(PARTS['torso'], 'IV_Bodice', level=2)
mt.offset_shell(bod, 0.014)


def navel_w(c):
    if c.dot(F) < 0.1 or c.z < 2.3 or c.z > 2.6: return 0.0
    d = math.hypot(c.dot(RT) / 0.10, (c.z - 2.435) / 0.09)
    return min(1.0, max(0.0, 1.3 * (1.0 - d)))


mt.smooth_region(bod, navel_w, 160)
# a corset spans the cleavage: straight span between the cup peaks per row, long fade, then fill pits
me = bod.data
rows = {}
for v in me.vertices:
    s, f = v.co.dot(RT), v.co.dot(F)
    if f > 0.05 and abs(s) < 0.22 and 2.95 < v.co.z < 3.45:
        rows.setdefault(int(round(v.co.z / 0.01)), []).append(v)
for k, rv in rows.items():
    L = [v for v in rv if -0.22 < v.co.dot(RT) < -0.1]; R_ = [v for v in rv if 0.1 < v.co.dot(RT) < 0.22]
    if not L or not R_: continue
    pl = max(L, key=lambda v: v.co.dot(F)); pr = max(R_, key=lambda v: v.co.dot(F))
    sl, fl = pl.co.dot(RT), pl.co.dot(F); sr, fr = pr.co.dot(RT), pr.co.dot(F)
    fade = max(0.0, min(1.0, (3.45 - k * 0.01) / 0.12))
    for v in rv:
        s, f = v.co.dot(RT), v.co.dot(F)
        if sl < s < sr:
            t = (s - sl) / (sr - sl)
            target = fl + (fr - fl) * t - 0.012 * math.sin(math.pi * t)   # a gentle corset dip
            if target > f: v.co += F * (target - f) * fade
mt.fill_pits(bod, lambda c: (max(0.0, 1 - abs(c.dot(RT)) / 0.16) * max(0.0, 1 - abs(c.z - 3.25) / 0.2)
                             if c.dot(F) > 0.1 else 0.0), F, 50)
# corset nip: subtle horizontal tension folds at the waist sides
for s_ in (-1, 1):
    mt.add_folds(bod, RT * (s_ * 0.37) + Vector((0, 0, 2.66)), (0.14, 0.32, 0.16), (0, 0, 1), 0.004, 0.05,
                 face_dir=tuple(RT * s_), min_dot=0.35)

TIP_A = 60.0           # angle of each cup's leaf tip from the side (0) towards the front (90)


def top_z(a):
    """Sweetheart top edge under the leaf cups: flat across the back, a soft
    rise over each cup, a V dip at the centre front."""
    a = a % 360
    if a > 180: return 3.3                               # back
    m = a if a <= 90 else 180 - a                         # mirror the two cups
    if m <= TIP_A:
        return 3.3 + 0.05 * math.sin(math.pi / 2 * m / TIP_A)
    t = (m - TIP_A) / (90 - TIP_A)
    return 3.35 - 0.13 * t ** 0.8


mt.cut_by_curve(bod, (0, 0), top_z, keep_above=False)
bod.data.materials.append(M_SUIT); mt.smooth(bod)
BB = mt.bvh_of(bod)
add('torso', bod)

# rolled neckline edge
add('torso', mt.tube('IV_Bodice_Edge', mt.ring_points([BB], (0, 0), 0, 0.004, nseg=240,
                                                         z_fn=lambda a: top_z(a) - 0.006), 0.0085, M_SUIT_DARK))


def piping(name, ctrl, mode, bvh, r=0.0045, n=60, center=(0, 0), group='torso'):
    p = mt.project(bvh, mt.catmull(ctrl, n), mode, center)
    if len(p) > 2:
        add(group, mt.tube(name, [c + nn * 0.0015 for c, nn in p], r, M_SUIT_DARK))
    return p


VINE_LINES = []
# proxy surface at the bodice's outer level (torso + 0.022) so the cup leaves can
# rise above the neckline without a kink at the bodice edge
_px = mt.world_copy(PARTS['torso'], '_tmp_proxy', level=2); mt.offset_shell(_px, 0.022)
PX = mt.bvh_of(_px); bpy.data.objects.remove(_px)


def leaf_outline(base, tip, width, n=40):
    """Pointed leaf outline in (s, z) between base and tip."""
    bx, bz = base; tx, tz = tip
    L = math.hypot(tx - bx, tz - bz); ux, uz = (tx - bx) / L, (tz - bz) / L; vx, vz = -uz, ux
    left, right = [], []
    for i in range(n + 1):
        u = i / n
        w = width / 2 * (math.sin(math.pi * u) ** 0.8) * (1.1 - 0.3 * u)
        cx, cz = bx + ux * u * L, bz + uz * u * L
        left.append((cx + vx * w, cz + vz * w)); right.append((cx - vx * w, cz - vz * w))
    return left + right[::-1][1:-1], (ux, uz), (vx, vz), L


for s in (-1, 1):
    # each cup is a big leaf: base under the bust, tip rising above the neckline, outward
    base, tip = (s * 0.1, 2.98), (s * 0.29, 3.53)
    poly, (ux, uz), (vx, vz), L = leaf_outline(base, tip, 0.25)
    add('torso', mt.patch(f'IV_CupLeaf{s}', PX, poly, 0.002, 0.005, M_CUP, 'front'))
    rim = mt.project(PX, poly + [poly[0]], 'front')
    add('torso', mt.tube(f'IV_CupLeafEdge{s}', [c + n * 0.007 for c, n in rim], 0.0055, M_SUIT_DARK))
    mid2d = [(base[0] + ux * L * u, base[1] + uz * L * u) for u in [k / 20 * 0.93 for k in range(21)]]
    mid = mt.project(PX, mid2d, 'front')
    add('torso', mt.tube(f'IV_CupMidrib{s}', [c + n * 0.0075 for c, n in mid], 0.0042, M_SUIT_DARK,
                         radii=[1 - 0.6 * k / 20 for k in range(21)]))
    for k, u0 in enumerate((0.25, 0.45, 0.65)):
        for sg in (-1, 1):
            w = 0.25 / 2 * (math.sin(math.pi * (u0 + 0.14)) ** 0.8) * 0.8
            v2d = [(base[0] + ux * L * (u0 + 0.14 * t) + vx * sg * w * t, base[1] + uz * L * (u0 + 0.14 * t) + vz * sg * w * t)
                   for t in (0, 0.5, 1)]
            vp = mt.project(PX, mt.catmull(v2d, 10), 'front')
            add('torso', mt.tube(f'IV_CupVein{s}{k}{sg}', [c + n * 0.0072 for c, n in vp], 0.0028, M_SUIT_DARK))
    # under-cup line sweeping into the centre-front V
    VINE_LINES.append(piping(f'IV_UnderCup{s}', [(s * 0.44, 3.24), (s * 0.3, 3.03), (s * 0.15, 2.97), (s * 0.03, 2.9)],
                             'front', BB))
    # converging panel lines towards the waist, then down
    VINE_LINES.append(piping(f'IV_PanelV{s}', [(s * 0.15, 2.97), (s * 0.08, 2.75), (s * 0.03, 2.55), (s * 0.02, 2.2)],
                             'front', BB))
    # side panel lines
    VINE_LINES.append(piping(f'IV_PanelSide{s}', [(s * 0.46, 3.22), (s * 0.38, 2.95), (s * 0.3, 2.68), (s * 0.34, 2.4),
                                                  (s * 0.4, 2.2)], 'front', BB))
    # back princess lines
    piping(f'IV_PanelBack{s}', [(s * 0.3, 3.28), (s * 0.2, 3.0), (s * 0.15, 2.7), (s * 0.2, 2.2)], 'back', BB)
# centre-back line
piping('IV_PanelBackC', [(0, 3.28), (0, 2.8), (0, 2.2)], 'back', BB)

# small leaves sprouting along the panel lines
kk = 0
for line in VINE_LINES:
    if not line or len(line) < 10: continue
    for idx in (int(len(line) * 0.6),):
        co, n = line[idx]
        along = line[min(idx + 1, len(line) - 1)][0] - line[max(idx - 1, 0)][0]
        leaf_on(f'IV_BodiceLeaf{kk}', co, n, along, 'torso', length=0.11, width=0.07,
                side=1 if kk % 2 else -1, out_angle=60)
        kk += 1
# a leaf pointing up from the centre V of the neckline
co, n = mt.project(BB, [(0, 3.21)], 'front')[0]
add('torso', mt.leaf('IV_NecklineLeaf', co + n * 0.008, (UP * 1 + n * 0.2).normalized(), n, M_LEAF_A, length=0.09,
                     width=0.065, kind='ivy', curl=0.1, vein_mat=M_VEIN))

# =========================================================== 2. OPERA GLOVES with a pointed leaf top
GLOVE = {}
for side, s in SIDES:
    out_a = 0 if s > 0 else 180
    ua = mt.world_copy(PARTS[f'upperarm_{side}'], f'IV_Glove_Upper_{side}', level=2)
    la = mt.world_copy(PARTS[f'lowerarm_{side}'], f'IV_Glove_Lower_{side}', level=2)
    hd = mt.world_copy(PARTS[f'hand_{side}'], f'IV_Glove_Hand_{side}', level=2)
    for ob, off in ((ua, 0.012), (la, 0.012), (hd, 0.011)):
        mt.offset_shell(ob, off)
    for ob in (ua, la):
        mt.add_folds(ob, RT * (s * 0.74) + F * 0.12 + Vector((0, 0, 2.79)), (0.26, 0.24, 0.14),
                     tuple(RT * (s * 0.25) + UP), 0.009, 0.055, face_dir=tuple(F), min_dot=0.0)
    cu = mt.slice_center(ua, 3.0)

    def gtop(a, out_a=out_a):
        d = math.radians(((a - out_a + 180) % 360) - 180)
        return 2.96 + 0.27 * max(0.0, math.cos(d)) ** 6       # sharp leaf point on the outer arm

    mt.cut_by_curve(ua, cu, gtop, keep_above=False)
    for ob in (ua, la, hd):
        ob.data.materials.append(M_GLOVE); mt.smooth(ob)
    ub, lb, hb = mt.bvh_of(ua), mt.bvh_of(la), mt.bvh_of(hd)
    GLOVE[side] = (ua, la, hd, ub, lb, hb, cu)
    add(f'upperarm_{side}', ua); add(f'lowerarm_{side}', la); add(f'hand_{side}', hd)
    # rolled top edge following the leaf point
    add(f'upperarm_{side}', mt.tube(f'IV_GloveEdge_{side}', mt.ring_points([ub], cu, 0, 0.003, nseg=200,
                                     z_fn=lambda a, g=gtop: g(a) - 0.005), 0.0065, M_SUIT_DARK))
    # veins on the leaf point
    piping(f'IV_GloveMidrib_{side}', [(out_a, 3.15), (out_a, 3.05), (out_a, 2.93), (out_a, 2.85)], 'cyl', ub,
           r=0.0035, n=30, center=cu, group=f'upperarm_{side}')
    for k, z0 in enumerate((3.08, 3.0, 2.93)):
        for sg in (-1, 1):
            piping(f'IV_GloveVein_{side}{k}{sg}', [(out_a, z0), (out_a + sg * (10 + 5 * k), z0 - 0.06)], 'cyl', ub,
                   r=0.0025, n=12, center=cu, group=f'upperarm_{side}')
    # outer seam down the glove + finger lines on the back of the hand
    cl = mt.slice_center(la, 2.6)
    piping(f'IV_GloveSeam_{side}', [(out_a, 2.85), (out_a, 2.6), (out_a, 2.3)], 'cyl', lb, r=0.0035, n=30, center=cl,
           group=f'lowerarm_{side}')
    for y in (-0.135, -0.03, 0.07):
        p = mt.project(hb, mt.catmull([(y, 1.74), (y, 1.86), (y, 1.97)], 20), 'right' if s > 0 else 'left')
        if len(p) > 2:
            add(f'hand_{side}', mt.tube(f'IV_GloveFinger_{side}{y}', [c + n * 0.0015 for c, n in p], 0.004, M_SUIT_DARK))
    # wrist band of tiny leaves
    wrist_bvh = mt.bvh_union([la, hd])
    for i in range(6):
        a = out_a - 75 + 30 * i
        p = mt.surface_path([wrist_bvh], lambda z: mt.slice_center(la, 2.3), [(a, 2.3)], 0.002)
        if p:
            co, n = p[0]
            leaf_on(f'IV_WristLeaf_{side}{i}', co, n, UP, f'lowerarm_{side}', length=0.1, width=0.066,
                    side=1 if i % 2 else -1, out_angle=70, lift=0.003)

# =========================================================== 3. VINES: arm spirals + shoulder/chest vine
arm_skin = {}
for side, s in SIDES:
    objs = [mt.world_copy(PARTS[f'{p}_{side}'], f'_tmp_{p}', level=1) for p in ('upperarm', 'lowerarm', 'hand')]
    arm_skin[side] = (mt.bvh_union(objs), objs)

for side, s in SIDES:
    ua, la, hd, ub, lb, hb, cu = GLOVE[side]
    skin_bvh, tmp_objs = arm_skin[side]
    out_a = 0 if s > 0 else 180

    def axis(z, ua=ua, la=la):
        return mt.slice_center(ua if z > 2.8 else la, z)

    samples = []
    N = 160
    for i in range(N):
        f = i / (N - 1)
        z = 3.48 - f * (3.48 - 2.34)
        a = out_a + s * (30 + 760 * f) + 10 * math.sin(f * 17)
        samples.append((a, z))
    path = mt.surface_path([skin_bvh, ub, lb, hb], axis, samples, 0.018)
    pts = [c for c, n in path]
    # split by body part so each piece follows its own bone
    upper = [i for i, (c, n) in enumerate(path) if c.z > 2.8]
    cut = upper[-1] + 1 if upper else 0
    if cut > 2:
        add(f'upperarm_{side}', mt.vine(f'IV_ArmVine_U_{side}', pts[:cut + 1], 0.017, M_STEM, taper=(1.0, 0.8)))
    if len(pts) - cut > 2:
        add(f'lowerarm_{side}', mt.vine(f'IV_ArmVine_L_{side}', pts[cut:], 0.017, M_STEM, taper=(0.8, 0.35)))
    # leaves alternating along the vine + a few tendrils
    for k, i in enumerate(range(8, len(path) - 4, 16)):
        co, n = path[i]
        along = path[i + 1][0] - path[i - 1][0]
        grp = f'upperarm_{side}' if co.z > 2.8 else f'lowerarm_{side}'
        big = 1.0 - 0.35 * (i / len(path))
        for j, (sg, sc_) in enumerate(((1, 1.0), (-1, 0.82))):     # leaves grow in pairs at each node
            leaf_on(f'IV_ArmLeaf_{side}{k}_{j}', co, n, along, grp, length=0.16 * big * sc_, width=0.11 * big * sc_,
                    kind='ivy' if (k + j) % 3 == 0 else 'pointed', side=sg * (1 if k % 2 else -1),
                    out_angle=60 + 15 * j)
        if k % 4 == 2:
            add(grp, mt.tendril(f'IV_ArmTendril_{side}{k}', co, (along.normalized() * 0.3 + n * 0.5).normalized(), n,
                                M_STEM, length=0.075, radius=0.0042))
    for o in tmp_objs: bpy.data.objects.remove(o)

# vine curling over her left shoulder onto the chest (skin), ending above the left cup tip
TB = mt.bvh_union([mt.world_copy(PARTS['torso'], '_tmp_t', level=1)])
bpy.data.objects.remove(bpy.data.objects['_tmp_t'])
s = -1
back_part = mt.project(TB, mt.catmull([(s * 0.36, 3.4), (s * 0.38, 3.52), (s * 0.36, 3.6)], 20), 'back')
top_part = mt.project(TB, mt.catmull([(s * 0.36, -0.15), (s * 0.35, 0.0), (s * 0.34, 0.1)], 16), 'top')
front_part = mt.project(TB, mt.catmull([(s * 0.33, 3.6), (s * 0.3, 3.53), (s * 0.22, 3.5), (s * 0.15, 3.52),
                                        (s * 0.1, 3.57)], 40), 'front')
chest = [(c + n * 0.016, n) for c, n in back_part + top_part + front_part]
add('torso', mt.vine('IV_ChestVine', [c for c, n in chest], 0.016, M_STEM, taper=(1.0, 0.4)))
for k, i in enumerate(range(6, len(chest) - 3, 12)):
    co, n = chest[i]
    along = chest[i + 1][0] - chest[i - 1][0]
    leaf_on(f'IV_ChestLeaf{k}', co, n, along, 'torso', length=0.15, width=0.1,
            kind='ivy' if k % 2 == 0 else 'pointed', side=1 if k % 2 else -1, out_angle=60)
end_co, end_n = chest[-1]
add('torso', mt.tendril('IV_ChestTendril', end_co, (chest[-1][0] - chest[-3][0]).normalized(), end_n, M_STEM,
                        length=0.08, radius=0.0045))
# a second, smaller branch dropping towards the left cup tip
branch = mt.project(TB, mt.catmull([(s * 0.25, 3.5), (s * 0.24, 3.45), (s * 0.22, 3.43)], 14), 'front')
add('torso', mt.vine('IV_ChestBranch', [c + n * 0.011 for c, n in branch], 0.008, M_STEM, taper=(1.0, 0.4)))
co, n = branch[-1]
leaf_on('IV_ChestBranchLeaf', co, n, branch[-1][0] - branch[-3][0], 'torso', length=0.08, width=0.05, side=1)

# =========================================================== 8. finishing
for ob in [bod] + [o for side in GLOVE for o in GLOVE[side][:3]]:
    mt.add_solidify(ob, 0.008)
    mt.add_subsurf(ob, 2 if ob is bod else 1)
for group, obs in GROUPS.items():
    for ob in obs:
        if ob.name in bpy.data.objects and ob.parent is None:
            mt.parent_to_part(ob, PARTS[group])
mt.qa_report({}, ground_z=0.0)

mt.add_studio_look()
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'attach_to_rig.py'), 'w') as f:
    f.write(mt.ATTACH_SCRIPT.format(coll=mt.COLL.name))
mt.save_deliverables(OUT, 'PoisonIvy_Morph')
print('SAVED')
