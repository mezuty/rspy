"""Catwoman (Arkham-style) catsuit morph - full suit.

Top: torso, arms, gloves with claws. Lower: hips, legs, thigh straps and
knee-high heeled boots.

Builds the morph pieces procedurally on top of the Starter 2.0 Rig and saves
a .blend. Run with Blender's Python (bpy 5.2):

    python build_catwoman.py <rig.blend> <out_dir>
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

RIG = sys.argv[-2]
OUT = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=RIG)

PARTS = {
    'torso': 'Robloxian2014',
    'upperarm_R': 'Robloxian2012', 'lowerarm_R': 'Robloxian2011', 'hand_R': 'Robloxian2010',
    'upperarm_L': 'Robloxian209', 'lowerarm_L': 'Robloxian208', 'hand_L': 'Robloxian207',
    'hips': 'Robloxian2013',
    'upperleg_R': 'Robloxian201', 'lowerleg_R': 'Robloxian202', 'foot_R': 'Robloxian203',
    'upperleg_L': 'Robloxian204', 'lowerleg_L': 'Robloxian205', 'foot_L': 'Robloxian206',
}

# ---------------------------------------------------------------- collection
rig_coll = bpy.data.collections['Starter 2.0 Rig']
coll = bpy.data.collections.new('Catwoman Morph')
bpy.context.scene.collection.children.link(coll)


# ----------------------------------------------------------------- materials
def principled(name, base, rough, metal=0.0, coat=0.0, coat_rough=0.1, spec=0.5,
               bump=None):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Specular IOR Level'].default_value = spec
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = coat_rough
    if bump:
        scale, strength = bump
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = scale
        nz.inputs['Detail'].default_value = 6
        bp = nt.nodes.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = strength
        bp.inputs['Distance'].default_value = 0.002
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
        nt.links.new(bp.outputs['Normal'], p.inputs['Normal'])
    m.diffuse_color = (*base, 1)   # viewport solid colour
    m.roughness = rough
    m.metallic = metal
    return m

M_SUIT = principled('CW_Leather_Suit', (0.011, 0.011, 0.013), 0.40, coat=0.22, coat_rough=0.28,
                    bump=(260, 0.08))
M_PANEL = principled('CW_Leather_Piping', (0.02, 0.02, 0.023), 0.30, coat=0.4, coat_rough=0.15)
M_GLOVE = principled('CW_Leather_Glove', (0.008, 0.008, 0.009), 0.46, coat=0.15, coat_rough=0.3,
                     bump=(320, 0.10))
M_STRAP = principled('CW_Leather_Strap', (0.016, 0.016, 0.018), 0.36, coat=0.3, coat_rough=0.2)
M_TAPE = principled('CW_Zipper_Tape', (0.012, 0.012, 0.013), 0.6)
M_METAL = principled('CW_Silver', (0.80, 0.80, 0.82), 0.22, metal=1.0)
M_CLAW = principled('CW_Claw_Steel', (0.62, 0.63, 0.66), 0.18, metal=1.0)
M_STITCH = principled('CW_Stitch', (0.10, 0.10, 0.11), 0.7)
M_BOOT = principled('CW_Leather_Boot', (0.008, 0.008, 0.009), 0.28, coat=0.5, coat_rough=0.1,
                    bump=(300, 0.05))
M_SOLE = principled('CW_Boot_Sole', (0.018, 0.018, 0.02), 0.65)


# ------------------------------------------------------------------- helpers
def world_copy(src_name, new_name, level=None):
    """New object holding the evaluated (subdivided) mesh of a rig part, in world space."""
    src = bpy.data.objects[src_name]
    sub = next((m for m in src.modifiers if m.type == 'SUBSURF'), None)
    old = sub.levels if sub else None
    if sub and level is not None:
        sub.levels = level
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
    if sub and level is not None:
        sub.levels = old
    me.transform(src.matrix_world)
    me.materials.clear()
    ob = bpy.data.objects.new(new_name, me)
    coll.objects.link(ob)
    return ob


def offset_shell(ob, dist):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * dist
    bm.to_mesh(ob.data); bm.free()


def smooth_region(ob, weight_fn, iters=20):
    """Relax vertices (weight 0..1) so the suit bridges small body dents."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for _ in range(iters):
        new = {}
        for v in bm.verts:
            w = weight_fn(v.co)
            if w <= 0 or not v.link_edges: continue
            avg = sum((e.other_vert(v).co for e in v.link_edges), Vector()) / len(v.link_edges)
            new[v] = v.co.lerp(avg, 0.5 * w)
        for v, c in new.items(): v.co = c
    bm.to_mesh(ob.data); bm.free()


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


def add_subsurf(ob, lv=1, rlv=2):
    m = ob.modifiers.new('Subdivision', 'SUBSURF')
    m.levels, m.render_levels = lv, rlv
    return m


def add_solidify(ob, t, offset=-1.0, rim=True):
    m = ob.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = t; m.offset = offset; m.use_rim = rim; m.use_even_offset = False
    m.use_quality_normals = True
    return m


def bvh_of(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


def catmull(pts, n):
    """Catmull-Rom through pts (list of Vector), n samples."""
    pts = [Vector(p) for p in pts]
    P = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    out = []
    segs = len(pts) - 1
    for i in range(n):
        t = i / (n - 1) * segs
        k = min(int(t), segs - 1); u = t - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u))
    return out


def project(bvh, pts2d, mode, center=(0.0, 0.0)):
    """Project 2D control samples onto a surface. Returns list of (co, normal).
    mode 'front': (x,z) ray along -Y; 'back': (x,z) ray along +Y;
    'top': (x,y) ray along -Z; 'cyl': (angle_deg, z) radial ray towards center."""
    res = []
    for p in pts2d:
        if mode == 'front':
            o, d = Vector((p[0], 3.0, p[1])), Vector((0, -1, 0))
        elif mode == 'back':
            o, d = Vector((p[0], -3.0, p[1])), Vector((0, 1, 0))
        elif mode in ('xpos', 'xneg'):
            sx = 1 if mode == 'xpos' else -1
            o, d = Vector((sx * 3.0, p[0], p[1])), Vector((-sx, 0, 0))
        elif mode == 'top':
            o, d = Vector((p[0], p[1], 6.0)), Vector((0, 0, -1))
        else:
            a = math.radians(p[0])
            r = Vector((math.cos(a), math.sin(a), 0))
            o = Vector((center[0], center[1], p[1])) + r * 3.0
            d = -r
        hit, n, i, dist = bvh.ray_cast(o, d)
        if hit is not None:
            res.append((hit, n))
    return res


def curve_tube(name, pts, radius, mat, res=3, caps=True):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    cu.bevel_depth = radius; cu.bevel_resolution = res; cu.use_fill_caps = caps
    ob = bpy.data.objects.new(name, cu); coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def to_mesh(ob):
    """Convert a curve object into a mesh object (same name)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    name = ob.name; mats = list(ob.data.materials)
    bpy.data.objects.remove(ob)
    new = bpy.data.objects.new(name, me); coll.objects.link(new)
    if not me.materials:
        for m in mats: me.materials.append(m)
    smooth(new)
    return new


def join(obs, name):
    obs = [o for o in obs if o]
    with bpy.context.temp_override(active_object=obs[0], selected_editable_objects=obs,
                                   selected_objects=obs):
        bpy.ops.object.join()
    obs[0].name = name
    return obs[0]


def apply_mods(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear(); ob.data = me
    bpy.data.meshes.remove(old)


def frame_at(co, n, tangent_hint):
    """Orthonormal frame (t, b, n) at a surface point."""
    n = n.normalized()
    t = (tangent_hint - n * tangent_hint.dot(n)).normalized()
    b = n.cross(t)
    return t, b, n


def box(bm, center, t, b, n, sx, sy, sz):
    """Append a box to bm, axes t,b,n with half sizes."""
    vs = []
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                vs.append(bm.verts.new(center + t * sx * i + b * sy * j + n * sz * k))
    idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for f in idx:
        bm.faces.new([vs[i] for i in f])


def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    me.materials.append(mat)
    return ob


def resample(path, step):
    """Resample a polyline (list of (co,n)) at constant arc length."""
    out = [path[0]]; acc = 0.0
    for a, b in zip(path, path[1:]):
        seg = (b[0] - a[0]).length
        if seg < 1e-9: continue
        acc += seg
        while acc >= step:
            acc -= step
            f = 1 - acc / seg
            out.append((a[0].lerp(b[0], f), a[1].lerp(b[1], f).normalized()))
    return out


def ribbon(name, path, width, lift, thick, mat, side_bias=0.0):
    """Flat strip following a surface path (list of (co, n))."""
    bm = bmesh.new(); rows = []
    for i, (co, n) in enumerate(path):
        nxt = path[min(i + 1, len(path) - 1)][0]; prv = path[max(i - 1, 0)][0]
        t = (nxt - prv).normalized()
        b = n.cross(t).normalized()
        c = co + n * lift + b * side_bias
        rows.append((bm.verts.new(c - b * width / 2), bm.verts.new(c + b * width / 2)))
    for r0, r1 in zip(rows, rows[1:]):
        bm.faces.new((r0[0], r0[1], r1[1], r1[0]))
    ob = mesh_obj(name, bm, mat)
    add_solidify(ob, thick, offset=1.0)
    smooth(ob)
    return ob


# =========================================================== 1. SUIT SHELLS
SUIT = {}
torso = world_copy(PARTS['torso'], 'CW_Suit_Torso')
offset_shell(torso, 0.016)


def navel_w(c):
    # belly button + spine groove: let the leather stretch over them
    if c.y < 0.1 or c.z < 2.3 or c.z > 2.6: return 0.0
    d = math.hypot(c.x / 0.10, (c.z - 2.435) / 0.09)
    return min(1.0, max(0.0, 1.3 * (1.0 - d)))


smooth_region(torso, navel_w, 160)

# --- open V-neck (zipper pulled down), cut with two clean bisect planes
V_TOP_Z, V_BOT_Z, V_HALF = 3.80, 3.10, 0.229
V_TAPE_TOP = 3.615
bm = bmesh.new(); bm.from_mesh(torso.data)
for s in (-1, 1):
    a = Vector((s * V_HALF, 0, V_TOP_Z)); b = Vector((0, 0, V_BOT_Z))
    d = (a - b).normalized()
    nrm = Vector((d.z, 0, -d.x)) * s
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=b, plane_no=nrm)


def in_v(c):
    if c.y < 0.0 or c.z < V_BOT_Z: return False
    half = V_HALF * (c.z - V_BOT_Z) / (V_TOP_Z - V_BOT_Z)
    return abs(c.x) < half


dead = [f for f in bm.faces if in_v(f.calc_center_median())]
bmesh.ops.delete(bm, geom=dead, context='FACES')
bm.to_mesh(torso.data); bm.free()
SUIT['torso'] = torso

for side in ('R', 'L'):
    for part, off in (('upperarm', 0.016), ('lowerarm', 0.016), ('hand', 0.011)):
        ob = world_copy(PARTS[f'{part}_{side}'], f'CW_Suit_{part.capitalize()}_{side}')
        offset_shell(ob, off)
        SUIT[f'{part}_{side}'] = ob

# glove = hand + lower forearm (below the cuff line); rest of sleeve = suit
GLOVE_Z = 2.47
for key, ob in SUIT.items():
    me = ob.data
    if key.startswith('hand'):
        me.materials.append(M_GLOVE)
    elif key.startswith('lowerarm'):
        me.materials.append(M_SUIT); me.materials.append(M_GLOVE)
        for p in me.polygons:
            p.material_index = 1 if p.center.z < GLOVE_Z else 0
    else:
        me.materials.append(M_SUIT)
    smooth(ob)

BVH = {k: bvh_of(o) for k, o in SUIT.items()}


def arm_center(ob, z):
    tol = 0.02
    vs = []
    while not vs:   # widen the slice where the mesh is sparse
        vs = [v.co for v in ob.data.vertices if abs(v.co.z - z) < tol]
        tol *= 2
    xs = [v.x for v in vs]; ys = [v.y for v in vs]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


# ========================================================= 2. ZIPPER
zip_parts = []
# closed zipper: centre front from bottom of the V to the hem
zc = project(BVH['torso'], catmull([(0, V_BOT_Z), (0, 2.8), (0, 2.45), (0, 2.21)], 80), 'front')
zc = resample(zc, 0.0125)
zip_parts.append(ribbon('CW_ZipTape_C', zc, 0.034, 0.0015, 0.003, M_TAPE))
bm = bmesh.new()
for i, (co, n) in enumerate(zc[1:-1]):
    t, b, n = frame_at(co, n, Vector((0, 0, -1)))
    box(bm, co + n * 0.0045 + b * (0.0035 if i % 2 else -0.0035), t, b, n, 0.0042, 0.0085, 0.0028)
teeth = mesh_obj('CW_ZipTeeth_C', bm, M_METAL)
zip_parts.append(teeth)

# open zipper: tape + teeth along each edge of the V
for s in (-1, 1):
    edge = [(s * (V_HALF * (z - V_BOT_Z) / (V_TOP_Z - V_BOT_Z) + 0.016), z)
            for z in [V_BOT_Z + 0.01 + i * (V_TAPE_TOP - V_BOT_Z) / 40 for i in range(41)]]
    pth = resample(project(BVH['torso'], edge, 'front'), 0.0125)
    zip_parts.append(ribbon(f'CW_ZipTape_V{s}', pth, 0.022, 0.0015, 0.003, M_TAPE))
    bm = bmesh.new()
    for co, n in pth[1:]:
        tdir = (pth[-1][0] - pth[0][0]).normalized()
        t, b, n = frame_at(co, n, tdir)
        side = b if b.x * s < 0 else -b   # towards the opening
        box(bm, co + n * 0.0045 + side * 0.009, t, side, n, 0.0042, 0.0055, 0.0028)
    zip_parts.append(mesh_obj(f'CW_ZipTeeth_V{s}', bm, M_METAL))

# slider + pull tab at the bottom of the V
co, n = project(BVH['torso'], [(0, V_BOT_Z - 0.012)], 'front')[0]
t, b, n = frame_at(co, n, Vector((0, 0, -1)))
bm = bmesh.new()
box(bm, co + n * 0.012, t, b, n, 0.026, 0.017, 0.0075)
slider = mesh_obj('CW_ZipSlider', bm, M_METAL)
bv = slider.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.005; bv.segments = 3
zip_parts.append(slider)
# pull tab: rounded loop hanging down from the slider
tab_c = co + n * 0.02 + t * 0.055
loop = []
for i in range(25):
    a = 2 * math.pi * i / 24
    loop.append(tab_c + t * (math.cos(a) * 0.038) + b * (math.sin(a) * 0.016))
tab = curve_tube('CW_ZipPull', loop, 0.0055, M_METAL)
zip_parts.append(to_mesh(tab))
zipper = join(zip_parts, 'CW_Zipper')
smooth(zipper)

# ========================================================= 3. PANEL SEAMS (piping)
SEAMS = {}


def seam(name, ctrl, mode, bvh, n=70, center=(0, 0), r=0.0048, group='torso', stitch=True):
    seam_objs = SEAMS.setdefault(group, [])
    p = project(bvh, catmull(ctrl, n), mode, center)
    if len(p) < 3: return
    pts = [co + nn * 0.0015 for co, nn in p]
    seam_objs.append(to_mesh(curve_tube(name, pts, r, M_PANEL)))
    if not stitch: return
    # stitching: small dashes offset to one side of the seam
    bm = bmesh.new()
    rs = resample(p, 0.024)
    for i in range(1, len(rs) - 1):
        co, nn = rs[i]
        tdir = (rs[i + 1][0] - rs[i - 1][0]).normalized()
        t, b, nn = frame_at(co, nn, tdir)
        for sgn in (-1, 1):
            box(bm, co + nn * 0.0012 + b * 0.0125 * sgn, t, b, nn, 0.0065, 0.0012, 0.0012)
    seam_objs.append(mesh_obj(name + '_stitch', bm, M_STITCH))


tb = BVH['torso']
for s in (-1, 1):
    # front princess seams over the bust, nipping into the waist
    seam(f'CW_Seam_Princess_F{s}', [(s * 0.34, 3.585), (s * 0.27, 3.42), (s * 0.235, 3.22),
                                     (s * 0.205, 2.98), (s * 0.165, 2.72), (s * 0.17, 2.52),
                                     (s * 0.215, 2.32), (s * 0.24, 2.205)], 'front', tb)
    # back princess seams
    seam(f'CW_Seam_Princess_B{s}', [(s * 0.32, 3.57), (s * 0.25, 3.35), (s * 0.20, 3.05),
                                     (s * 0.16, 2.75), (s * 0.17, 2.5), (s * 0.23, 2.205)], 'back', tb)
    # side seams
    seam(f'CW_Seam_Side{s}', [(0 if s > 0 else 180, z) for z in (3.36, 3.1, 2.8, 2.5, 2.205)],
         'cyl', tb)
    # shoulder seams over the top
    seam(f'CW_Seam_Shoulder{s}', [(s * 0.215, -0.06), (s * 0.35, -0.07), (s * 0.5, -0.08)], 'top', tb,
         n=30)
    # curved under-bust panel line (corset feel), stops at the zipper tape
    seam(f'CW_Seam_Underbust{s}', [(s * 0.05, 2.99), (s * 0.12, 2.955), (s * 0.18, 2.94),
                                    (s * 0.205, 2.95)], 'front', tb, n=30)
# centre back seam
seam('CW_Seam_Back_C', [(0, 3.66), (0, 3.2), (0, 2.8), (0, 2.205)], 'back', tb)

# sleeve seams (outer line of each arm) + front lines on the upper arm
for side, s in (('R', 1), ('L', -1)):
    ua = SUIT[f'upperarm_{side}']; la = SUIT[f'lowerarm_{side}']
    c_ua = arm_center(ua, 3.1); c_la = arm_center(la, 2.65)
    ang_out = 0 if s > 0 else 180
    seam(f'CW_Seam_UArm_{side}', [(ang_out, z) for z in (3.42, 3.2, 2.95, 2.72)], 'cyl',
         BVH[f'upperarm_{side}'], n=40, center=c_ua, group=f'upperarm_{side}')
    seam(f'CW_Seam_LArm_{side}', [(ang_out, z) for z in (2.82, 2.65, GLOVE_Z + 0.03)], 'cyl',
         BVH[f'lowerarm_{side}'], n=30, center=c_la, group=f'lowerarm_{side}')

# finger divisions on the back of each glove so the mitten hand reads as a glove
for side, s in (('R', 1), ('L', -1)):
    for y in (-0.135, -0.03, 0.07):
        seam(f'CW_Seam_Finger_{side}{y}', [(y, 1.74), (y, 1.86), (y, 1.97)],
             'xpos' if s > 0 else 'xneg', BVH[f'hand_{side}'], n=20, r=0.0042,
             group=f'hand_{side}', stitch=False)

seams = {g: join(obs, 'CW_Seams_' + g) for g, obs in SEAMS.items()}
SEAMS.clear()

# piped hem along the bottom of the top
hem = []
for i in range(73):
    a = 2 * math.pi * i / 72
    r = Vector((math.cos(a), math.sin(a), 0))
    hit, n, _, _ = BVH['torso'].ray_cast(Vector((0, 0, 2.215)) + r * 2, -r)
    hem.append(hit + n * 0.004)
hem_trim = to_mesh(curve_tube('CW_Hem_Trim', hem, 0.011, M_PANEL))

# ========================================================= 4. COLLAR
# A flared stand collar, open at the front. It flares outward (instead of
# straight up) so it clears the rig's low head.
NECK_C = Vector((0, -0.045, 0))
prof = [(0.228, 3.625), (0.262, 3.675), (0.315, 3.725), (0.375, 3.77), (0.405, 3.79)]
GAP = 40.0  # half opening angle at the front (deg)
bm = bmesh.new(); rows = []
nseg = 48
for i in range(nseg + 1):
    a_deg = 90 + GAP + (360 - 2 * GAP) * i / nseg
    a = math.radians(a_deg)
    # collar is a touch lower towards the front opening
    fr = abs(math.cos(math.radians(a_deg - 90) / 2))  # 1 at front, 0 at back
    drop = 0.03 * max(0, (fr - 0.7) / 0.3)
    endf = min(1.0, min(i, nseg - i) / 5.0)
    k = 0.45 + 0.55 * math.sin(endf * math.pi / 2)
    row = []
    for j, (r, z) in enumerate(prof):
        z = prof[0][1] + (z - prof[0][1]) * k
        r = prof[0][0] + (r - prof[0][0]) * k
        zz = z - drop * (j / (len(prof) - 1))
        rr = r - 0.4 * drop * (j / (len(prof) - 1))
        row.append(bm.verts.new(Vector((math.cos(a) * rr, -0.045 + math.sin(a) * rr * 0.95, zz))))
    rows.append(row)
for r0, r1 in zip(rows, rows[1:]):
    for j in range(len(prof) - 1):
        bm.faces.new((r0[j], r1[j], r1[j + 1], r0[j + 1]))
collar = mesh_obj('CW_Collar', bm, M_SUIT)
add_solidify(collar, 0.026, offset=-1.0)
add_subsurf(collar, 2, 2)
smooth(collar)
# piping along the collar's outer edge
edge_pts = []
for i in range(nseg + 1):
    v = collar.data.vertices[i * len(prof) + len(prof) - 1].co
    edge_pts.append(v.copy())
collar_trim = to_mesh(curve_tube('CW_Collar_Trim', edge_pts, 0.008, M_PANEL))

# ========================================================= 5. ARM STRAPS + BUCKLES
strap_objs = []; metal_objs = []


def strap(name, side, s, bvh, center, z, h=0.05, lift=0.006, buckle_ang=None):
    bm = bmesh.new(); rows = []; hits = []
    nseg = 40
    for i in range(nseg):
        a = 2 * math.pi * i / nseg
        r = Vector((math.cos(a), math.sin(a), 0))
        row = []
        for dz in (-h / 2, h / 2):
            o = Vector((center[0], center[1], z + dz)) + r * 2
            hit, n, _, _ = bvh.ray_cast(o, -r)
            row.append(bm.verts.new(hit + n * lift))
        rows.append(row)
    for i in range(nseg):
        r0, r1 = rows[i], rows[(i + 1) % nseg]
        bm.faces.new((r0[0], r1[0], r1[1], r0[1]))
    ob = mesh_obj(name, bm, M_STRAP)
    add_solidify(ob, 0.014, offset=1.0)
    smooth(ob)
    strap_objs.append(ob)
    # buckle on the front/outer side
    a = math.radians(buckle_ang)
    r = Vector((math.cos(a), math.sin(a), 0))
    hit, n, _, _ = bvh.ray_cast(Vector((center[0], center[1], z)) + r * 2, -r)
    up = Vector((0, 0, 1))
    t = up.cross(n).normalized()  # around the arm
    c = hit + n * (lift + 0.016)
    w, hh = 0.04, 0.05
    frame = []
    for i in range(33):
        u = 2 * math.pi * i / 32
        # superellipse -> rounded rectangle
        cx = math.copysign(abs(math.cos(u)) ** 0.45, math.cos(u)) * w
        cz = math.copysign(abs(math.sin(u)) ** 0.45, math.sin(u)) * hh
        frame.append(c + t * cx + up * cz)
    metal_objs.append(to_mesh(curve_tube(name + '_Buckle', frame, 0.0068, M_METAL)))
    bar = [c + t * (-0.004) + up * (-hh), c + t * (-0.004) + up * hh]
    metal_objs.append(to_mesh(curve_tube(name + '_BuckleBar', bar, 0.0045, M_METAL)))
    # prong
    pr = [c + t * (-0.004) + n * 0.003, c + t * (w * 0.85) + n * 0.004]
    metal_objs.append(to_mesh(curve_tube(name + '_Prong', pr, 0.003, M_METAL)))
    # strap tail tucked past the buckle
    tail = bmesh.new()
    tc = c + t * (w + 0.03) - n * 0.004
    box(tail, tc, t, up, n, 0.035, h * 0.42, 0.005)
    tob = mesh_obj(name + '_Tail', tail, M_STRAP)
    tb_ = tob.modifiers.new('Bevel', 'BEVEL'); tb_.width = 0.004; tb_.segments = 2
    strap_objs.append(tob)


for side, s in (('R', 1), ('L', -1)):
    ua = SUIT[f'upperarm_{side}']; la = SUIT[f'lowerarm_{side}']
    ang = 50 if s > 0 else 130   # front-outer face of the arm
    strap(f'CW_Strap_UArm_{side}', side, s, BVH[f'upperarm_{side}'], arm_center(ua, 3.08), 3.08,
          buckle_ang=ang)
    strap(f'CW_Strap_LArm_{side}', side, s, BVH[f'lowerarm_{side}'], arm_center(la, 2.64), 2.64,
          h=0.045, buckle_ang=ang)

# glove cuff roll
for side, s in (('R', 1), ('L', -1)):
    la = SUIT[f'lowerarm_{side}']; bvh = BVH[f'lowerarm_{side}']
    c = arm_center(la, GLOVE_Z)
    pts = []
    for i in range(49):
        a = 2 * math.pi * i / 48
        r = Vector((math.cos(a), math.sin(a), 0))
        hit, n, _, _ = bvh.ray_cast(Vector((c[0], c[1], GLOVE_Z)) + r * 2, -r)
        pts.append(hit + n * 0.006)
    strap_objs.append(to_mesh(curve_tube(f'CW_GloveCuff_{side}', pts, 0.012, M_GLOVE)))

# ========================================================= 6. CLAWS
claw_objs = []


def claw(name, base, direction, normal, length=0.07, radius=0.016):
    """Curved tapered claw: ring sweep along a bent path."""
    d = direction.normalized(); nrm = (normal - d * normal.dot(d)).normalized()
    side = d.cross(nrm)
    bm = bmesh.new(); rings = []; steps = 10; seg = 10
    for i in range(steps + 1):
        f = i / steps
        # path bends towards -nrm (hooked claw)
        p = base + d * (length * f) - nrm * (length * 0.45 * f * f)
        tang = (d - nrm * (0.9 * f)).normalized()
        nn = (nrm - tang * nrm.dot(tang)).normalized(); ss = tang.cross(nn)
        rad = radius * (1 - f) ** 0.8 + 0.0008
        ring = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ring.append(bm.verts.new(p + nn * math.cos(a) * rad * 0.75 + ss * math.sin(a) * rad))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k]))
    bm.faces.new(rings[0][::-1])
    tip = bm.verts.new(rings[-1][0].co.lerp(rings[-1][seg // 2].co, 0.5) + (rings[-1][0].co - rings[-2][0].co) * 0.3)
    for k in range(seg):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], tip))
    ob = mesh_obj(name, bm, M_CLAW); smooth(ob)
    claw_objs.append(ob)


for side, s in (('R', 1), ('L', -1)):
    hb = BVH[f'hand_{side}']
    # four fingertips run along Y at the bottom of the mitten hand
    for k, y in enumerate((-0.19, -0.085, 0.02, 0.115)):
        o = Vector((s * 0.99, y, 1.55))
        hit, n, _, _ = hb.ray_cast(o, Vector((0, 0, 1)))
        if hit is None: continue
        claw(f'CW_Claw_{side}{k}', hit + n * 0.002, Vector((-s * 0.55, 0, -1)), Vector((-s, 0, 0)),
             length=0.085, radius=0.02)


# ========================================================= 7. LOWER BODY
def leg_center(ob, z):
    return arm_center(ob, z)


hips = world_copy(PARTS['hips'], 'CW_Suit_Hips')
offset_shell(hips, 0.017)
hips.data.materials.append(M_SUIT); smooth(hips)
SUIT['hips'] = hips

LOW = {}   # extra objects per group
BOOT_TOP = 0.90    # just under the knee joint; the front rises a little


def boot_top_z(ang_deg):
    f = max(0.0, math.sin(math.radians(ang_deg)))      # 1 at the front (+Y)
    return BOOT_TOP + 0.035 * f ** 3


for side in ('R', 'L'):
    ul = world_copy(PARTS[f'upperleg_{side}'], f'CW_Suit_Upperleg_{side}')
    offset_shell(ul, 0.016)
    ul.data.materials.append(M_SUIT); smooth(ul)
    SUIT[f'upperleg_{side}'] = ul

    # catsuit continues under the boot, so the knee never shows skin
    under = world_copy(PARTS[f'lowerleg_{side}'], f'CW_Suit_Lowerleg_{side}')
    offset_shell(under, 0.016)
    under.data.materials.append(M_SUIT); smooth(under)
    add_solidify(under, 0.010, offset=-1.0); add_subsurf(under, 1, 2)
    LOW.setdefault(f'lowerleg_{side}', []).append(under)

    ll = world_copy(PARTS[f'lowerleg_{side}'], f'CW_Boot_Leg_{side}', level=3)
    offset_shell(ll, 0.026)
    ll.data.materials.append(M_BOOT); smooth(ll)
    ft = world_copy(PARTS[f'foot_{side}'], f'CW_Boot_Foot_{side}')
    offset_shell(ft, 0.024)
    ft.data.materials.append(M_BOOT); smooth(ft)
    SUIT[f'lowerleg_{side}'] = ll; SUIT[f'foot_{side}'] = ft

for k in ('hips', 'upperleg_R', 'upperleg_L', 'lowerleg_R', 'lowerleg_L', 'foot_R', 'foot_L'):
    BVH[k] = bvh_of(SUIT[k])

# open the top of each boot along a curved line (peaks over the knee)
BOOT_C = {}
for side in ('R', 'L'):
    ll = SUIT[f'lowerleg_{side}']
    cx, cy = leg_center(ll, 0.8); BOOT_C[side] = (cx, cy)
    bm = bmesh.new(); bm.from_mesh(ll.data)
    dead = []
    for f in bm.faces:
        c = f.calc_center_median()
        ang = math.degrees(math.atan2(c.y - cy, c.x - cx))
        if c.z > boot_top_z(ang): dead.append(f)
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    # snap the opening onto the exact cut curve so the cuff sits flush
    for v in bm.verts:
        if v.is_boundary:
            ang = math.degrees(math.atan2(v.co.y - cy, v.co.x - cx))
            v.co.z = boot_top_z(ang)
    bm.to_mesh(ll.data); bm.free()

def low_add(group, ob):
    LOW.setdefault(group, []).append(ob)
    return ob


for side, s in (('R', 1), ('L', -1)):
    cx, cy = BOOT_C[side]
    bvh = BVH[f'lowerleg_{side}']
    # rolled cuff following the boot top
    pts = []
    for i in range(73):
        a = 360.0 * i / 72
        r = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
        z = boot_top_z(a) - 0.004
        hit, n, _, _ = bvh.ray_cast(Vector((cx, cy, z)) + r * 2, -r)
        pts.append(hit + n * 0.004)
    low_add(f'lowerleg_{side}', to_mesh(curve_tube(f'CW_BootCuff_{side}', pts, 0.016, M_BOOT)))

    # zipper on the inner side of the boot
    ang_in = 180 + 25 if s > 0 else -25          # inner, slightly towards the back
    zp = project(bvh, catmull([(ang_in, BOOT_TOP - 0.03), (ang_in, 0.7), (ang_in, 0.46)], 50),
                 'cyl', center=(cx, cy))
    zp = resample(zp, 0.0125)
    low_add(f'lowerleg_{side}', ribbon(f'CW_BootZipTape_{side}', zp, 0.03, 0.0015, 0.003, M_TAPE))
    bm = bmesh.new()
    for i, (co, n) in enumerate(zp[1:-1]):
        t, b, n = frame_at(co, n, Vector((0, 0, -1)))
        box(bm, co + n * 0.0045 + b * (0.0035 if i % 2 else -0.0035), t, b, n, 0.0042, 0.0080, 0.0028)
    low_add(f'lowerleg_{side}', mesh_obj(f'CW_BootZipTeeth_{side}', bm, M_METAL))
    co, n = zp[1]
    t, b, n = frame_at(co, n, Vector((0, 0, -1)))
    bm = bmesh.new(); box(bm, co + n * 0.011, t, b, n, 0.022, 0.014, 0.0065)
    sl = low_add(f'lowerleg_{side}', mesh_obj(f'CW_BootZipSlider_{side}', bm, M_METAL))
    bv = sl.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.004; bv.segments = 3
    tc = co + n * 0.018 + t * 0.045
    loop = [tc + t * (math.cos(2 * math.pi * i / 24) * 0.03) + b * (math.sin(2 * math.pi * i / 24) * 0.013)
            for i in range(25)]
    low_add(f'lowerleg_{side}', to_mesh(curve_tube(f'CW_BootZipPull_{side}', loop, 0.0045, M_METAL)))

    # ankle strap + buckle on the outer side
    strap(f'CW_Strap_Ankle_{side}', side, s, bvh, leg_center(SUIT[f'lowerleg_{side}'], 0.5), 0.5,
          h=0.045, lift=0.005, buckle_ang=20 if s > 0 else 160)

    # sole + stacked heel
    fb = BVH[f'foot_{side}']
    fcx = s * 0.262; fcy = 0.055
    outline = []
    for i in range(64):
        a = 2 * math.pi * i / 64
        r = Vector((math.cos(a), math.sin(a), 0))
        hit, n, _, _ = fb.ray_cast(Vector((fcx, fcy, 0.02)) + r * 2, -r)
        if hit: outline.append(Vector((hit.x, hit.y, 0)) + Vector((n.x, n.y, 0)).normalized() * 0.012)

    def slab(name, pts, z0, z1, shrink=1.0):
        cen = sum(pts, Vector()) / len(pts)
        bm = bmesh.new()
        top = [bm.verts.new((p.x, p.y, z1)) for p in pts]
        bot = [bm.verts.new((cen + (p - cen) * shrink).to_2d().to_3d() + Vector((0, 0, z0))) for p in pts]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            bm.faces.new((bot[i], bot[j], top[j], top[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = mesh_obj(name, bm, M_SOLE)
        bv = ob.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.009; bv.segments = 3
        bv.harden_normals = False
        smooth(ob)
        return ob

    front = [p for p in outline if p.y > -0.11]
    heel = [p for p in outline if p.y < -0.17]
    low_add(f'foot_{side}', slab(f'CW_BootSole_{side}', front, -0.05, 0.03))
    # chunky stacked heel: pushed out past the boot so it reads from the side and back
    hc = sum(heel, Vector()) / len(heel)
    heel = [hc + (p - hc) * 1.12 + Vector((0, -0.012, 0)) for p in heel]
    low_add(f'foot_{side}', slab(f'CW_BootHeel_{side}', heel, -0.06, 0.075, shrink=0.72))

    # seams: shin line, toe cap, back seam
    seam(f'CW_Seam_Shin_{side}', [(90, BOOT_TOP + 0.04), (90, 0.75), (90, 0.5)], 'cyl', bvh,
         n=40, center=(cx, cy), group=f'lowerleg_{side}')
    seam(f'CW_Seam_BootBack_{side}', [(270, BOOT_TOP - 0.02), (270, 0.7), (270, 0.42)], 'cyl', bvh,
         n=40, center=(cx, cy), group=f'lowerleg_{side}')
    seam(f'CW_Seam_ToeCap_{side}', [(fcx - 0.19, 0.16), (fcx - 0.12, 0.25), (fcx, 0.29),
                                    (fcx + 0.12, 0.25), (fcx + 0.19, 0.16)], 'top', fb, n=40,
         group=f'foot_{side}')

    # thigh: panel seams + two buckled straps
    ub = BVH[f'upperleg_{side}']; ul = SUIT[f'upperleg_{side}']
    uc = leg_center(ul, 1.5)
    out_a = 0 if s > 0 else 180
    seam(f'CW_Seam_ThighOut_{side}', [(out_a, 2.0), (out_a, 1.5), (out_a, 1.0)], 'cyl', ub,
         n=50, center=uc, group=f'upperleg_{side}')
    front_a = 68 if s > 0 else 112
    seam(f'CW_Seam_ThighFront_{side}', [(front_a, 2.02), (front_a + 6 * s, 1.6), (front_a + 14 * s, 1.15),
                                         (90, 1.0)], 'cyl', ub, n=50, center=uc, group=f'upperleg_{side}')
    for k, z in enumerate((1.74, 1.56)):
        strap(f'CW_Strap_Thigh{k}_{side}', side, s, ub, leg_center(ul, z), z, h=0.05,
              buckle_ang=15 if s > 0 else 165)

# hips: panel lines (front "brief" curve, sides, back)
hb = BVH['hips']
for s in (-1, 1):
    seam(f'CW_Seam_HipFront{s}', [(s * 0.44, 2.27), (s * 0.33, 2.17), (s * 0.2, 2.06), (s * 0.08, 1.99)],
         'front', hb, n=40, group='hips')
    seam(f'CW_Seam_HipBack{s}', [(s * 0.44, 2.27), (s * 0.3, 2.14), (s * 0.15, 2.03), (s * 0.06, 1.99)],
         'back', hb, n=40, group='hips')
seam('CW_Seam_HipBackC', [(0, 2.33), (0, 2.15), (0, 1.99)], 'back', hb, n=30, group='hips')

seams.update({g: join(obs, 'CW_Seams_' + g) for g, obs in SEAMS.items()})

# ========================================================= 8. finishing
for k, ob in SUIT.items():
    add_solidify(ob, 0.010, offset=-1.0)
    add_subsurf(ob, 1, 2)

# group per rig part & parent so the morph follows the rig parts
groups = {
    'torso': [torso, zipper, seams['torso'], collar, collar_trim, hem_trim],
}
for side in ('R', 'L'):
    groups[f'upperarm_{side}'] = [SUIT[f'upperarm_{side}']] + [o for o in strap_objs + metal_objs if f'UArm_{side}' in o.name]
    groups[f'lowerarm_{side}'] = [SUIT[f'lowerarm_{side}']] + [o for o in strap_objs + metal_objs if f'LArm_{side}' in o.name or f'GloveCuff_{side}' in o.name]
    groups[f'upperarm_{side}'].append(seams[f'upperarm_{side}'])
    groups[f'lowerarm_{side}'].append(seams[f'lowerarm_{side}'])
    groups[f'hand_{side}'] = [SUIT[f'hand_{side}'], seams[f'hand_{side}']] + [o for o in claw_objs if f'Claw_{side}' in o.name]
    for part in ('upperleg', 'lowerleg', 'foot'):
        k = f'{part}_{side}'
        groups[k] = [SUIT[k]] + LOW.get(k, []) + ([seams[k]] if k in seams else [])
    for o in coll.objects:
        bits = o.name.split('_')
        if o.name.startswith('CW_Strap_Thigh') and bits[3] == side:
            groups[f'upperleg_{side}'].append(o)
        elif o.name.startswith('CW_Strap_Ankle') and bits[3] == side:
            groups[f'lowerleg_{side}'].append(o)
groups['hips'] = [SUIT['hips'], seams['hips']] + LOW.get('hips', [])

# seams on the arms belong to the arm groups: split by name before parenting
for key, obs in groups.items():
    parent = bpy.data.objects[PARTS[key]]
    for ob in obs:
        if ob.parent: continue
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
        ob['morph_target'] = parent.name   # used by attach_to_rig.py

bpy.context.view_layer.update()
os.makedirs(OUT, exist_ok=True)
# 1) full rig + morph
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'Catwoman_Morph.blend'), compress=True)

# 2) morph pieces only (world space, unparented) to Append into your own rig file
for ob in coll.objects:
    mw = ob.matrix_world.copy(); ob.parent = None; ob.matrix_world = mw
keep = set(coll.objects)
for ob in list(bpy.data.objects):
    if ob not in keep:
        bpy.data.objects.remove(ob)
for c in list(bpy.data.collections):
    if c != coll:
        bpy.data.collections.remove(c)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'Catwoman_Morph_PiecesOnly.blend'),
                            compress=True)
print('SAVED')
