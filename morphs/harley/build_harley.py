"""Harley Quinn (Suicide Squad) morph for the Starter 2.0 Rig, built with
morph_toolkit.

    python build_harley.py <rig.blend> <out_dir>

Current pass, TOP: fitted distressed raglan tee with print and garment
construction (raglan/side seams, rib collar, double-needle hems), shoulder
holster harness, PUDDIN choker, forearm tattoo, wristband, spiked bracelet,
fingerless glove. The lower body (shorts, belt, fishnets, sneakers) is drafted
in lower_v1_draft.py and gets reworked in the next pass.
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'toolkit'))
import bpy, bmesh
from mathutils import Vector
import morph_toolkit as mt

RIG, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=RIG)
random.seed(11)

PARTS = {
    'torso': 'Robloxian2014', 'hips': 'Robloxian2013',
    'upperarm_R': 'Robloxian2012', 'lowerarm_R': 'Robloxian2011', 'hand_R': 'Robloxian2010',
    'upperarm_L': 'Robloxian209', 'lowerarm_L': 'Robloxian208', 'hand_L': 'Robloxian207',
    'upperleg_R': 'Robloxian201', 'lowerleg_R': 'Robloxian202', 'foot_R': 'Robloxian203',
    'upperleg_L': 'Robloxian204', 'lowerleg_L': 'Robloxian205', 'foot_L': 'Robloxian206',
}
mt.set_front(mt.detect_front(bpy.data.objects[PARTS['foot_R']]))
F, RT, UP = mt.FRONT, mt.RIGHT, mt.UP
mt.new_collection('Harley Quinn Morph')
GROUPS = {k: [] for k in PARTS}
SIDES = (('R', 1), ('L', -1))       # character's right = +RIGHT


def add(group, *obs):
    for o in obs:
        if isinstance(o, (list, tuple)):
            GROUPS[group].extend(o)
        elif o is not None:
            GROUPS[group].append(o)


def side_dir(a_deg):
    a = math.radians(a_deg)
    return RT * math.cos(a) + F * math.sin(a)


# ------------------------------------------------------------------ materials
def fabric(name, col, rough=0.75, bump=(180, 0.06)):
    return mt.principled(name, col, rough, bump=bump)


def sequin(name, col):
    m = mt.principled(name, col, 0.26, metal=0.75, coat=0.3, coat_rough=0.1)
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 220
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6
    bp.inputs['Distance'].default_value = 0.002
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    nt.links.new(vo.outputs['Distance'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], p.inputs['Normal'])
    return m


M_SHIRT = fabric('HQ_Shirt_White', (0.80, 0.79, 0.76))
M_SHIRT_RED = fabric('HQ_Shirt_Red', (0.55, 0.015, 0.025))
M_SHIRT_BLUE = fabric('HQ_Shirt_Blue', (0.02, 0.10, 0.55))
M_RIB_RED = fabric('HQ_Rib_Red', (0.5, 0.012, 0.02), bump=(90, 0.25))
M_PRINT_BLK = mt.principled('HQ_Print_Black', (0.012, 0.012, 0.012), 0.55)
M_PRINT_RED = mt.principled('HQ_Print_Red', (0.6, 0.01, 0.02), 0.55)
M_SEQ_RED = sequin('HQ_Sequin_Red', (0.65, 0.02, 0.04))
M_SEQ_BLUE = sequin('HQ_Sequin_Blue', (0.03, 0.09, 0.62))
M_LEATHER = mt.principled('HQ_Leather_Black', (0.013, 0.013, 0.014), 0.4, coat=0.25, coat_rough=0.25,
                          bump=(260, 0.08))
M_GOLD = mt.principled('HQ_Gold', (0.86, 0.6, 0.24), 0.24, metal=1.0)
M_SILVER = mt.principled('HQ_Silver', (0.8, 0.8, 0.82), 0.22, metal=1.0)
M_GUN = mt.principled('HQ_Gunmetal', (0.12, 0.12, 0.13), 0.35, metal=1.0)
M_NET = mt.principled('HQ_Fishnet', (0.01, 0.01, 0.01), 0.5)
M_INK_BLK = mt.principled('HQ_Tattoo_Black', (0.02, 0.02, 0.025), 0.6)
M_INK_RED = mt.principled('HQ_Tattoo_Red', (0.45, 0.02, 0.03), 0.6)
M_CHOKER = mt.principled('HQ_Choker_Red', (0.45, 0.01, 0.02), 0.35, coat=0.35, coat_rough=0.15)
M_GLOVE_RED = mt.principled('HQ_Glove_Red', (0.42, 0.012, 0.02), 0.5, coat=0.1, coat_rough=0.4, bump=(260, 0.06))
M_PURPLE = mt.principled('HQ_Purple', (0.2, 0.03, 0.35), 0.45, coat=0.2)
M_SNK_BLK = mt.principled('HQ_Sneaker_Black', (0.014, 0.014, 0.016), 0.35, coat=0.35, coat_rough=0.2,
                          bump=(300, 0.05))
M_SNK_WHT = mt.principled('HQ_Sneaker_White', (0.82, 0.82, 0.82), 0.42, coat=0.25, coat_rough=0.2)
M_SOLE = mt.principled('HQ_Sole_White', (0.85, 0.85, 0.84), 0.6)
M_SOLE_GREY = mt.principled('HQ_Sole_Grey', (0.25, 0.25, 0.27), 0.5, metal=0.4)
M_LACE = fabric('HQ_Lace', (0.88, 0.88, 0.86), 0.7, bump=(400, 0.1))
M_THREAD = fabric('HQ_Thread', (0.78, 0.76, 0.72), 0.85, bump=None)
M_STITCH = mt.principled('HQ_Stitch', (0.55, 0.55, 0.55), 0.6)
M_STITCH_D = mt.principled('HQ_Stitch_Dark', (0.06, 0.06, 0.065), 0.6)

FONT_SCRIPT = bpy.data.fonts.load(os.path.join(HERE, 'fonts', 'Lobster-Regular.ttf'))
bold_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_BLOCK = bpy.data.fonts.load(bold_path) if os.path.exists(bold_path) else FONT_SCRIPT


# ------------------------------------------------------------------ local helpers
def ring_multi(name, bvhs, center, z, h, lift, thick, mat, nseg=64, z_fn=None):
    """Band around whatever surface is outermost (several shells overlap)."""
    bm = bmesh.new(); rows = []
    for i in range(nseg):
        a = 360.0 * i / nseg
        r = side_dir(a); zz = z_fn(a) if z_fn else z
        row = []
        for dz in (-h / 2, h / 2):
            hit = mt.outer_hit(bvhs, Vector((center[0], center[1], zz + dz)) + r * 5, -r)
            row.append(bm.verts.new(hit[0] + hit[1] * lift))
        rows.append(row)
    for i in range(nseg):
        r0, r1 = rows[i], rows[(i + 1) % nseg]
        bm.faces.new((r0[0], r1[0], r1[1], r0[1]))
    ob = mt.mesh_obj(name, bm, mat); mt.add_solidify(ob, thick, offset=1.0); mt.smooth(ob)
    return ob


def ring_points(bvhs, center, z, lift, nseg=72, z_fn=None):
    pts = []
    for i in range(nseg + 1):
        a = 360.0 * i / nseg
        r = side_dir(a); zz = z_fn(a) if z_fn else z
        hit = mt.outer_hit(bvhs, Vector((center[0], center[1], zz)) + r * 5, -r)
        if hit is not None:
            pts.append(hit[0] + hit[1] * lift)
    return pts


def angle_of(co, center):
    d = co - Vector((center[0], center[1], co.z))
    return math.degrees(math.atan2(d.dot(F), d.dot(RT))) % 360


def cut_by_curve(ob, center, z_fn, keep_above=True):
    """Delete faces on one side of a curve z_fn(angle) and snap the new edge
    onto the exact curve (clean openings for necklines, hems, sleeves)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    dead = []
    for f in bm.faces:
        c = f.calc_center_median()
        zc = z_fn(angle_of(c, center))
        if (c.z < zc) if keep_above else (c.z > zc):
            dead.append(f)
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    for v in bm.verts:
        if v.is_boundary:
            zc = z_fn(angle_of(v.co, center))
            if abs(v.co.z - zc) < 0.06:
                v.co.z = zc
    bm.to_mesh(ob.data); bm.free()


def text_mesh(body, font, size, offset=0.0, align='CENTER', rot_deg=0.0):
    cu = bpy.data.curves.new('tmp_txt', 'FONT')
    cu.body = body; cu.font = font; cu.size = size; cu.offset = offset
    cu.align_x = align; cu.align_y = 'CENTER'; cu.resolution_u = 6
    ob = bpy.data.objects.new('tmp_txt', cu); mt.COLL.objects.link(ob)
    ob.rotation_euler = (0, 0, math.radians(rot_deg))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    return me


def decal_from_mesh(name, me, bvh, s0, z0, lift, thick, mat, mode='front', center=(0, 0), ang0=90,
                    radius=0.2):
    """Wrap a flat 2D mesh (x right, y up) onto a surface: 'front' maps x->RIGHT,
    'cyl' maps x->arc length around `center` starting at angle ang0."""
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    for _ in range(2):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        # seen from the front, the viewer's right is the character's LEFT (-RIGHT),
        # so text x maps to -s / increasing angle or it comes out mirrored
        if mode == 'front':
            p = mt.project(bvh, [(s0 - x, z0 + y)], 'front')
        else:
            p = mt.project(bvh, [(ang0 + math.degrees(x / radius), z0 + y)], 'cyl', center)
        if p:
            v.co = p[0][0] + p[0][1] * lift
    ob = mt.mesh_obj(name, bm, mat)
    mt.add_solidify(ob, thick, offset=1.0); mt.smooth(ob)
    bpy.data.meshes.remove(me)
    return ob


def patch(name, bvh, corners2d, lift, thick, mat, mode='cyl', center=(0, 0), subdiv=3):
    """Polygon (tattoo diamond, panel, label) built in the projection's 2D
    space, subdivided, then EVERY vertex projected so it hugs curved surfaces."""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((u, v, 0))) for u, v in corners2d]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for _ in range(subdiv):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts:
        p = mt.project(bvh, [(v.co.x, v.co.y)], mode, center)
        if not p:
            bm.free(); return None
        v.co = p[0][0] + p[0][1] * lift
    ob = mt.mesh_obj(name, bm, mat); mt.add_solidify(ob, thick, offset=1.0); mt.smooth(ob)
    return ob


def diamond2d(cx, cz, w, h):
    return [(cx, cz - h / 2), (cx + w / 2, cz), (cx, cz + h / 2), (cx - w / 2, cz)]


def raw_bvh(part, off=0.0, level=1):
    tmp = mt.world_copy(PARTS[part], '_tmp', level=level)
    if off: mt.offset_shell(tmp, off)
    b = mt.bvh_of(tmp); c = tmp
    return b, c

# =========================================================== 1. FITTED T-SHIRT
BUILD_LOWER = False      # lower body (shorts, belt, fishnets, sneakers) is a separate pass
TEE_OFF = 0.014
shirt = mt.world_copy(PARTS['torso'], 'HQ_Shirt_Torso', level=2)
mt.offset_shell(shirt, TEE_OFF)


def fs(co):                                   # (s along RIGHT, f along FRONT)
    return co.dot(RT), co.dot(F)


def bridge_fabric(ob):
    """A fitted tee is snug but it is still fabric: it spans the cleavage and
    the crease under the bust instead of following them like body paint."""
    me = ob.data
    vs = [v for v in me.vertices if v.co.dot(F) > 0.05 and 2.7 < v.co.z < 3.45]
    # (1) under-bust: per vertical column, straight line from bust apex down
    cols = {}
    for v in vs:
        s, f = fs(v.co)
        if abs(s) > 0.36: continue
        cols.setdefault(int(round(s / 0.02)), []).append(v)
    for k, cv in cols.items():
        apex = max((v for v in cv if 3.0 < v.co.z < 3.35), key=lambda v: v.co.dot(F), default=None)
        if apex is None: continue
        za, fa = apex.co.z, apex.co.dot(F)
        zl = za - 0.33
        low = [v for v in cv if abs(v.co.z - zl) < 0.02]
        if not low: continue
        fl = max(v.co.dot(F) for v in low)
        for v in cv:
            if zl < v.co.z < za:
                t = (v.co.z - zl) / (za - zl)
                target = fl + (fa - fl) * t ** 1.6 - 0.004 * math.sin(math.pi * t)
                f = v.co.dot(F)
                if target > f:
                    v.co += F * (target - f)
    # (2) cleavage: per height, straight span between the two bust peaks
    rows = {}
    for v in vs:
        s, f = fs(v.co)
        if abs(s) < 0.2 and 2.95 < v.co.z < 3.36:
            rows.setdefault(int(round(v.co.z / 0.01)), []).append(v)
    for k, rv in rows.items():
        L = [v for v in rv if -0.2 < fs(v.co)[0] < -0.1]; Rr = [v for v in rv if 0.1 < fs(v.co)[0] < 0.2]
        if not L or not Rr: continue
        pl = max(L, key=lambda v: v.co.dot(F)); pr = max(Rr, key=lambda v: v.co.dot(F))
        sl, fl = fs(pl.co); sr, fr = fs(pr.co)
        z = k * 0.01
        fade = min(1.0, (3.36 - z) / 0.08)
        for v in rv:
            s, f = fs(v.co)
            if sl < s < sr:
                t = (s - sl) / (sr - sl)
                target = fl + (fr - fl) * t - 0.006 * math.sin(math.pi * t)
                if target > f:
                    v.co += F * (target - f) * fade


bridge_fabric(shirt)
mt.smooth_region(shirt, lambda c: 0.5 if (c.dot(F) > 0.05 and 2.7 < c.z < 3.4 and abs(c.dot(RT)) < 0.38) else 0.0, 6)


def navel_w(c):
    if c.dot(F) < 0.1 or c.z < 2.3 or c.z > 2.6: return 0.0
    d = math.hypot(c.dot(RT) / 0.10, (c.z - 2.435) / 0.09)
    return min(1.0, max(0.0, 1.3 * (1.0 - d)))


mt.smooth_region(shirt, navel_w, 160)
for s_ in (-1, 1):
    mt.add_folds(shirt, RT * (s_ * 0.37) + Vector((0, 0, 2.66)), (0.14, 0.32, 0.16), (0, 0, 1), 0.004, 0.05,
                 face_dir=tuple(RT * s_), min_dot=0.35)
# soft tension folds pulling from the bust towards the sides
for s_ in (-1, 1):
    mt.add_folds(shirt, RT * (s_ * 0.3) + F * 0.25 + Vector((0, 0, 2.95)), (0.14, 0.2, 0.12),
                 tuple((RT * s_ * 0.6 + UP).normalized()), 0.0035, 0.055, face_dir=tuple(F), min_dot=0.1)

neck_c = (0.0, -0.045)
neck_z = lambda a: 3.648 - 0.04 * max(0.0, math.sin(math.radians(a))) ** 2
HEM = 2.39
hem_z = lambda a: HEM
cut_by_curve(shirt, neck_c, neck_z, keep_above=False)
cut_by_curve(shirt, (0, 0), hem_z, keep_above=True)

# raglan: red shoulder panels outside the diagonal seam (neck -> underarm)
RAG = []
bm = bmesh.new(); bm.from_mesh(shirt.data)
for s in (-1, 1):
    A = RT * (s * 0.205) + Vector((0, 0, 3.64)); B = RT * (s * 0.5) + Vector((0, 0, 3.3))
    n = (B - A).cross(F).normalized()
    if n.dot(RT) * s < 0: n = -n
    RAG.append((A, n))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=A, plane_no=n)
bm.to_mesh(shirt.data); bm.free()
shirt.data.materials.append(M_SHIRT); shirt.data.materials.append(M_SHIRT_RED)
for p in shirt.data.polygons:
    c = p.center
    if c.z > 3.2 and any((c - A).dot(n) > 0 for A, n in RAG):
        p.material_index = 1
mt.smooth(shirt)

# --- horizontal tears with rolled frayed edges and hanging threads
TEARS = [('front', 0.25, 3.2, 0.075, 0.03, 8), ('front', -0.15, 2.66, 0.1, 0.038, -6),
         ('front', 0.13, 2.52, 0.07, 0.027, 4), ('front', -0.3, 3.0, 0.06, 0.026, -10),
         ('back', 0.16, 3.0, 0.09, 0.034, 6), ('back', -0.2, 2.62, 0.07, 0.028, -5)]
TPH = [(random.uniform(0, 6), random.uniform(0, 6), random.uniform(0, 6)) for _ in TEARS]


def tear_local(c, tr):
    side, s0, z0, rx, rz, tilt = tr
    facing = c.dot(F)
    if (side == 'front' and facing <= 0.05) or (side == 'back' and facing >= -0.05): return None
    s = c.dot(RT) if side == 'front' else -c.dot(RT)
    s0_ = s0 if side == 'front' else -s0
    a = math.radians(tilt)
    dx, dz = s - s0_, c.z - z0
    return (dx * math.cos(a) + dz * math.sin(a)) / rx, (-dx * math.sin(a) + dz * math.cos(a)) / rz


def tear_r(phi, ph):
    return 1 + 0.16 * math.sin(4 * phi + ph[0]) + 0.1 * math.sin(7 * phi + ph[1]) + 0.06 * math.sin(13 * phi + ph[2])


def in_tear(c):
    for tr, ph in zip(TEARS, TPH):
        l = tear_local(c, tr)
        if l is None: continue
        if math.hypot(*l) < tear_r(math.atan2(l[1], l[0]), ph): return True
    return False


def snap_to_tear(v):
    """Move a boundary vertex onto its tear's smooth outline (no grid stair-steps)."""
    for tr, ph in zip(TEARS, TPH):
        l = tear_local(v.co, tr)
        if l is None or math.hypot(*l) > 1.8: continue
        side, s0, z0, rx, rz, tilt = tr
        phi = math.atan2(l[1], l[0]); r_t = tear_r(phi, ph)
        lx, lz = math.cos(phi) * r_t * rx, math.sin(phi) * r_t * rz
        a = math.radians(tilt)
        ds = lx * math.cos(a) - lz * math.sin(a); dz = lx * math.sin(a) + lz * math.cos(a)
        sdir = RT if side == 'front' else -RT
        s0_ = s0 if side == 'front' else -s0
        cur_s = v.co.dot(sdir)
        v.co += sdir * ((s0_ + ds) - cur_s) + UP * ((z0 + dz) - v.co.z)
        return True
    return False


bm = bmesh.new(); bm.from_mesh(shirt.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if in_tear(f.calc_center_median())], context='FACES')
for v in bm.verts:
    if v.is_boundary and snap_to_tear(v):
        v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * 0.0012
bm.to_mesh(shirt.data); bm.free()


def boundary_loops(ob, pred):
    """Ordered boundary loops whose vertices satisfy pred(co)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    edges = [e for e in bm.edges if e.is_boundary and pred(e.verts[0].co) and pred(e.verts[1].co)]
    adj = {}
    for e in edges:
        a, b = e.verts
        adj.setdefault(a.index, []).append(b.index); adj.setdefault(b.index, []).append(a.index)
    co = {v.index: v.co.copy() for v in bm.verts}
    nrm = {v.index: v.normal.copy() for v in bm.verts}
    bm.free()
    loops, seen = [], set()
    for start in adj:
        if start in seen: continue
        loop = [start]; seen.add(start); prev = None; cur = start
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            if not nxt: break
            prev, cur = cur, nxt[0]; loop.append(cur); seen.add(cur)
        if len(loop) > 6:
            loops.append([(co[i], nrm[i]) for i in loop])
    return loops


tear_loops = boundary_loops(shirt, lambda c: any(tear_local(c, tr) is not None and math.hypot(*tear_local(c, tr)) < 1.7
                                                  for tr in TEARS))
fray = []
for k, lp in enumerate(tear_loops):
    pts = [c + n * 0.0015 for c, n in lp] + [lp[0][0] + lp[0][1] * 0.0015]
    fray.append(mt.tube(f'HQ_TearRim{k}', pts, 0.0026, M_THREAD, res=2))
    cen = sum((c for c, _ in lp), Vector()) / len(lp)
    for i, (c, n) in enumerate(lp):
        if i % 6: continue
        inward = (cen - c); inward -= n * inward.dot(n)
        if inward.length < 1e-6: continue
        inward.normalize()
        top = c.z > cen.z
        L_ = random.uniform(0.01, 0.022)
        if top:      # threads hang down from the upper lip
            p = [c, c + inward * L_ * 0.4 - UP * L_ * 0.3, c + inward * L_ * 0.55 - UP * L_ * 0.9]
        else:
            p = [c, c + inward * L_ * 0.5 + UP * 0.002, c + inward * L_ * 0.8 - UP * 0.004]
        fray.append(mt.tube(f'HQ_TearThread{k}_{i}', p, 0.0013, M_THREAD, res=1))
    # two sagging threads spanning the tear
    tops = [c for c, _ in lp if c.z > cen.z]; bots = [c for c, _ in lp if c.z <= cen.z]
    for j in range(1):
        if not tops or not bots: break
        a_ = random.choice(tops); b_ = min(bots, key=lambda q: (q - a_).length + random.uniform(0, 0.01))
        mid = (a_ + b_) / 2 - UP * 0.004 + (cen - (a_ + b_) / 2) * 0.0
        fray.append(mt.tube(f'HQ_TearSpan{k}_{j}', [a_, mid, b_], 0.0012, M_THREAD, res=1))
if fray: add('torso', mt.join(fray, 'HQ_Shirt_Fray'))

SB = mt.bvh_of(shirt)
TB, ttmp = raw_bvh('torso'); bpy.data.objects.remove(ttmp)

# --- garment construction: raglan seams, side seams, collar band, hem
TEE_SEAM = (M_SHIRT, M_STITCH)
for s in (-1, 1):
    for mode in ('front', 'back'):
        mt_seam = mt.seam(f'HQ_RaglanSeam_{mode}{s}', [(s * 0.205, 3.618), (s * 0.34, 3.46), (s * 0.495, 3.31)],
                          mode, SB, (M_SHIRT_RED, M_STITCH), n=40, r=0.0034, stitch_gap=0.008, stitch_len=0.009)
        add('torso', mt_seam)
    add('torso', mt.seam(f'HQ_SideSeam{s}', [(0 if s > 0 else 180, z) for z in (3.3, 3.0, 2.7, HEM + 0.01)], 'cyl', SB,
                         TEE_SEAM, n=50, r=0.003, stitch_gap=0.007, stitch_len=0.009))

# rib collar band rising onto the neck + stitch line
COL_H = 0.034
col = ring_multi('HQ_Collar', [SB, TB], neck_c, 0, COL_H, 0.004, 0.008, M_RIB_RED, nseg=96,
                 z_fn=lambda a: neck_z(a) + 0.004)
mt.add_bevel(col, 0.003); add('torso', col)
add('torso', mt.tube('HQ_Collar_Roll', ring_points([SB, TB], neck_c, 0, 0.012, nseg=96,
                                                   z_fn=lambda a: neck_z(a) + 0.004 + COL_H / 2), 0.0055, M_RIB_RED))
add('torso', mt.tube('HQ_Collar_Stitch', ring_points([SB], neck_c, 0, 0.0016, nseg=120,
                                                     z_fn=lambda a: neck_z(a) - 0.012), 0.0011, M_STITCH))

# double-needle hem: rolled fold + two stitch rows
add('torso', mt.tube('HQ_Hem_Roll', ring_points([SB], (0, 0), HEM + 0.005, 0.0015, nseg=120), 0.0065, M_SHIRT))


def stitch_ring(name, bvhs, center, z, lift, mat, nseg=200, dash=0.55):
    """Dashed stitch line round a body at height z."""
    pts = ring_points(bvhs, center, z, lift, nseg=nseg)
    bm = bmesh.new()
    for i in range(0, len(pts) - 1, 2):
        a_, b_ = pts[i], pts[i + 1]
        t = (b_ - a_); L_ = t.length
        if L_ < 1e-6: continue
        t.normalize(); c = a_.lerp(b_, 0.5)
        n = (c - Vector((center[0], center[1], c.z))).normalized()
        b = n.cross(t).normalized()
        mt.box(bm, c, t, b, n, L_ * dash, 0.001, 0.0012)
    return mt.mesh_obj(name, bm, mat)


for k, dz in enumerate((0.02, 0.029)):
    add('torso', stitch_ring(f'HQ_Hem_Stitch{k}', [SB], (0, 0), HEM + dz, 0.0012, M_STITCH))

# --- chest print, scaled to span the chest
def sized_text(body, font, width, rot=4):
    me = text_mesh(body, font, 0.1, rot_deg=rot)
    xs = [v.co.x for v in me.vertices]
    k = width / (max(xs) - min(xs))
    for v in me.vertices: v.co *= k
    return me


for line, width, z0, s0 in (("Daddy's", 0.40, 3.5, -0.015), ("Lil Monster", 0.54, 3.355, 0.0)):
    tag = line.replace("'", '').replace(' ', '')
    add('torso', decal_from_mesh(f'HQ_Print_{tag}_Shadow', sized_text(line, FONT_SCRIPT, width), SB,
                                 s0 - 0.008, z0 - 0.008, 0.0015, 0.0012, M_PRINT_RED))
    add('torso', decal_from_mesh(f'HQ_Print_{tag}', sized_text(line, FONT_SCRIPT, width), SB, s0, z0,
                                 0.003, 0.0014, M_PRINT_BLK))

# --- sleeves: fitted, 3/4 length, red raglan caps, printed stripes, double-needle hems
SLEEVE_END = 2.62
for side, s in SIDES:
    ua = mt.world_copy(PARTS[f'upperarm_{side}'], f'HQ_Sleeve_Upper_{side}', level=2)
    la = mt.world_copy(PARTS[f'lowerarm_{side}'], f'HQ_Sleeve_Lower_{side}', level=2)
    for ob in (ua, la):
        mt.offset_shell(ob, TEE_OFF)
        mt.add_folds(ob, RT * (s * 0.74) + F * 0.12 + Vector((0, 0, 2.79)), (0.26, 0.24, 0.14),
                     tuple(RT * (s * 0.25) + UP), 0.008, 0.06, face_dir=tuple(F), min_dot=0.0)
    c_la = mt.slice_center(la, SLEEVE_END)
    cut_by_curve(la, c_la, lambda a: SLEEVE_END, keep_above=True)
    bm = bmesh.new(); bm.from_mesh(ua.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=Vector((0, 0, 3.3)), plane_no=UP)
    bm.to_mesh(ua.data); bm.free()
    ua.data.materials.append(M_SHIRT); ua.data.materials.append(M_SHIRT_RED)
    for p in ua.data.polygons:
        p.material_index = 1 if p.center.z > 3.3 else 0
    la.data.materials.append(M_SHIRT)
    mt.smooth(ua); mt.smooth(la)
    ub, lb = mt.bvh_of(ua), mt.bvh_of(la)
    cu = mt.slice_center(ua, 3.0)
    # raglan cap seam on the sleeve
    add(f'upperarm_{side}', mt.tube(f'HQ_SleeveCapSeam_{side}', ring_points([ub], mt.slice_center(ua, 3.3), 3.3, 0.0016,
                                                                          nseg=96), 0.0034, M_SHIRT_RED))
    for k, dz in enumerate((-0.009, 0.009)):
        add(f'upperarm_{side}', stitch_ring(f'HQ_SleeveCapStitch{k}_{side}', [ub], mt.slice_center(ua, 3.3),
                                            3.3 + dz, 0.0013, M_STITCH, nseg=150))
    # stripes: thin printed bands hugging the sleeve (clean straight edges)
    stripes = ((3.03, M_SHIRT_RED), (2.94, M_SHIRT_RED)) if s > 0 else ((3.03, M_SHIRT_RED), (2.94, M_SHIRT_BLUE))
    for k, (z, m) in enumerate(stripes):
        bmS = bmesh.new(); rows = []
        NR, NS = 6, 120
        for r_ in range(NR + 1):
            zz = z - 0.021 + 0.042 * r_ / NR
            rows.append([bmS.verts.new(p) for p in ring_points([ub], cu, zz, 0.0012, nseg=NS)[:-1]])
        for r_ in range(NR):
            for i in range(NS):
                bmS.faces.new((rows[r_][i], rows[r_][(i + 1) % NS], rows[r_ + 1][(i + 1) % NS], rows[r_ + 1][i]))
        st = mt.mesh_obj(f'HQ_SleeveStripe{k}_{side}', bmS, m); mt.add_solidify(st, 0.0012, offset=1.0); mt.smooth(st)
        add(f'upperarm_{side}', st)
    # hem: roll + double stitching
    add(f'lowerarm_{side}', mt.tube(f'HQ_SleeveHem_{side}', ring_points([lb], c_la, SLEEVE_END + 0.005, 0.0015,
                                                                       nseg=96), 0.0062, M_SHIRT))
    for k, dz in enumerate((0.019, 0.027)):
        add(f'lowerarm_{side}', stitch_ring(f'HQ_SleeveHemStitch{k}_{side}', [lb], c_la, SLEEVE_END + dz, 0.0012,
                                            M_STITCH, nseg=150))
    # underarm seam
    out_a = 0 if s > 0 else 180
    add(f'upperarm_{side}', mt.seam(f'HQ_SleeveSeam_{side}', [(out_a + 180, 3.25), (out_a + 180, 2.95), (out_a + 180, 2.72)],
                                    'cyl', ub, TEE_SEAM, n=30, center=cu, r=0.003, stitch_gap=0.007, stitch_len=0.009))
    add(f'upperarm_{side}', ua); add(f'lowerarm_{side}', la)

# =========================================================== 2. SHOULDER HOLSTER HARNESS
M_HARNESS_ST = mt.principled('HQ_Harness_Stitch', (0.2, 0.2, 0.21), 0.6)
STRAP_W = 0.046


def strap_ribbon(name, path, group):
    path = mt.resample(path, 0.008)
    ob = mt.ribbon(name, path, STRAP_W, 0.005, 0.008, M_LEATHER)
    mt.add_bevel(ob, 0.0025, 2)
    bm = bmesh.new(); rs = mt.resample(path, 0.02)
    for i in range(1, len(rs) - 1):
        co, n = rs[i]
        t, b, n = mt.frame_at(co, n, (rs[i + 1][0] - rs[i - 1][0]).normalized())
        for sg in (-1, 1):
            mt.box(bm, co + n * 0.0135 + b * sg * (STRAP_W / 2 - 0.007), t, b, n, 0.006, 0.0011, 0.0011)
    add(group, ob, mt.mesh_obj(name + '_Stitch', bm, M_HARNESS_ST))
    return path


back_ring_co, back_ring_n = mt.project(SB, [(0, 3.12)], 'back')[0]
for s in (-1, 1):
    front = mt.project(SB, mt.catmull([(s * 0.475, 3.26), (s * 0.41, 3.44), (s * 0.345, 3.6)], 30), 'front')
    top = mt.project(SB, mt.catmull([(s * 0.345, 0.12), (s * 0.35, -0.05), (s * 0.345, -0.22)], 20), 'top')
    back = mt.project(SB, mt.catmull([(s * 0.345, 3.6), (s * 0.2, 3.33), (s * 0.035, 3.135)], 30), 'back')
    path = strap_ribbon(f'HQ_Harness{s}', front + top + back, 'torso')
    # slide adjuster on the front of the strap
    i = len(front) // 2
    co, n = front[i]
    t, b, n = mt.frame_at(co, n, (front[i + 1][0] - front[i - 1][0]).normalized())
    c = co + n * 0.017
    add('torso', mt.tube(f'HQ_HarnessSlide{s}', mt.rounded_rect(c, b, t, STRAP_W / 2 + 0.007, 0.013, k=0.4, n=40),
                         0.0042, M_SILVER))
    add('torso', mt.tube(f'HQ_HarnessSlideBar{s}', [c - b * (STRAP_W / 2 + 0.007), c + b * (STRAP_W / 2 + 0.007)],
                         0.0032, M_SILVER))
t, b, n = mt.frame_at(back_ring_co, back_ring_n, UP)
rc = back_ring_co + n * 0.017
add('torso', mt.tube('HQ_HarnessRing', [rc + (t * math.cos(a) + b * math.sin(a)) * 0.032
                                        for a in [2 * math.pi * i / 40 for i in range(41)]], 0.0075, M_SILVER))

# holster under her left arm
HA = 183
hd = side_dir(HA)
hit = mt.outer_hit([SB], Vector((0, 0, 2.95)) + hd * 5, -hd)
hn = hd; hu = UP; ht = hu.cross(hn).normalized()
hc = hit[0] + hn * 0.045
outline = []
for i in range(40):
    u = 2 * math.pi * i / 40
    cx, cz = math.cos(u), math.sin(u)
    w = 0.058 + 0.016 * (cz + 1) / 2                       # wider at the top
    outline.append((math.copysign(abs(cx) ** 0.5, cx) * w, math.copysign(abs(cz) ** 0.6, cz) * 0.15))
bm = bmesh.new()
fr = [bm.verts.new(hc + ht * x + hu * z + hn * 0.024) for x, z in outline]
bk = [bm.verts.new(hc + ht * x * 0.92 + hu * z - hn * 0.024) for x, z in outline]
bm.faces.new(fr); bm.faces.new(bk[::-1])
for i in range(40):
    j = (i + 1) % 40; bm.faces.new((bk[i], bk[j], fr[j], fr[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
hol = mt.mesh_obj('HQ_Holster', bm, M_LEATHER); mt.add_bevel(hol, 0.012, 4); mt.smooth(hol)
add('torso', hol)
edge = [hc + ht * x * 0.86 + hu * z * 0.93 + hn * 0.0255 for x, z in outline] 
add('torso', mt.tube('HQ_Holster_Welt', edge + [edge[0]], 0.0035, M_LEATHER))
bm = bmesh.new()
for i, (x, z) in enumerate(outline[::2]):
    p = hc + ht * x * 0.78 + hu * z * 0.86 + hn * 0.0262
    mt.box(bm, p, ht, hu, hn, 0.0035, 0.0035, 0.001)
add('torso', mt.mesh_obj('HQ_Holster_Stitch', bm, M_HARNESS_ST))
# pistol grip + retention strap with snap
gc = hc + hu * 0.19 + ht * 0.012
bm = bmesh.new(); mt.box(bm, gc, (ht + hu * 0.25).normalized(), hu, hn, 0.032, 0.06, 0.019)
grip = mt.mesh_obj('HQ_PistolGrip', bm, M_GUN); mt.add_bevel(grip, 0.012, 3); add('torso', grip)
for sg in (-1, 1):
    bm = bmesh.new(); mt.box(bm, gc + hn * sg * 0.02, (ht + hu * 0.25).normalized(), hu, hn, 0.024, 0.045, 0.002)
    add('torso', mt.mesh_obj(f'HQ_GripPanel{sg}', bm, M_LEATHER))
strap_pts = [(hc + hu * 0.165 + hn * z + ht * 0.0, hn) for z in (-0.03, 0.0, 0.035)]
ret = [hc + hu * 0.16 - hn * 0.03, hc + hu * 0.2 - hn * 0.02, hc + hu * 0.215 + hn * 0.0, hc + hu * 0.2 + hn * 0.026,
       hc + hu * 0.15 + hn * 0.03]
add('torso', mt.tube('HQ_Holster_Retention', ret, 0.008, M_LEATHER))
add('torso', mt.tube('HQ_Holster_Snap', [hc + hu * 0.15 + hn * 0.036, hc + hu * 0.15 + hn * 0.044], 0.009, M_SILVER))
drop = mt.project(SB, mt.catmull([(181, 3.27), (182, 3.17), (183, 3.12)], 12), 'cyl')
strap_ribbon('HQ_HolsterDrop', drop + [(hc + hu * 0.15 + hn * 0.0, hn)], 'torso')

# =========================================================== 3. CHOKER "PUDDIN"
CH_Z = 3.682
choker = ring_multi('HQ_Choker', [TB], neck_c, CH_Z, 0.046, 0.004, 0.01, M_CHOKER, nseg=96)
mt.add_bevel(choker, 0.0035); add('torso', choker)
for k, dz in enumerate((-0.017, 0.017)):
    add('torso', stitch_ring(f'HQ_Choker_Stitch{k}', [TB], neck_c, CH_Z + dz, 0.0145, M_STITCH_D, nseg=140))
tmpc = choker.copy(); tmpc.data = choker.data.copy(); mt.COLL.objects.link(tmpc)
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(tmpc.evaluated_get(dg)); bpy.data.objects.remove(tmpc)
bmc = bmesh.new(); bmc.from_mesh(me); cbv = mt.BVHTree.FromBMesh(bmc); bmc.free(); bpy.data.meshes.remove(me)
add('torso', decal_from_mesh('HQ_Choker_Letters', text_mesh('PUDDIN', FONT_BLOCK, 0.034), cbv, 0, CH_Z, 0.0004,
                             0.0035, M_GOLD, mode='cyl', center=neck_c, ang0=90, radius=0.24))
rc_ = mt.project(cbv, [(90, CH_Z - 0.023)], 'cyl', neck_c)[0][0] + F * 0.005
add('torso', mt.tube('HQ_Choker_Ring', [rc_ - UP * (0.013 - 0.013 * math.cos(a)) + RT * (0.013 * math.sin(a))
                                        for a in [2 * math.pi * i / 28 for i in range(29)]], 0.003, M_GOLD))

# =========================================================== 4. WRISTS + HANDS
for side, s in SIDES:
    fa_tmp = mt.world_copy(PARTS[f'lowerarm_{side}'], '_tmp_fa', level=2)
    hd_tmp = mt.world_copy(PARTS[f'hand_{side}'], '_tmp_hd', level=2)
    c_w = mt.slice_center(fa_tmp, 2.32)
    wrist = mt.join([fa_tmp, hd_tmp], '_tmp_wrist')
    fb = mt.bvh_of(wrist); bpy.data.objects.remove(wrist)
    G = f'lowerarm_{side}'

    def leather_band(name, z, h, mat, lift=0.006, thick=0.016, studs=False):
        band = ring_multi(name, [fb], c_w, z, h, lift, thick, mat, nseg=96)
        mt.add_bevel(band, 0.005, 3); add(G, band)
        for k, dz in enumerate((-h / 2 + 0.008, h / 2 - 0.008)):
            add(G, stitch_ring(f'{name}_Stitch{k}', [fb], c_w, z + dz, lift + thick + 0.0004, M_STITCH_D, nseg=150))
        return band

    if s > 0:
        k = 0
        for row in range(4):
            for col in range(4):
                ang = 30 + col * 17 + (8.5 if row % 2 else 0)
                z = 2.39 + row * 0.042
                if z > SLEEVE_END - 0.03: continue
                m = M_INK_RED if (row + col) % 2 else M_INK_BLK
                add(G, patch(f'HQ_Tattoo_Arm{k}', fb, diamond2d(ang, z, 15, 0.075), 0.0015, 0.0008, m, 'cyl', c_w)); k += 1
        leather_band(f'HQ_Wristband_{side}', 2.3, 0.085, M_PURPLE)
        for j, a in enumerate((60, 95)):
            d = side_dir(a); hit = fb.ray_cast(Vector((c_w[0], c_w[1], 2.3)) + d * 5, -d)
            p = hit[0] + hit[1] * 0.0235
            sn = bmesh.new(); bmesh.ops.create_uvsphere(sn, u_segments=16, v_segments=8, radius=0.011)
            for v in sn.verts: v.co = p + hit[1] * (v.co.dot(Vector((0, 0, 1))) * 0.4) + (v.co - Vector((0, 0, v.co.z)))
            ob = mt.mesh_obj(f'HQ_Wristband_Snap{j}_{side}', sn, M_SILVER); mt.smooth(ob); add(G, ob)
    else:
        leather_band(f'HQ_Bracelet_{side}', 2.335, 0.06, M_LEATHER)
        for i in range(12):
            d = side_dir(30 * i); hit = fb.ray_cast(Vector((c_w[0], c_w[1], 2.335)) + d * 5, -d)
            add(G, mt.claw(f'HQ_Spike_{side}{i}', hit[0] + hit[1] * 0.02, hit[1], UP, M_GOLD, length=0.05,
                           radius=0.014, hook=0.0))
        leather_band(f'HQ_Band_{side}', 2.255, 0.036, M_PURPLE, thick=0.012)
        # fingerless glove: black leather, raised red back panel with piping
        gl = mt.world_copy(PARTS[f'hand_{side}'], f'HQ_Glove_{side}', level=2)
        mt.offset_shell(gl, 0.011)
        bm = bmesh.new(); bm.from_mesh(gl.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((0, 0, 1.915)), plane_no=UP)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z < 1.915], context='FACES')
        bm.to_mesh(gl.data); bm.free()
        gl.data.materials.append(M_LEATHER); mt.smooth(gl)
        add(f'hand_{side}', gl)
        gb = mt.bvh_of(gl); gc = mt.slice_center(gl, 2.02)
        add(f'hand_{side}', mt.tube(f'HQ_Glove_Edge_{side}', ring_points([gb], gc, 1.922, 0.003, nseg=96), 0.0085, M_LEATHER))
        mode = 'right' if s > 0 else 'left'
        panel2d = [(p.x, p.y) for p in mt.rounded_rect(Vector((-0.045, 2.03, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)),
                                                       0.17, 0.085, k=0.45, n=48)[:-1]]
        pts = mt.project(gb, [(p[0], p[1]) for p in panel2d], mode)
        if len(pts) == len(panel2d):
            pnl = patch(f'HQ_Glove_Panel_{side}', gb, [(p[0], p[1]) for p in panel2d], 0.002, 0.004, M_GLOVE_RED, mode)
            add(f'hand_{side}', pnl)
            rim = [c + n * 0.006 for c, n in pts] + [pts[0][0] + pts[0][1] * 0.006]
            add(f'hand_{side}', mt.tube(f'HQ_Glove_PanelPiping_{side}', rim, 0.0035, M_LEATHER))
        # wrist strap across the back of the hand with a snap
        strap2d = [(p.x, p.y) for p in mt.rounded_rect(Vector((-0.04, 2.155, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)),
                                                       0.19, 0.022, k=0.5, n=40)[:-1]]
        add(f'hand_{side}', patch(f'HQ_Glove_Strap_{side}', gb, strap2d, 0.004, 0.006, M_LEATHER, mode))
        sp = mt.project(gb, [(0.1, 2.155)], mode)
        if sp:
            c_, n_ = sp[0]
            add(f'hand_{side}', mt.tube(f'HQ_Glove_Snap_{side}', [c_ + n_ * 0.01, c_ + n_ * 0.016], 0.011, M_SILVER))

# =========================================================== 8. finishing (top)
for ob in [shirt] + [o for o in mt.COLL.objects if o.name.startswith(('HQ_Sleeve_Upper', 'HQ_Sleeve_Lower', 'HQ_Glove_L', 'HQ_Glove_R'))
                     and o.type == 'MESH' and not o.modifiers]:
    mt.add_solidify(ob, 0.007)
    mt.add_subsurf(ob, 1)
add('torso', shirt)
for group, obs in GROUPS.items():
    for ob in obs:
        if ob.name in bpy.data.objects and ob.parent is None:
            mt.parent_to_part(ob, PARTS[group])
stray = [o.name for o in mt.COLL.objects if o.parent is None]
print('unparented:', stray)

mt.add_studio_look()
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'attach_to_rig.py'), 'w') as f:
    f.write(mt.ATTACH_SCRIPT.format(coll=mt.COLL.name))
mt.save_deliverables(OUT, 'HarleyQuinn_Morph')
print('SAVED')
