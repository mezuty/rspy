"""morph_toolkit.py - procedural Roblox-morph building blocks for Blender (bpy).

Rig-agnostic helpers for building stylized clothing/armor "morphs" on top of a
segmented (R15-style) Roblox rig entirely from Python, then previewing them
with studio renders. Tested with the `bpy` 5.2 module (pip install bpy==5.2.*,
Python 3.13). Most of it also works on 4.x.

Conventions
-----------
* All geometry is built in WORLD space. Pieces are parented to the rig part
  they sit on at the end (keep-transform), see `parent_to_part`.
* Z is up. The rig's FRONT direction is configurable (`set_front`); detect it
  with `detect_front` - never assume it.
* "Shell" = a copy of a body part pushed outward along its normals: the base
  for any skin-tight garment (suit, sleeve, glove, boot).
* Details (seams, zippers, straps, trims) are placed by ray-casting onto the
  shell with a BVH tree, so they always sit exactly on the surface.

Never name your own script `inspect.py`, `types.py`, `random.py`, ...: it
shadows the Python stdlib and crashes bpy on import.
"""
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

UP = Vector((0, 0, 1))
FRONT = Vector((0, 1, 0))      # overwritten by set_front()
RIGHT = Vector((1, 0, 0))      # character's right = FRONT x UP
COLL = None                    # output collection


# ------------------------------------------------------------------ setup
def set_front(v):
    """Set the character's facing direction (horizontal unit vector)."""
    global FRONT, RIGHT
    FRONT = Vector(v).normalized()
    RIGHT = FRONT.cross(UP).normalized()


def new_collection(name):
    global COLL
    COLL = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(COLL)
    return COLL


def eval_world_verts(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg); me = e.to_mesh()
    vs = [ob.matrix_world @ v.co for v in me.vertices]
    e.to_mesh_clear()
    return vs


def world_bounds(ob):
    vs = eval_world_verts(ob)
    return (Vector([min(v[i] for v in vs) for i in range(3)]),
            Vector([max(v[i] for v in vs) for i in range(3)]))


def survey_rig(include_hidden=False):
    """Print every mesh with its world bounds, parent info, modifiers and
    materials. First thing to run on an unknown rig."""
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type != 'MESH': continue
        if not include_hidden and o.hide_render: continue
        mn, mx = world_bounds(o)
        print(f"{o.name:28s} min({mn.x:6.2f},{mn.y:6.2f},{mn.z:6.2f}) max({mx.x:6.2f},{mx.y:6.2f},{mx.z:6.2f})"
              f" parent={o.parent.name if o.parent else None} bone={o.parent_bone!r}"
              f" mods={[m.type for m in o.modifiers]} mats={[m.name for m in o.data.materials if m]}")


def slice_report(ob, n=12, axis_filter=None):
    """Cross-section extents along Z: the main way to 'see' a body part."""
    vs = eval_world_verts(ob)
    if axis_filter: vs = [v for v in vs if axis_filter(v)]
    z0 = min(v.z for v in vs); z1 = max(v.z for v in vs)
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        sl = [v for v in vs if abs(v.z - z) < (z1 - z0) / (2 * n)]
        if sl:
            print('  z=%.3f x[%.3f,%.3f] y[%.3f,%.3f]' % (z, min(v.x for v in sl), max(v.x for v in sl),
                                                        min(v.y for v in sl), max(v.y for v in sl)))


def detect_front(foot_obj, torso_obj=None):
    """Feet stick out towards the front: compare how far the foot extends past
    its own centre along +-X / +-Y. Returns a unit vector. Confirm visually
    with a render from that side (face texture, chest, toes)."""
    vs = eval_world_verts(foot_obj)
    c = sum(vs, Vector()) / len(vs)
    best, bestv = None, -1
    for d in (Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))):
        ext = max((v - c).dot(d) for v in vs)
        if ext > bestv: best, bestv = d, ext
    return best


# ------------------------------------------------------------------ materials
def principled(name, base, rough, metal=0.0, coat=0.0, coat_rough=0.1, spec=0.5, bump=None,
               emission=None):
    """Principled BSDF material. bump=(noise_scale, strength) adds fine grain
    (leather/fabric) without changing geometry."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Specular IOR Level'].default_value = spec
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = coat_rough
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[0], 1)
        p.inputs['Emission Strength'].default_value = emission[1]
    if bump:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = bump[0]; nz.inputs['Detail'].default_value = 6
        bp = nt.nodes.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = bump[1]; bp.inputs['Distance'].default_value = 0.002
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
        nt.links.new(bp.outputs['Normal'], p.inputs['Normal'])
    m.diffuse_color = (*base, 1); m.roughness = rough; m.metallic = metal   # solid-mode colours
    return m


# ------------------------------------------------------------------ objects
def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); COLL.objects.link(ob)
    if mat: me.materials.append(mat)
    return ob


def smooth(ob):
    for p in ob.data.polygons: p.use_smooth = True


def add_subsurf(ob, lv=1, rlv=None):
    """Keep viewport level == render level, or the user's viewport looks
    worse than your renders."""
    m = ob.modifiers.new('Subdivision', 'SUBSURF'); m.levels = lv; m.render_levels = rlv or lv
    return m


def add_solidify(ob, t, offset=-1.0, rim=True):
    """Thickness. NEVER use_even_offset=True on shells: degenerate faces shoot
    out long spikes."""
    m = ob.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = t; m.offset = offset; m.use_rim = rim
    m.use_even_offset = False; m.use_quality_normals = True
    return m


def add_bevel(ob, width, seg=2):
    m = ob.modifiers.new('Bevel', 'BEVEL'); m.width = width; m.segments = seg
    return m


def world_copy(src_name, new_name, level=None):
    """Copy a rig part's evaluated mesh into world space. `level` temporarily
    raises its Subdivision modifier so the copy is dense enough for folds and
    clean cuts (1 = light, 2 = good for folds, 3 = cut edges)."""
    src = bpy.data.objects[src_name]
    sub = next((m for m in src.modifiers if m.type == 'SUBSURF'), None)
    old = sub.levels if sub else None
    if sub and level is not None: sub.levels = level
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
    if sub and level is not None: sub.levels = old
    me.transform(src.matrix_world); me.materials.clear()
    ob = bpy.data.objects.new(new_name, me); COLL.objects.link(ob)
    return ob


def offset_shell(ob, dist):
    """Push every vertex out along its normal (merging split verts first so the
    shell doesn't tear at UV/normal seams)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    bm.normal_update()
    for v in bm.verts: v.co += v.normal * dist
    bm.to_mesh(ob.data); bm.free()


def smooth_region(ob, weight_fn, iters=60):
    """Laplacian relax where weight_fn(co)->0..1 > 0. Use it so fabric bridges
    body dents (navel, spine groove, armpit creases) instead of following them.
    Measure the dent's real position first - a wrong centre does nothing."""
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


def fill_pits(ob, weight_fn, push_dir, iters=60):
    """Fill-only relax: move vertices toward their neighbours' average but
    only OUTWARD along push_dir. Removes pits and grooves where fabric should
    span a gap (top of the cleavage, small body dents) without the shrinkage a
    normal Laplacian smooth causes (which re-digs the groove you just bridged)."""
    d = Vector(push_dir).normalized()
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for _ in range(iters):
        moves = {}
        for v in bm.verts:
            w = weight_fn(v.co)
            if w <= 0 or not v.link_edges: continue
            avg = sum((e.other_vert(v).co for e in v.link_edges), Vector()) / len(v.link_edges)
            gain = (avg - v.co).dot(d)
            if gain > 0: moves[v] = d * gain * 0.6 * w
        for v, m in moves.items(): v.co += m
    bm.to_mesh(ob.data); bm.free()


def add_folds(ob, center, radii, axis, amp, wavelength, face_dir=None, min_dot=0.0, sharp=1.6,
              wobble=0.12):
    """Stylized cloth folds: soft ridges across `axis` inside an ellipsoid
    (radii along x,y,z), pushed out along normals. Keep wobble/sharp low -
    high values look crumpled, not stylized. Needs a dense mesh (level>=2)."""
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    axis = Vector(axis).normalized(); c = Vector(center)
    fd = Vector(face_dir).normalized() if face_dir else None
    for v in bm.verts:
        d = v.co - c
        q = (d.x / radii[0]) ** 2 + (d.y / radii[1]) ** 2 + (d.z / radii[2]) ** 2
        if q >= 1: continue
        w = (1 - q) ** 2
        if fd is not None:
            k = v.normal.dot(fd)
            if k <= min_dot: continue
            w *= min(1.0, (k - min_dot) / 0.3)
        a = d.dot(axis) / wavelength + wobble * math.sin(d.x * 4.0 + d.y * 5.0)
        ridge = (1 - abs(math.sin(math.pi * a))) ** sharp
        v.co += v.normal * (amp * w * (ridge - 0.2))
    bm.to_mesh(ob.data); bm.free()


def cut_opening(ob, planes, inside_fn, snap_fn=None):
    """Cut a clean opening (V-neck, keyhole, cut-out...): bisect along each
    (plane_co, plane_no) so the edge follows the plane exactly, then delete
    faces whose centre satisfies inside_fn(c). snap_fn(v) may move boundary
    verts onto an exact curve afterwards (for curved cuts)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for co, no in planes:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    dead = [f for f in bm.faces if inside_fn(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    if snap_fn:
        for v in bm.verts:
            if v.is_boundary: snap_fn(v)
    bm.to_mesh(ob.data); bm.free()


def slice_center(ob, z):
    """Centre (x, y) of a mesh's cross-section at height z (world-space mesh)."""
    tol = 0.02; vs = []
    while not vs:
        vs = [v.co for v in ob.data.vertices if abs(v.co.z - z) < tol]; tol *= 2
    xs = [v.x for v in vs]; ys = [v.y for v in vs]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


# ------------------------------------------------------------------ surface projection
def bvh_of(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


def outer_hit(bvhs, o, d):
    """Nearest hit over several surfaces (belts crossing torso + hips + legs)."""
    best = None
    for b in bvhs:
        h = b.ray_cast(o, d)
        if h[0] is not None and (best is None or h[3] < best[3]): best = h
    return best


def catmull(pts, n):
    """Smooth curve through control points (2D or 3D), n samples."""
    pts = [Vector(p) for p in pts]
    P = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    out = []; segs = len(pts) - 1
    for i in range(n):
        t = i / (n - 1) * segs; k = min(int(t), segs - 1); u = t - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u))
    return out


def project(bvh, pts2d, mode, center=(0.0, 0.0)):
    """Drop 2D design points onto a surface -> list of (co, normal).
      'front' : (s, z) s along the character's RIGHT axis, ray from the front
      'back'  : (s, z) ray from behind
      'right'/'left' : (f, z) f along FRONT, ray from that side
      'top'   : (x, y) ray straight down
      'cyl'   : (angle_deg, z) radial ray towards `center` (x, y); angle 0 = RIGHT,
                90 = FRONT. Best for limbs and anything wrapping around."""
    res = []
    for p in pts2d:
        if mode == 'front':
            o = RIGHT * p[0] + FRONT * 5 + UP * p[1]; d = -FRONT
        elif mode == 'back':
            o = RIGHT * p[0] - FRONT * 5 + UP * p[1]; d = FRONT.copy()
        elif mode in ('right', 'left'):
            s = 1 if mode == 'right' else -1
            o = FRONT * p[0] + RIGHT * 5 * s + UP * p[1]; d = -RIGHT * s
        elif mode == 'top':
            o = Vector((p[0], p[1], 50)); d = -UP
        else:
            a = math.radians(p[0])
            r = RIGHT * math.cos(a) + FRONT * math.sin(a)
            o = Vector((center[0], center[1], p[1])) + r * 5; d = -r
        hit, n, _, _ = bvh.ray_cast(o, d)
        if hit is not None: res.append((hit, n))
    return res


def resample(path, step):
    """Re-space a (co, n) path at constant arc length (zipper teeth, stitches)."""
    out = [path[0]]; acc = 0.0
    for a, b in zip(path, path[1:]):
        seg = (b[0] - a[0]).length
        if seg < 1e-9: continue
        acc += seg
        while acc >= step:
            acc -= step; f = 1 - acc / seg
            out.append((a[0].lerp(b[0], f), a[1].lerp(b[1], f).normalized()))
    return out


def frame_at(co, n, tangent_hint):
    n = n.normalized(); t = (tangent_hint - n * tangent_hint.dot(n)).normalized()
    return t, n.cross(t), n


def parallel_frames(pts):
    """Twist-free tangent/normal/binormal frames along a polyline."""
    T = [(pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(len(pts))]
    ref = UP if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [(ref - T[0] * ref.dot(T[0])).normalized()]
    for i in range(1, len(pts)):
        n = N[-1] - T[i] * N[-1].dot(T[i]); N.append(n.normalized() if n.length > 1e-8 else N[-1])
    return T, N, [t.cross(n) for t, n in zip(T, N)]


# ------------------------------------------------------------------ primitives
def box(bm, center, t, b, n, sx, sy, sz):
    """Oriented box (half sizes) appended to a bmesh: zipper teeth, stitches, tabs."""
    vs = [bm.verts.new(center + t * sx * i + b * sy * j + n * sz * k)
          for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]
    for f in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]:
        bm.faces.new([vs[i] for i in f])


def curve_tube(name, pts, radius, mat, res=3, caps=True, radii=None):
    """Tube along points (piping, trims, rings, cords). radii = per-point scale
    for tapering. Convert with to_mesh() before export."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
        if radii: sp.points[i].radius = radii[i]
    cu.bevel_depth = radius; cu.bevel_resolution = res; cu.use_fill_caps = caps
    ob = bpy.data.objects.new(name, cu); COLL.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def to_mesh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    name = ob.name; mats = list(ob.data.materials)
    bpy.data.objects.remove(ob)
    new = bpy.data.objects.new(name, me); COLL.objects.link(new)
    if not me.materials:
        for m in mats: me.materials.append(m)
    smooth(new)
    return new


def tube(name, pts, radius, mat, **kw):
    return to_mesh(curve_tube(name, pts, radius, mat, **kw))


def join(obs, name):
    obs = [o for o in obs if o]
    with bpy.context.temp_override(active_object=obs[0], selected_editable_objects=obs,
                                   selected_objects=obs):
        bpy.ops.object.join()
    obs[0].name = name
    return obs[0]


def ribbon(name, path, width, lift, thick, mat):
    """Flat strip following a surface path (zipper tape, straps, belts on a
    path, ties)."""
    bm = bmesh.new(); rows = []
    for i, (co, n) in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)][0] - path[max(i - 1, 0)][0]).normalized()
        b = n.cross(t).normalized(); c = co + n * lift
        rows.append((bm.verts.new(c - b * width / 2), bm.verts.new(c + b * width / 2)))
    for r0, r1 in zip(rows, rows[1:]):
        bm.faces.new((r0[0], r0[1], r1[1], r1[0]))
    ob = mesh_obj(name, bm, mat); add_solidify(ob, thick, offset=1.0); smooth(ob)
    return ob


def rounded_rect(c, t, b, w, h, k=0.45, n=40):
    """Superellipse outline (buckles, plates, frames). k<1 = squarer."""
    pts = []
    for i in range(n + 1):
        u = 2 * math.pi * i / n
        pts.append(c + t * math.copysign(abs(math.cos(u)) ** k, math.cos(u)) * w
                   + b * math.copysign(abs(math.sin(u)) ** k, math.sin(u)) * h)
    return pts


# ------------------------------------------------------------------ details
def seam(name, ctrl2d, mode, bvh, mats, n=70, center=(0, 0), r=0.0048, stitch=True,
         stitch_gap=0.0125, stitch_len=0.013):
    """Raised piping + dashed stitching on both sides. mats=(piping, stitch).
    Returns list of objects. The single most effective 'premium' detail."""
    p = project(bvh, catmull(ctrl2d, n), mode, center)
    if len(p) < 3: return []
    out = [tube(name, [co + nn * 0.0015 for co, nn in p], r, mats[0])]
    if stitch:
        bm = bmesh.new(); rs = resample(p, stitch_len * 1.85)
        for i in range(1, len(rs) - 1):
            co, nn = rs[i]
            t, b, nn = frame_at(co, nn, (rs[i + 1][0] - rs[i - 1][0]).normalized())
            for sgn in (-1, 1):
                box(bm, co + nn * 0.0012 + b * stitch_gap * sgn, t, b, nn, stitch_len / 2, 0.0012, 0.0012)
        out.append(mesh_obj(name + '_stitch', bm, mats[1]))
    return out


def zipper(name, path, tape_mat, metal_mat, tape_w=0.034, open_side=None):
    """Zipper along a (co, n) path: tape + alternating metal teeth. With
    open_side=+1/-1 the teeth sit on one edge only (an unzipped half)."""
    path = resample(path, 0.0125)
    out = [ribbon(name + '_Tape', path, tape_w, 0.0015, 0.003, tape_mat)]
    bm = bmesh.new()
    for i, (co, n) in enumerate(path[1:-1]):
        t, b, n = frame_at(co, n, (path[-1][0] - path[0][0]).normalized())
        if open_side is None:
            box(bm, co + n * 0.0045 + b * (0.0035 if i % 2 else -0.0035), t, b, n, 0.0042, 0.0085, 0.0028)
        else:
            box(bm, co + n * 0.0045 + b * 0.009 * open_side, t, b, n, 0.0042, 0.0055, 0.0028)
    out.append(mesh_obj(name + '_Teeth', bm, metal_mat))
    return out


def zipper_pull(name, co, n, down, metal_mat):
    """Slider + hanging loop tab at a zipper end."""
    t, b, n = frame_at(co, n, down)
    bm = bmesh.new(); box(bm, co + n * 0.012, t, b, n, 0.026, 0.017, 0.0075)
    sl = mesh_obj(name + '_Slider', bm, metal_mat); add_bevel(sl, 0.005, 3)
    c = co + n * 0.02 + t * 0.055
    loop = [c + t * math.cos(2 * math.pi * i / 24) * 0.038 + b * math.sin(2 * math.pi * i / 24) * 0.016
            for i in range(25)]
    return [sl, tube(name + '_Pull', loop, 0.0055, metal_mat)]


def band_ring(name, bvh, center_xy, z, h, lift, thick, mat, nseg=48, z_fn=None):
    """A strap/cuff wrapping a limb or torso at height z (or z_fn(angle_deg))
    found by radial ray casts. Returns the object."""
    bm = bmesh.new(); rows = []
    for i in range(nseg):
        a = 360.0 * i / nseg
        r = RIGHT * math.cos(math.radians(a)) + FRONT * math.sin(math.radians(a))
        zz = z_fn(a) if z_fn else z
        row = []
        for dz in (-h / 2, h / 2):
            hit, n, _, _ = bvh.ray_cast(Vector((center_xy[0], center_xy[1], zz + dz)) + r * 5, -r)
            row.append(bm.verts.new(hit + n * lift))
        rows.append(row)
    for i in range(nseg):
        r0, r1 = rows[i], rows[(i + 1) % nseg]
        bm.faces.new((r0[0], r1[0], r1[1], r0[1]))
    ob = mesh_obj(name, bm, mat); add_solidify(ob, thick, offset=1.0); smooth(ob)
    return ob


def buckle(name, bvh, center_xy, z, angle_deg, strap_h, metal_mat, strap_mat, lift=0.006, strap_t=0.014):
    """Rounded-rect buckle frame + bar + prong + tucked strap tail, placed on a
    band at angle_deg (0 = character's right, 90 = front)."""
    r = RIGHT * math.cos(math.radians(angle_deg)) + FRONT * math.sin(math.radians(angle_deg))
    hit, n, _, _ = bvh.ray_cast(Vector((center_xy[0], center_xy[1], z)) + r * 5, -r)
    t = UP.cross(n).normalized()
    c = hit + n * (lift + strap_t + 0.002)
    w, hh = strap_h * 0.8, strap_h
    out = [tube(name + '_Frame', rounded_rect(c, t, UP, w, hh), 0.0068, metal_mat),
           tube(name + '_Bar', [c - t * 0.004 - UP * hh, c - t * 0.004 + UP * hh], 0.0045, metal_mat),
           tube(name + '_Prong', [c - t * 0.004 + n * 0.003, c + t * w * 0.85 + n * 0.004], 0.003, metal_mat)]
    bm = bmesh.new(); box(bm, c + t * (w + 0.03) - n * 0.004, t, UP, n, 0.035, strap_h * 0.42, 0.005)
    tail = mesh_obj(name + '_Tail', bm, strap_mat); add_bevel(tail, 0.004, 2)
    return out + [tail]


def braid(name, path, strand_r, braid_r, period, mat, scale_fn=None, strands=3):
    """Braided cord / whip / rope along a 3D polyline: `strands` helical tubes
    + a core. scale_fn(f in 0..1) tapers it. Use dense paths (>= 8 pts per period)."""
    L = [0.0]
    for a, b in zip(path, path[1:]): L.append(L[-1] + (b - a).length)
    total = L[-1]; T, N, B = parallel_frames(path)
    sc = [scale_fn(l / total) if scale_fn else 1.0 for l in L]
    out = []
    for k in range(strands):
        pts = []
        for i, p in enumerate(path):
            ph = 2 * math.pi * L[i] / period + 2 * math.pi * k / strands
            pts.append(p + (N[i] * math.cos(ph) + B[i] * math.sin(ph)) * braid_r * sc[i])
        out.append(tube(f'{name}_Strand{k}', pts, strand_r, mat, res=1, radii=sc))
    out.append(tube(f'{name}_Core', path, strand_r * 1.15, mat, res=2, radii=sc))
    return out


def claw(name, base, direction, normal, mat, length=0.085, radius=0.02, hook=0.45):
    """Hooked tapered claw/spike/horn: ring sweep along a bent path.
    hook=0 gives a straight cone (studs, bracelet spikes)."""
    d = direction.normalized(); nrm = (normal - d * normal.dot(d)).normalized()
    bm = bmesh.new(); rings = []; seg = 10
    for i in range(11):
        f = i / 10
        p = base + d * (length * f) - nrm * (length * hook * f * f)
        tang = (d - nrm * (2 * hook * f)).normalized()
        nn = (nrm - tang * nrm.dot(tang)).normalized(); ss = tang.cross(nn)
        rad = radius * (1 - f) ** 0.8 + 0.0008
        rings.append([bm.verts.new(p + nn * math.cos(2 * math.pi * k / seg) * rad * 0.75
                                   + ss * math.sin(2 * math.pi * k / seg) * rad) for k in range(seg)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k]))
    bm.faces.new(rings[0][::-1])
    tip = bm.verts.new(rings[-1][0].co.lerp(rings[-1][seg // 2].co, 0.5) + (rings[-1][0].co - rings[-2][0].co) * 0.3)
    for k in range(seg):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], tip))
    ob = mesh_obj(name, bm, mat); smooth(ob)
    return ob


def slab(name, outline, z0, z1, mat, shrink=1.0, bevel=0.009):
    """Extrude a closed horizontal outline (soles, heels, plates, bases).
    shrink<1 tapers the bottom."""
    cen = sum(outline, Vector()) / len(outline)
    bm = bmesh.new()
    top = [bm.verts.new((p.x, p.y, z1)) for p in outline]
    bot = [bm.verts.new(Vector(((cen + (p - cen) * shrink).x, (cen + (p - cen) * shrink).y, z0))) for p in outline]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(len(outline)):
        j = (i + 1) % len(outline); bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_obj(name, bm, mat); add_bevel(ob, bevel, 3); smooth(ob)
    return ob


def outline_at(bvh, center_xy, z, grow=0.012, n=64):
    """Horizontal outline of a surface at height z (radial ray casts), pushed
    out by `grow` - e.g. the footprint for a sole."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = Vector((math.cos(a), math.sin(a), 0))
        hit, nn, _, _ = bvh.ray_cast(Vector((center_xy[0], center_xy[1], z)) + r * 5, -r)
        if hit: pts.append(Vector((hit.x, hit.y, 0)) + Vector((nn.x, nn.y, 0)).normalized() * grow)
    return pts


# ------------------------------------------------------------------ rig hookup + delivery
def parent_to_part(ob, part_name):
    """Parent keep-transform and remember the target so pieces can be
    re-attached after appending into another file."""
    parent = bpy.data.objects[part_name]
    ob.parent = parent; ob.matrix_parent_inverse = parent.matrix_world.inverted()
    ob['morph_target'] = part_name


def add_studio_look(sc=None, target_z=2.5):
    """Grey world + soft area lights placed relative to FRONT, EEVEE engine,
    and every 3D viewport set to Material Preview USING the scene lights and
    world. Without this the user's viewport uses Blender's outdoor HDRI and
    glossy materials look blotchy/washed out compared to your renders."""
    sc = sc or bpy.context.scene
    w = bpy.data.worlds.get('Morph_Studio_World') or bpy.data.worlds.new('Morph_Studio_World')
    sc.world = w; nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg is None:
        bg = nt.nodes.new('ShaderNodeBackground')
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None) or nt.nodes.new('ShaderNodeOutputWorld')
        nt.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[0].default_value = (0.045, 0.045, 0.045, 1); bg.inputs[1].default_value = 1.0
    sc.view_settings.view_transform = 'AgX'
    if 'Morph Studio Lights' not in bpy.data.collections:
        lc = bpy.data.collections.new('Morph Studio Lights'); sc.collection.children.link(lc)
        side = RIGHT
        for name, e, loc, size in (('Key', 1000, -side * 3.5 + FRONT * 5 + UP * 6, 4),
                                   ('Fill', 450, side * 4.5 + FRONT * 4 + UP * 3, 5),
                                   ('Rim', 750, side * 1.5 - FRONT * 5 + UP * 5, 3),
                                   ('Rim2', 400, -side * 3 - FRONT * 4 + UP * 2, 3),
                                   ('Top', 250, FRONT * 1 + UP * 8, 4),
                                   ('Low', 200, FRONT * 5 + UP * 0.3, 4)):
            ld = bpy.data.lights.new('Morph_' + name, 'AREA'); ld.energy = e; ld.size = size
            o = bpy.data.objects.new('Morph_' + name, ld); lc.objects.link(o)
            o.location = loc
            o.rotation_euler = (Vector((0, 0, target_z)) - o.location).to_track_quat('-Z', 'Y').to_euler()
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: sc.render.engine = eng; break
        except TypeError: pass
    if hasattr(sc.eevee, 'use_raytracing'): sc.eevee.use_raytracing = True
    for scr in bpy.data.screens:
        for area in scr.areas:
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sh = sp.shading; sh.type = 'MATERIAL'
                    sh.use_scene_lights = sh.use_scene_world = True
                    sh.use_scene_lights_render = sh.use_scene_world_render = True


def render_view(path, loc, target, lens=55, res=(800, 1000), samples=48):
    """Cycles CPU still (works headless with no GPU). Camera looks at target."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    cam = bpy.data.objects.get('_cam') or bpy.data.objects.new('_cam', bpy.data.cameras.new('_cam'))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.data.lens = lens; cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def save_deliverables(out_dir, base_name):
    """1) full rig + morph   2) morph pieces only (unparented, world space)."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    cam = bpy.data.objects.get('_cam')
    if cam: bpy.data.objects.remove(cam)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, base_name + '.blend'), compress=True)
    for ob in COLL.objects:
        mw = ob.matrix_world.copy(); ob.parent = None; ob.matrix_world = mw
    keep = set(COLL.objects)
    for ob in list(bpy.data.objects):
        if ob not in keep: bpy.data.objects.remove(ob)
    for c in list(bpy.data.collections):
        if c != COLL: bpy.data.collections.remove(c)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, base_name + '_PiecesOnly.blend'), compress=True)


def qa_report(expected_openings=None, ground_z=None, far=12.0):
    """Automated checks before showing the user anything. Prints and returns a
    list of problems:
      * pieces with no parent (won't follow the rig);
      * leftover temporary objects (names starting with '_');
      * open boundary loops on each mesh that aren't in expected_openings
        (a dict {object_name: [(x, y, z), ...]} of loop centres you meant to
        cut: necklines, hems, tears...). Catches accidental holes;
      * geometry far below ground_z (soles are expected slightly below);
      * stray geometry far from the rig (failed ray casts dump points at origin
        or 5 units out)."""
    problems = []
    expected_openings = expected_openings or {}
    for ob in COLL.objects:
        if ob.parent is None:
            problems.append(f'unparented: {ob.name}')
    for ob in bpy.data.objects:
        if ob.name.startswith('_') and ob.type == 'MESH':
            problems.append(f'temporary object left behind: {ob.name}')
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in COLL.objects:
        if ob.type != 'MESH': continue
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
        if ground_z is not None or far:
            for v in bm.verts:
                if ground_z is not None and v.co.z < ground_z - 0.1:
                    problems.append(f'{ob.name}: geometry far below ground (z={v.co.z:.2f})'); break
                if far and (abs(v.co.x) > far or abs(v.co.y) > far):
                    problems.append(f'{ob.name}: stray geometry at {tuple(round(c, 2) for c in v.co)}'); break
        if ob.name in expected_openings or any(m.type in ('SOLIDIFY', 'SUBSURF') for m in ob.modifiers):
            adj = {}
            for e in bm.edges:
                if e.is_boundary:
                    a, b = e.verts
                    adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
            seen = set()
            for v in adj:
                if v in seen: continue
                stack, comp = [v], []
                while stack:
                    x = stack.pop()
                    if x in seen: continue
                    seen.add(x); comp.append(x); stack += adj[x]
                c = sum((x.co for x in comp), Vector()) / len(comp)
                exp = expected_openings.get(ob.name)
                if exp is not None and not any((c - Vector(e)).length < 0.08 for e in exp):
                    problems.append(f'{ob.name}: unexpected opening near {tuple(round(q, 3) for q in c)} ({len(comp)} verts)')
        bm.free()
    print('QA:', 'OK' if not problems else '\n  ' + '\n  '.join(problems))
    return problems


ATTACH_SCRIPT = '''import bpy
# Run in Blender's Text Editor after appending the morph collection.
COLL_NAME = "{coll}"
for ob in bpy.data.collections[COLL_NAME].objects:
    target = bpy.data.objects.get(ob.get("morph_target", ""))
    if target is None:
        print("no target for", ob.name); continue
    mw = ob.matrix_world.copy()
    ob.parent = target
    ob.matrix_parent_inverse = target.matrix_world.inverted()
    ob.matrix_world = mw
print("morph attached")
'''
