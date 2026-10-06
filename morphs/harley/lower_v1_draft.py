"""Harley lower-body v1 (shorts, belt, fishnets, sneakers).
Draft kept for the lower-body rework; it expects the helpers from
build_harley.py and is not runnable on its own."""
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

