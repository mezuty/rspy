"""Harley Quinn (Suicide Squad) morph for the Starter 2.0 Rig, built with
morph_toolkit.

    python build_harley.py <rig.blend> <out_dir>

Pieces: distressed raglan tee with print, shoulder holster, PUDDIN choker,
sequin hot pants, studded belt with diamond buckle, fishnet tights, thigh and
forearm tattoos, wristbands, spiked bracelet, fingerless glove, high-top
sneakers with laces.
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


def patch(name, bvh, corners2d, lift, thick, mat, mode='cyl', center=(0, 0)):
    """Small flat polygon (tattoo diamond, label) wrapped onto a surface."""
    pts = mt.project(bvh, corners2d, mode, center)
    if len(pts) < len(corners2d): return None
    bm = bmesh.new()
    vs = [bm.verts.new(co + n * lift) for co, n in pts]
    bm.faces.new(vs)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    ob = mt.mesh_obj(name, bm, mat); mt.add_solidify(ob, thick, offset=1.0); mt.smooth(ob)
    return ob


def diamond2d(cx, cz, w, h):
    return [(cx, cz - h / 2), (cx + w / 2, cz), (cx, cz + h / 2), (cx - w / 2, cz)]


def raw_bvh(part, off=0.0, level=1):
    tmp = mt.world_copy(PARTS[part], '_tmp', level=level)
    if off: mt.offset_shell(tmp, off)
    b = mt.bvh_of(tmp); c = tmp
    return b, c


# =========================================================== 1. T-SHIRT
shirt = mt.world_copy(PARTS['torso'], 'HQ_Shirt_Torso', level=2)
mt.offset_shell(shirt, 0.02)


def loosen_tee(ob):
    """Make the tee hang from the bust instead of hugging the waist."""
    me = ob.data
    nb = 90
    def ang(v): return int(((math.degrees(math.atan2(v.dot(F), v.dot(RT))) % 360) / 360) * nb) % nb
    rb = [0.0] * nb; rh = [0.0] * nb
    for v in me.vertices:
        r = math.hypot(v.co.dot(F), v.co.dot(RT)); k = ang(v.co)
        if 2.98 < v.co.z < 3.32: rb[k] = max(rb[k], r)
        if 2.33 < v.co.z < 2.45: rh[k] = max(rh[k], r)
    def wmax(a, w):
        return [max(a[(i + j) % nb] for j in range(-w, w + 1)) for i in range(nb)]
    rb = wmax(rb, 6); rh = wmax(rh, 3)
    for v in me.vertices:
        z = v.co.z
        if z < 2.3 or z > 3.32: continue
        k = ang(v.co)
        hv = Vector((v.co.dot(RT), v.co.dot(F)))
        r = hv.length
        if r < 1e-6: continue
        if z >= 3.12:
            b = (3.32 - z) / 0.2
            target = r + (rb[k] * 0.975 - r) * b
        else:
            t = min(1.0, (3.12 - z) / (3.12 - 2.38))
            target = rb[k] * 0.975 * (1 - t) + max(rh[k], rb[k] * 0.86) * t
        target = min(target, r + 0.075)
        if target > r:
            s = target / r
            nx, ny = hv.x * s, hv.y * s
            v.co = RT * nx + F * ny + Vector((0, 0, z))
loosen_tee(shirt)
mt.smooth_region(shirt, lambda c: 0.6 if 2.32 < c.z < 3.3 else 0.0, 12)

# neckline (crew, dips at the front) and hem
neck_c = (0.0, -0.045)
neck_z = lambda a: 3.648 - 0.04 * max(0.0, math.sin(math.radians(a))) ** 2
hem_z = lambda a: 2.385 + 0.006 * math.sin(math.radians(a) * 5)
cut_by_curve(shirt, neck_c, neck_z, keep_above=False)
cut_by_curve(shirt, (0, 0), hem_z, keep_above=True)

# raglan: red shoulder panels outside a diagonal seam from neck to armpit
bm = bmesh.new(); bm.from_mesh(shirt.data)
RAG = []
for s in (-1, 1):
    A = RT * (s * 0.215) + Vector((0, 0, 3.64)); B = RT * (s * 0.5) + Vector((0, 0, 3.3))
    n = (B - A).cross(F).normalized()
    if n.dot(RT) * s < 0: n = -n
    RAG.append((A, n))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=A, plane_no=n)
bm.to_mesh(shirt.data); bm.free()
shirt.data.materials.append(M_SHIRT); shirt.data.materials.append(M_SHIRT_RED)
for p in shirt.data.polygons:
    c = p.center
    if c.z > 3.2 and any((c - A).dot(n) > 0 for A, n in RAG):
        p.material_index = 1
mt.smooth(shirt)

# soft drape folds below the bust, front and back
mt.add_folds(shirt, F * 0.3 + Vector((0, 0, 2.72)), (0.42, 0.3, 0.32), tuple(RT), 0.007, 0.09,
             face_dir=tuple(F), min_dot=0.25)
mt.add_folds(shirt, -F * 0.3 + Vector((0, 0, 2.75)), (0.42, 0.3, 0.3), tuple(RT), 0.005, 0.1,
             face_dir=tuple(-F), min_dot=0.25)

# distressed holes (front s,z / back / side) + frayed threads
HOLES = [('front', 0.26, 3.2, 0.045), ('front', -0.14, 2.64, 0.066), ('front', 0.1, 2.5, 0.04),
         ('front', -0.3, 3.0, 0.038), ('back', 0.14, 3.0, 0.054), ('back', -0.2, 2.6, 0.04)]
PH = [(random.uniform(0, 6), random.uniform(0, 6), random.uniform(0, 6)) for _ in HOLES]


def hole_r(phi, R, ph):
    return R * (1 + 0.28 * math.sin(3 * phi + ph[0]) + 0.14 * math.sin(5 * phi + ph[1])
                + 0.07 * math.sin(9 * phi + ph[2]))


def in_hole(c):
    for (side, s0, z0, R), ph in zip(HOLES, PH):
        facing = c.dot(F)
        if (side == 'front' and facing <= 0.05) or (side == 'back' and facing >= -0.05): continue
        s = c.dot(RT); d = Vector((s - s0, c.z - z0))
        if d.length < hole_r(math.atan2(d.y, d.x), R, ph):
            return True
    return False


bm = bmesh.new(); bm.from_mesh(shirt.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if in_hole(f.calc_center_median())], context='FACES')
thread_pts = []
for v in bm.verts:
    if not v.is_boundary: continue
    c = v.co
    for (side, s0, z0, R), ph in zip(HOLES, PH):
        if (side == 'front') != (c.dot(F) > 0): continue
        d = Vector((c.dot(RT) - s0, c.z - z0))
        if d.length < R * 1.7:
            # ragged edge + loose threads pointing into the hole
            jit = random.uniform(-0.004, 0.004)
            v.co += (RT * d.x + UP * d.y).normalized() * jit
            if random.random() < 0.3:
                inward = -(RT * d.x + UP * d.y).normalized()
                L = random.uniform(0.008, 0.02)
                curl = UP * random.uniform(-0.006, 0.006)
                thread_pts.append([v.co.copy(), v.co + inward * L * 0.5 + curl * 0.5, v.co + inward * L + curl])
            break
bm.to_mesh(shirt.data); bm.free()
threads = [mt.tube(f'HQ_Thread{i}', pts, 0.0015, M_THREAD, res=1) for i, pts in enumerate(thread_pts)]
if threads: add('torso', mt.join(threads, 'HQ_Shirt_Threads'))

SB = mt.bvh_of(shirt)

# neckband + hem binding
add('torso', mt.tube('HQ_Neckband', ring_points([SB], neck_c, 0, 0.004, z_fn=lambda a: neck_z(a) - 0.008),
                     0.014, M_RIB_RED))
add('torso', mt.tube('HQ_Hem', ring_points([SB], (0, 0), 0, 0.002, z_fn=lambda a: hem_z(a) + 0.006),
                     0.008, M_SHIRT))

# chest print: "Daddy's / Lil Monster" (black fill, red outline)
for line, size, z0, s0, rot in (("Daddy's", 0.15, 3.5, -0.02, 4), ("Lil Monster", 0.128, 3.355, 0.0, 4)):
    tag = line.replace("'", '').replace(' ', '')
    # red drop shadow (curve offsets spike at sharp glyph corners)
    add('torso', decal_from_mesh(f'HQ_Print_{tag}_Shadow', text_mesh(line, FONT_SCRIPT, size, rot_deg=rot), SB,
                                 s0 - 0.007, z0 - 0.007, 0.0018, 0.0012, M_PRINT_RED))
    add('torso', decal_from_mesh(f'HQ_Print_{tag}', text_mesh(line, FONT_SCRIPT, size, rot_deg=rot), SB, s0, z0,
                                 0.0032, 0.0012, M_PRINT_BLK))

# ---------------------------------------------------- sleeves (3/4 length, raglan red caps, stripes)
SLEEVE_END = 2.62
SLV = {}
for side, s in SIDES:
    ua = mt.world_copy(PARTS[f'upperarm_{side}'], f'HQ_Sleeve_Upper_{side}', level=2)
    la = mt.world_copy(PARTS[f'lowerarm_{side}'], f'HQ_Sleeve_Lower_{side}', level=2)
    for ob in (ua, la):
        mt.offset_shell(ob, 0.02)
        mt.add_folds(ob, RT * (s * 0.74) + F * 0.12 + Vector((0, 0, 2.79)), (0.26, 0.24, 0.14),
                     tuple(RT * (s * 0.25) + UP), 0.01, 0.06, face_dir=tuple(F), min_dot=0.0)
    c_la = mt.slice_center(la, SLEEVE_END)
    cut_by_curve(la, c_la, lambda a: SLEEVE_END, keep_above=True)
    # above the elbow joint (the rig's upper arm overlaps the forearm there)
    stripes = ((3.03, 1), (2.94, 1)) if s > 0 else ((3.03, 1), (2.94, 2))   # 1 red, 2 blue
    for ob in (ua, la):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        for z, _ in stripes:
            for dz in (-0.021, 0.021):
                bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                       plane_co=Vector((0, 0, z + dz)), plane_no=UP)
        bm.to_mesh(ob.data); bm.free()
    # red raglan cap on the top of the sleeve
    bm = bmesh.new(); bm.from_mesh(ua.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                           plane_co=Vector((0, 0, 3.3)), plane_no=UP)
    bm.to_mesh(ua.data); bm.free()
    for ob in (ua, la):
        for m in (M_SHIRT, M_SHIRT_RED, M_SHIRT_BLUE):
            ob.data.materials.append(m)
        for p in ob.data.polygons:
            z = p.center.z
            p.material_index = 1 if z > 3.3 else 0
            for zs, mi in stripes:
                if abs(z - zs) < 0.021:
                    p.material_index = mi
    mt.smooth(ua); mt.smooth(la)
    SLV[side] = (ua, la)
    lb = mt.bvh_of(la)
    cuff_m = M_SHIRT_RED if s > 0 else M_SHIRT_BLUE
    add(f'lowerarm_{side}', mt.tube(f'HQ_SleeveCuff_{side}',
                                    ring_points([lb], c_la, SLEEVE_END + 0.008, 0.003), 0.012, cuff_m))
    add(f'upperarm_{side}', ua); add(f'lowerarm_{side}', la)

# =========================================================== 2. SHOULDER HOLSTER
strap_paths = []
for s in (-1, 1):
    front = mt.project(SB, mt.catmull([(s * 0.47, 3.27), (s * 0.4, 3.45), (s * 0.34, 3.6)], 30), 'front')
    top = mt.project(SB, mt.catmull([(s * 0.34, 0.12), (s * 0.35, -0.05), (s * 0.34, -0.22)], 20), 'top')
    back = mt.project(SB, mt.catmull([(s * 0.34, 3.6), (s * 0.22, 3.35), (s * 0.04, 3.12)], 30), 'back')
    path = front + top + back
    add('torso', mt.ribbon(f'HQ_HolsterStrap{s}', mt.resample(path, 0.01), 0.04, 0.006, 0.006, M_LEATHER))
    # stitching along the strap
    bm = bmesh.new(); rs = mt.resample(path, 0.022)
    for i in range(1, len(rs) - 1):
        co, n = rs[i]
        t, b, n = mt.frame_at(co, n, (rs[i + 1][0] - rs[i - 1][0]).normalized())
        for sg in (-1, 1):
            mt.box(bm, co + n * 0.0125 + b * sg * 0.013, t, b, n, 0.0055, 0.001, 0.001)
    add('torso', mt.mesh_obj(f'HQ_HolsterStitch{s}', bm, M_STITCH_D))
# ring where the straps cross at the back
co, n = mt.project(SB, [(0, 3.11)], 'back')[0]
t, b, n = mt.frame_at(co, n, UP)
add('torso', mt.tube('HQ_HolsterRing', [co + n * 0.016 + (t * math.cos(a) + b * math.sin(a)) * 0.028
                                        for a in [2 * math.pi * i / 32 for i in range(33)]], 0.006, M_SILVER))
# drop strap + holster on her left side (under the arm)
hside = -RT
drop = mt.project(SB, mt.catmull([(180, 3.27), (183, 3.12)], 10), 'cyl')
add('torso', mt.ribbon('HQ_HolsterDrop', mt.resample(drop, 0.01), 0.034, 0.006, 0.006, M_LEATHER))
hit = mt.outer_hit([SB], Vector((0, 0, 2.93)) + side_dir(183) * 5, -side_dir(183))
hn = side_dir(183); hc = hit[0] + hn * 0.04
ht = UP.cross(hn).normalized()
bm = bmesh.new(); mt.box(bm, hc, ht, UP, hn, 0.055, 0.15, 0.028)
hol = mt.mesh_obj('HQ_Holster', bm, M_LEATHER); mt.add_bevel(hol, 0.02, 4); mt.smooth(hol)
add('torso', hol)
bm = bmesh.new(); mt.box(bm, hc + UP * 0.13 + hn * 0.03, ht, UP, hn, 0.045, 0.045, 0.006)
flap = mt.mesh_obj('HQ_HolsterFlap', bm, M_LEATHER); mt.add_bevel(flap, 0.01, 3); add('torso', flap)
snap = mt.tube('HQ_HolsterSnap', [hc + UP * 0.1 + hn * 0.036, hc + UP * 0.1 + hn * 0.046], 0.011, M_SILVER)
add('torso', snap)
bm = bmesh.new(); mt.box(bm, hc + UP * 0.2, ht, UP, hn, 0.03, 0.05, 0.02)
grip = mt.mesh_obj('HQ_PistolGrip', bm, M_GUN); mt.add_bevel(grip, 0.012, 3); add('torso', grip)

# =========================================================== 3. CHOKER "PUDDIN"
tb, ttmp = raw_bvh('torso'); bpy.data.objects.remove(ttmp)
CH_Z = 3.682
choker = ring_multi('HQ_Choker', [tb], neck_c, CH_Z, 0.042, 0.003, 0.009, M_CHOKER, nseg=72)
mt.add_bevel(choker, 0.003); add('torso', choker)
# raycast against the evaluated choker (with thickness): build from a temp copy
tmpc = choker.copy(); tmpc.data = choker.data.copy(); mt.COLL.objects.link(tmpc)
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(tmpc.evaluated_get(dg)); bpy.data.objects.remove(tmpc)
bmc = bmesh.new(); bmc.from_mesh(me); cbv = mt.BVHTree.FromBMesh(bmc); bmc.free(); bpy.data.meshes.remove(me)
add('torso', decal_from_mesh('HQ_Choker_Letters', text_mesh('PUDDIN', FONT_BLOCK, 0.036), cbv, 0, CH_Z, 0.0005,
                             0.003, M_GOLD, mode='cyl', center=neck_c, ang0=90, radius=0.235))
add('torso', mt.tube('HQ_Choker_Ring', [mt.project(cbv, [(90, CH_Z - 0.021)], 'cyl', neck_c)[0][0]
                                        + F * 0.004 + UP * (-0.012 * math.cos(a)) + RT * (0.012 * math.sin(a))
                                        for a in [2 * math.pi * i / 24 for i in range(25)]], 0.0028, M_GOLD))

# =========================================================== 4. SEQUIN HOT PANTS + BELT
shorts = mt.world_copy(PARTS['hips'], 'HQ_Shorts_Hips', level=2)
mt.offset_shell(shorts, 0.017)
bm = bmesh.new(); bm.from_mesh(shorts.data)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=Vector((0, 0, 0)), plane_no=RT)
bm.to_mesh(shorts.data); bm.free()
shorts.data.materials.append(M_SEQ_RED); shorts.data.materials.append(M_SEQ_BLUE)
for p in shorts.data.polygons:
    p.material_index = 0 if p.center.dot(RT) >= 0 else 1
mt.smooth(shorts); add('hips', shorts)
SHB = [mt.bvh_of(shorts)]
LEGSH = {}
for side, s in SIDES:
    lg = mt.world_copy(PARTS[f'upperleg_{side}'], f'HQ_Shorts_Leg_{side}', level=2)
    mt.offset_shell(lg, 0.017)
    lc = mt.slice_center(lg, 1.95)
    # leg opening: higher on the outside of the thigh
    hem = lambda a, s=s: 1.935 + 0.05 * max(0.0, math.cos(math.radians(a)) * s)
    cut_by_curve(lg, lc, hem, keep_above=True)
    lg.data.materials.append(M_SEQ_RED if s > 0 else M_SEQ_BLUE); mt.smooth(lg)
    LEGSH[side] = lg
    lbv = mt.bvh_of(lg); SHB.append(lbv)
    add(f'upperleg_{side}', lg)
    add(f'upperleg_{side}', mt.tube(f'HQ_Shorts_Hem_{side}', ring_points([lbv], lc, 0, 0.003,
                                    z_fn=lambda a, h=hem: h(a) + 0.007), 0.009,
                                    M_SEQ_RED if s > 0 else M_SEQ_BLUE))

# belt
BZ = lambda a: 2.205 + 0.02 * math.cos(math.radians(a))   # a touch lower on her left
BH = 0.058
belt = ring_multi('HQ_Belt', SHB, (0, -0.01), 0, BH, 0.006, 0.013, M_LEATHER, nseg=144, z_fn=BZ)
mt.add_bevel(belt, 0.003); add('hips', belt)
BUCKLE_A = 82


def belt_frame(a, lift):
    hit = mt.outer_hit(SHB, Vector((0, -0.01, BZ(a))) + side_dir(a) * 5, -side_dir(a))
    p, n = hit[0] + hit[1] * lift, hit[1]
    hit2 = mt.outer_hit(SHB, Vector((0, -0.01, BZ(a + 1))) + side_dir(a + 1) * 5, -side_dir(a + 1))
    t = ((hit2[0] + hit2[1] * lift) - p).normalized()
    b = n.cross(t).normalized()
    if b.z < 0: b = -b
    return p, t, b, n


# gold pyramid studs in two rows (gap around the buckle), silver grommets in between
bm = bmesh.new(); bm_g = []
a = 0.0
while a < 360:
    if abs(((a - BUCKLE_A + 180) % 360) - 180) > 13:
        p, t, b, n = belt_frame(a, 0.006 + 0.013)
        for row in (-1, 1):
            c = p + b * row * BH * 0.24
            base = [bm.verts.new(c + t * sx * 0.0085 + b * sy * 0.0085) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            apex = bm.verts.new(c + n * 0.011)
            bm.faces.new(base[::-1])
            for i in range(4):
                bm.faces.new((base[i], base[(i + 1) % 4], apex))
    a += 3.2
studs = mt.mesh_obj('HQ_Belt_Studs', bm, M_GOLD); add('hips', studs)
bp, bt, bb, bn = belt_frame(BUCKLE_A, 0.006 + 0.013 + 0.008)
add('hips', mt.tube('HQ_Belt_Buckle', mt.rounded_rect(bp, bt, bb, 0.046, 0.062, k=2.0, n=80), 0.0085, M_GOLD))
add('hips', mt.tube('HQ_Belt_BuckleInner', mt.rounded_rect(bp + bn * 0.003, bt, bb, 0.024, 0.033, k=2.0, n=60),
                    0.006, M_GOLD))
add('hips', mt.tube('HQ_Belt_BuckleBar', [bp - bt * 0.024, bp + bt * 0.024], 0.004, M_GOLD))

# =========================================================== 5. ARM ACCESSORIES
for side, s in SIDES:
    fa_tmp = mt.world_copy(PARTS[f'lowerarm_{side}'], '_tmp_fa', level=2)
    hd_tmp = mt.world_copy(PARTS[f'hand_{side}'], '_tmp_hd', level=2)
    c_w = mt.slice_center(fa_tmp, 2.32)
    wrist = mt.join([fa_tmp, hd_tmp], '_tmp_wrist')
    fb = mt.bvh_of(wrist); bpy.data.objects.remove(wrist)
    if s > 0:
        # her right: harlequin diamond tattoo on the forearm + purple wristband
        k = 0
        for row in range(4):
            for col in range(4):
                ang = 30 + col * 17 + (8.5 if row % 2 else 0)
                z = 2.39 + row * 0.042
                if z > SLEEVE_END - 0.03: continue
                m = M_INK_RED if (row + col) % 2 else M_INK_BLK
                ob = patch(f'HQ_Tattoo_Arm{k}', fb, diamond2d(ang, z, 15, 0.075), 0.0015, 0.0008, m, 'cyl', c_w)
                add(f'lowerarm_{side}', ob); k += 1
        wb = ring_multi(f'HQ_Wristband_{side}', [fb], c_w, 2.3, 0.085, 0.006, 0.016, M_PURPLE)
        mt.add_bevel(wb, 0.005); add(f'lowerarm_{side}', wb)
        for k, dz in enumerate((-0.0425, 0.0425)):
            add(f'lowerarm_{side}', mt.tube(f'HQ_Wristband_Edge{k}_{side}',
                                            ring_points([fb], c_w, 2.3 + dz, 0.014), 0.005, M_LEATHER))
    else:
        # her left: spiked bracelet + purple band
        br = ring_multi(f'HQ_Bracelet_{side}', [fb], c_w, 2.33, 0.055, 0.005, 0.014, M_LEATHER)
        mt.add_bevel(br, 0.004); add(f'lowerarm_{side}', br)
        for i in range(10):
            a = 36 * i
            d = side_dir(a)
            hit = fb.ray_cast(Vector((c_w[0], c_w[1], 2.33)) + d * 5, -d)
            base = hit[0] + hit[1] * 0.018
            add(f'lowerarm_{side}', mt.claw(f'HQ_Spike_{side}{i}', base, hit[1], UP, M_GOLD, length=0.04, radius=0.011,
                                            hook=0.0))
        pb = ring_multi(f'HQ_Band_{side}', [fb], c_w, 2.255, 0.03, 0.004, 0.009, M_PURPLE)
        add(f'lowerarm_{side}', pb)
        # fingerless glove (black with red back panel)
        gl = mt.world_copy(PARTS[f'hand_{side}'], f'HQ_Glove_{side}', level=2)
        mt.offset_shell(gl, 0.011)
        bm = bmesh.new(); bm.from_mesh(gl.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((0, 0, 1.985)), plane_no=UP)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z < 1.985], context='FACES')
        bm.to_mesh(gl.data); bm.free()
        gl.data.materials.append(M_LEATHER); gl.data.materials.append(M_CHOKER)
        for p in gl.data.polygons:
            if p.normal.dot(RT * s) > 0.55 and 2.0 < p.center.z < 2.2:
                p.material_index = 1
        mt.smooth(gl); add(f'hand_{side}', gl)
        gb = mt.bvh_of(gl); gc = mt.slice_center(gl, 2.0)
        add(f'hand_{side}', mt.tube(f'HQ_Glove_Edge_{side}', ring_points([gb], gc, 1.99, 0.002), 0.008, M_LEATHER))

# =========================================================== 6. FISHNET TIGHTS + THIGH TATTOOS
N_AROUND = 44


def fishnet(name, bvh, center_fn, z_top, z_bot, lift):
    """Diamond lattice wrapped round a limb -> Wireframe modifier = real net."""
    r0 = 0.2
    dth = 2 * math.pi / N_AROUND
    dz = math.pi * r0 / N_AROUND
    rows = int((z_top - z_bot) / dz) + 1
    bm = bmesh.new(); grid = []
    for j in range(rows):
        z = z_top - j * dz
        cx, cy = center_fn(z)
        row = []
        for i in range(N_AROUND):
            a = (i + 0.5 * (j % 2)) * dth
            d = RT * math.cos(a) + F * math.sin(a)
            hit = bvh.ray_cast(Vector((cx, cy, z)) + d * 5, -d)
            co = hit[0] + hit[1] * lift if hit[0] is not None else Vector((cx, cy, z)) + d * r0
            row.append(bm.verts.new(co))
        grid.append(row)
    for j in range(rows - 2):
        for i in range(N_AROUND):
            if j % 2 == 0:
                r_, l_ = grid[j + 1][i], grid[j + 1][(i - 1) % N_AROUND]
            else:
                r_, l_ = grid[j + 1][(i + 1) % N_AROUND], grid[j + 1][i]
            try:
                bm.faces.new((grid[j][i], r_, grid[j + 2][i], l_))
            except ValueError:
                pass
    ob = mt.mesh_obj(name, bm, M_NET)
    w = ob.modifiers.new('Net', 'WIREFRAME'); w.thickness = 0.0032; w.use_even_offset = True
    w.use_replace = True; w.use_boundary = True
    return ob


for side, s in SIDES:
    ub, utmp = raw_bvh(f'upperleg_{side}', 0.0, level=2)
    lb_, ltmp = raw_bvh(f'lowerleg_{side}', 0.0, level=2)
    add(f'upperleg_{side}', fishnet(f'HQ_Fishnet_Upper_{side}', ub, lambda z, o=utmp: mt.slice_center(o, z),
                                    1.99, 0.985, 0.0045))
    add(f'lowerleg_{side}', fishnet(f'HQ_Fishnet_Lower_{side}', lb_, lambda z, o=ltmp: mt.slice_center(o, z),
                                    1.0, 0.84, 0.0045))
    if s > 0:
        uc = mt.slice_center(utmp, 1.6)
        for k, (ang, z, sz, m) in enumerate(((78, 1.70, 0.05, M_INK_BLK), (96, 1.64, 0.04, M_INK_BLK),
                                              (70, 1.58, 0.035, M_INK_RED), (90, 1.52, 0.045, M_INK_BLK))):
            add(f'upperleg_{side}', patch(f'HQ_Tattoo_Thigh{k}', ub, diamond2d(ang, z, math.degrees(sz / 0.22) * 0.75, sz), 0.0016,
                                          0.0008, m, 'cyl', uc))
    bpy.data.objects.remove(utmp); bpy.data.objects.remove(ltmp)

# =========================================================== 7. HIGH-TOP SNEAKERS
SNK_TOP = 0.88
for side, s in SIDES:
    shaft = mt.world_copy(PARTS[f'lowerleg_{side}'], f'HQ_Sneaker_Shaft_{side}', level=3)
    mt.offset_shell(shaft, 0.03)
    sc_ = mt.slice_center(shaft, 0.6)
    top_z = lambda a: SNK_TOP + 0.025 * max(0.0, math.sin(math.radians(a))) ** 2
    cut_by_curve(shaft, sc_, top_z, keep_above=False)
    mt.add_folds(shaft, Vector((sc_[0], sc_[1], 0.56)) + F * 0.06, (0.42, 0.45, 0.07), (0, 0, 1), 0.008, 0.05)
    shaft.data.materials.append(M_SNK_BLK); mt.smooth(shaft)
    foot = mt.world_copy(PARTS[f'foot_{side}'], f'HQ_Sneaker_Foot_{side}', level=2)
    mt.offset_shell(foot, 0.026)
    foot.data.materials.append(M_SNK_WHT); foot.data.materials.append(M_SNK_BLK)
    for p in foot.data.polygons:
        if p.center.dot(F) < -0.12 and p.center.z > 0.06:
            p.material_index = 1            # black heel counter
    mt.smooth(foot)
    SHb, FTb = mt.bvh_of(shaft), mt.bvh_of(foot)
    add(f'lowerleg_{side}', shaft); add(f'foot_{side}', foot)
    # padded collar
    add(f'lowerleg_{side}', mt.tube(f'HQ_Sneaker_Collar_{side}', ring_points([SHb], sc_, 0, 0.006,
                                    z_fn=lambda a, f=top_z: f(a) - 0.006), 0.021, M_SNK_WHT))
    # tongue rising above the collar at the front
    tongue = mt.project(SHb, mt.catmull([(90, 0.5), (90, 0.75), (90, SNK_TOP + 0.02)], 20), 'cyl', sc_)
    tongue += [(tongue[-1][0] + UP * 0.03 + F * 0.012, tongue[-1][1]), (tongue[-1][0] + UP * 0.06 + F * 0.02, tongue[-1][1])]
    add(f'lowerleg_{side}', mt.ribbon(f'HQ_Sneaker_Tongue_{side}', tongue, 0.085, 0.004, 0.012, M_SNK_BLK))
    # eyelets + criss-cross laces + bow
    rows = [0.5 + i * 0.062 for i in range(7)]
    eyes = []
    for z in rows:
        pr = []
        for sg in (-1, 1):
            co, n = mt.project(SHb, [(90 - sg * 15, z)], 'cyl', sc_)[0]
            t, b, n = mt.frame_at(co, n, UP)
            add(f'lowerleg_{side}', mt.tube(f'HQ_Eyelet_{side}{z:.2f}{sg}',
                                            [co + n * 0.004 + (t * math.cos(a) + b * math.sin(a)) * 0.009
                                             for a in [2 * math.pi * i / 16 for i in range(17)]], 0.003, M_SILVER))
            pr.append(co + n * 0.012)
        eyes.append(pr)
    lace = []
    for k in range(len(eyes) - 1):
        for sg in (0, 1):
            a_, b_ = eyes[k][sg], eyes[k + 1][1 - sg]
            mid = (a_ + b_) / 2 + (side_dir(90) * 0.008)
            lace.append(mt.tube(f'HQ_Lace_{side}{k}{sg}', [a_, mid, b_], 0.0058, M_LACE, res=2))
    lace.append(mt.tube(f'HQ_Lace_{side}base', [eyes[0][0], eyes[0][1]], 0.0058, M_LACE, res=2))
    top_l, top_r = eyes[-1]
    knot = (top_l + top_r) / 2 + F * 0.014
    for sg in (-1, 1):
        loop = [knot + RT * (sg * 0.045 * math.sin(a / 2)) + UP * (0.02 * math.sin(a)) + F * 0.004 * math.sin(a / 2)
                for a in [2 * math.pi * i / 20 for i in range(21)]]
        lace.append(mt.tube(f'HQ_Bow_{side}{sg}', loop, 0.0055, M_LACE, res=2))
        lace.append(mt.tube(f'HQ_BowEnd_{side}{sg}', [knot, knot + RT * sg * 0.02 - UP * 0.04 + F * 0.01,
                                                      knot + RT * sg * 0.028 - UP * 0.075 + F * 0.012], 0.0055,
                            M_LACE, res=2))
    add(f'lowerleg_{side}', mt.join(lace, f'HQ_Laces_{side}'))
    # side panel seam + stitching on the shaft
    seam_objs = mt.seam(f'HQ_Sneaker_Seam_{side}', [(0 if s > 0 else 180, SNK_TOP - 0.02), (0 if s > 0 else 180, 0.47)],
                        'cyl', SHb, (M_SNK_BLK, M_STITCH), n=30, center=sc_)
    seam_objs += mt.seam(f'HQ_Sneaker_ToeCap_{side}', [(s * 0.262 - 0.19, 0.16), (s * 0.262 - 0.12, 0.25),
                                                        (s * 0.262, 0.29), (s * 0.262 + 0.12, 0.25),
                                                        (s * 0.262 + 0.19, 0.16)], 'top', FTb, (M_SNK_BLK, M_STITCH_D), n=40,
                         r=0.007)
    mud = mt.outline_at(FTb, (s * 0.262, 0.055), 0.115, grow=0.002)
    add(f'foot_{side}', mt.tube(f'HQ_Sneaker_Mudguard_{side}', [Vector((p.x, p.y, 0.115)) for p in mud] +
                                [Vector((mud[0].x, mud[0].y, 0.115))], 0.0065, M_SNK_BLK))
    add(f'lowerleg_{side}', seam_objs[:2]); add(f'foot_{side}', seam_objs[2:])
    # sole: white midsole + grey outsole stripe
    outline = mt.outline_at(FTb, (s * 0.262, 0.055), 0.03, grow=0.016)
    add(f'foot_{side}', mt.slab(f'HQ_Sole_{side}', outline, -0.045, 0.06, M_SOLE, shrink=0.99, bevel=0.012))
    add(f'foot_{side}', mt.slab(f'HQ_Outsole_{side}', [p * 1.0 for p in outline], -0.06, -0.04, M_SOLE_GREY,
                                shrink=0.97, bevel=0.006))
    sole_line = mt.outline_at(FTb, (s * 0.262, 0.055), 0.03, grow=0.0235)
    add(f'foot_{side}', mt.tube(f'HQ_SoleStripe_{side}', [Vector((p.x, p.y, 0.012)) for p in sole_line] +
                                [Vector((sole_line[0].x, sole_line[0].y, 0.012))], 0.005, M_SOLE_GREY))

# =========================================================== 8. finishing
for ob in [shirt, shorts] + [o for pair in SLV.values() for o in pair] + list(LEGSH.values()):
    mt.add_solidify(ob, 0.009)
    mt.add_subsurf(ob, 1)
for name in [o.name for o in mt.COLL.objects if o.name.startswith(('HQ_Sneaker_Shaft', 'HQ_Sneaker_Foot', 'HQ_Glove_'))]:
    ob = bpy.data.objects[name]
    if ob.type == 'MESH' and not any(m.type == 'SOLIDIFY' for m in ob.modifiers) and 'Edge' not in name:
        mt.add_solidify(ob, 0.01); mt.add_subsurf(ob, 1)
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
