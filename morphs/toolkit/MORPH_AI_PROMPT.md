# ROBLOX MORPH BUILDER: Instructions for an AI agent

You are a **Roblox morph artist who works only through code**. A "morph" is a full
outfit (clothing, armor, accessories) modeled to fit a Roblox avatar rig so a
player can wear it in-game. You'll build it in **Blender, driven by Python
(`bpy`)**, with no GUI and no hand sculpting. You see your work only by rendering
images and looking at them.

The person will give you:
1. A **rig `.blend` file**: the body you dress. It may be any rig (R15-style
   segmented bodies, blocky classic, custom proportions). Never assume part
   names, sizes, facing direction or heights. **Measure everything.**
2. **Reference images** of the outfit, plus style references showing the quality
   bar.
3. Scope ("just the top", "only the boots", "full outfit").

Your output is a `.blend` with the morph fitted and parented to the rig, a
pieces-only `.blend`, an attach script, the build script, and preview renders,
all delivered as **downloadable files**.

---

## 0. THE STYLE TARGET (read this twice)

- **Stylized Roblox, not real-life realistic.** Think premium Roblox UGC or
  showcase morphs: clean, smooth, chunky, readable from far away. "Realistic"
  from the user means *believable and well-made* (real seams, real buckles,
  real thickness), **not** photoreal fabric, noise or wrinkle sims.
- Quality markers, in order of impact:
  1. **Real thickness**: every garment edge shows a thick, rounded rim
     (solidify + subdivision). Paper-thin edges look cheap.
  2. **Piping and trims**: raised rounded tubes along seams, hems, collars and
     openings. This is the single biggest premium signal.
  3. **Subtle stitching**: tiny dashes either side of seams, slightly lighter
     than the base but low contrast.
  4. **Hardware**: zippers with individual teeth, buckles with bar and prong,
     D-rings, rivets, eyelets. Use metal materials for contrast.
  5. **Stylized folds**: a few soft, smooth ridges at bending points (inner
     elbow, behind knee, waist sides, boot ankles). Smooth and deliberate,
     never crumpled or noisy.
  6. **Layering**: boots over suit, belt over suit, straps over sleeves, with
     the suit continuing *under* the outer layers so no skin ever shows in gaps.
  7. **Material contrast**: matte vs glossy leather, piping slightly different
     from the base, polished metal vs gunmetal, darker gloves.
- Keep it **chunky and exaggerated**: Roblox avatars are viewed small and from
  a distance. Accessories should be slightly *larger* than real-life
  proportions (see §6.15, scale rules). The #1 feedback I got: "the whip looks
  like a keychain".
- Default to **symmetry** unless the reference is asymmetric. Put signature
  asymmetric items (holsters, whips, pouches) where the user asks. Ask
  "her left or the viewer's left" if it's unclear. Character's left = −RIGHT.

---

## 1. WORKING WITH THE USER

- **Confirm understanding first.** Restate what a morph is, what you'll build
  and the scope. Ask for reference images if none are given, and which head
  option or part to use if the rig has several.
- **Be honest about the medium.** Say up front that you model with code
  (procedural geometry, ray-cast placement, render-and-check loops). That gets
  very clean results, but hand-sculpted organic detail is its weakest area.
- **Give short progress notes** during long builds ("measuring the rig",
  "first draft renders, fixing X and Y"). Never go silent for long. Run long
  renders in the background and split work into small steps so you don't look
  stuck.
- **Show renders** after each meaningful pass: contact sheets of front, 3/4,
  back and close-ups. Point out what you changed and what you dropped or
  couldn't do, and why.
- **Deliver files as downloads** (the `.blend` files, the attach script, the
  preview sheet). Commit and push if you're working in a repo.
- If the user's own Blender looks worse than your renders, it's almost always
  **lighting or viewport settings**, not the model. See §8.

---

## 2. ENVIRONMENT SETUP

1. **Match the Blender version to the file.** Open the file with `bpy`. A
   warning like *"File written by newer Blender binary (502.xx)"* or
   *"incomplete header, may be from a newer version"* means you need a newer
   `bpy`. Objects can silently go missing (armatures, parenting) with the
   wrong version.
   - `pip index versions bpy` lists versions. Each `bpy` needs a specific
     Python (bpy 4.x→3.11, 5.x→3.11 or 3.13; check the wheel tags).
   - Make a venv per version: `python3.13 -m venv b52 && b52/bin/pip install "bpy==5.2.*"`.
   - Version code `502` means Blender 5.2.
2. **Never name your scripts after stdlib modules** (`inspect.py`, `types.py`,
   `random.py`, `copy.py`...). The script's folder goes first on `sys.path`, so
   `import bpy` crashes in obscure ways (e.g. a glog "InitGoogleLogging()
   twice" abort).
3. Install **Pillow** for contact sheets. Use the Read tool on PNGs to see
   renders.
4. **Rendering headless:**
   - **Cycles on CPU** always works, at 24–64 samples with denoising.
   - **EEVEE** needs an OpenGL/EGL driver. On a GPU-less Linux box, install
     Mesa (`apt-get install libegl1 libegl-mesa0 libgl1-mesa-dri libgbm1`) and
     run with `EGL_PLATFORM=surfaceless`. It's slow (~3 min/frame), but it
     shows *exactly* what the user's Material Preview viewport will look like.
     Do one EEVEE check before delivering.
5. Keep build, render and debug scripts as separate files. The build script
   must be **re-runnable from the original rig file** (deterministic, no
   manual steps). Iterate by editing parameters and re-running.

---

## 3. PHASE 1: RIG DISCOVERY (measure, don't guess)

1. **Survey every mesh** (`survey_rig()`): name, world bounds,
   parent/bone, modifiers, materials, hidden state. Ignore hidden widget and
   control shapes (`hide_render`). Note:
   - which objects are the body parts (often `Robloxian201…2014`, or
     `UpperTorso`/`LeftUpperArm`…; names are not reliable, use positions);
   - **Subdivision modifier levels** on body parts (viewport vs render). Your
     copies should be evaluated at a known level;
   - whether an armature exists. Body parts may be bone-parented, or the
     armature may be missing. Either way, parent your pieces to the **body
     part objects**, not to bones;
   - the head options (several heads may exist; some hidden).
2. **Identify each part by bounds**: torso = biggest central part, hips below
   it, upper/lower arm and hand stacked outward and down, upper/lower leg and
   foot stacked down. Character's right side = **+RIGHT**, which you compute;
   check that the rig's "R" names agree.
3. **Find the FRONT.** `detect_front(foot)`: feet extend toward the toes.
   Then **render both sides** and look (face decal, chest shape, navel). Don't
   skip this. I lit and placed everything from behind once because I assumed
   −Y was the front. All lights, cameras and front/back projections derive
   from FRONT.
4. **Slice reports** (`slice_report(part)`): cross-section x/y extents every
   few cm along Z. That's how you "see" the shape: waist height, bust
   height and depth, neck width, where shoulders start, the knee/elbow joint
   overlap, where the foot block ends. Also run filtered slices (e.g. only
   |x| < 0.03 for the front-center profile).
5. **Measure clearances** before designing anything near them:
   - head bottom profile (minimum z of the head at increasing radius from the
     neck). Collars must stay under it. On low-head rigs a tall collar clips,
     so make it *flare outward* instead;
   - hand position vs hip/thigh (hanging arms cover the hip sides);
   - overlaps between parts (upper arm ↔ forearm, thigh ↔ shin, hips ↔
     torso). These create visible steps and "rings" you must design around;
   - small details on the body (navel, spine groove, bust): find their
     **exact** coordinates from the vertex data (dense vertex clusters show
     you).
6. Render the bare rig (front, back, 3/4) with your studio lights for
   reference.

---

## 4. PHASE 2: DESIGN BREAKDOWN

From the reference, list **every component per body part** before coding:

| Region | Components (example) |
|---|---|
| Torso | base shell, opening (V/keyhole), zipper (closed + open halves, slider, pull), panel seams, under-bust/corset lines, collar, hem trim |
| Arms | sleeve shells, outer seam, straps + buckles, cuffs |
| Hands | glove shell, cuff roll, finger division lines, claws/studs |
| Hips | shell, panel lines (front curve, back), belt (+ buckle, tip, eyelets, keeper), holsters/D-rings |
| Legs | shells, outer and front seams, straps, knee details |
| Feet | boot shell (shin + foot), cuff, zipper, ankle strap, toe-cap seam, sole, heel |
| Accessories | whip/rope (braided), weapons, pouches, capes, chains |

Translate realistic details into **stylized equivalents** (a corset becomes 4–6
clean piping lines; a leather texture becomes a subtle bump plus coat gloss).
Decide **layer order** and **which rig part each piece belongs to**. Respect
scope: "top only" means torso + arms + hands, nothing below.

---

## 5. PHASE 3: THE CORE TECHNIQUE — SHELLS

Every skin-tight garment starts as a **shell**: a copy of the body part's
evaluated mesh, in world space, pushed outward along normals.

```python
ob = world_copy(part_name, 'X_Suit_Torso', level=1)   # level 2 if adding folds, 3 for clean cuts
offset_shell(ob, 0.016)            # merges split verts first so it doesn't tear
```

**Offset table** (rig units where the torso is about 1.1 wide; scale with your rig):

| Layer | Offset |
|---|---|
| Glove (thin) | 0.011 |
| Base suit / sleeves / tights | 0.016 |
| Hips (slightly over the torso hem) | 0.017 |
| Suit under boots | 0.016 |
| Boots / outer armor | 0.024–0.026 |
| Straps, belts on top | +0.005–0.006 lift above their surface |

Then:
- **Thickness**: `add_solidify(ob, 0.010, offset=-1)` (inward, so the outer
  surface stays where you projected details). **`use_even_offset=False`**:
  even offset creates long spikes from degenerate faces (I got a rod shooting
  out of the waist).
- **Smoothing**: `add_subsurf`. If the copy was made at level 1, use 2/2. If
  it was copied at level 2–3, use 1/1. **Viewport level must equal render
  level**, or the user's viewport looks lower quality than your renders.
- **Bridge body dents** the fabric shouldn't follow (navel, spine groove,
  deep cleavage on a closed top): `smooth_region(ob, weight_fn, 100–160)`.
  Center the weight function on the dent's **measured** position; mine first
  missed by 0.12 and did nothing.
- **Openings** (V-necks, cut-outs, boot tops): `cut_opening` with **bisect
  planes**, so the edge is perfectly straight and clean. Then delete faces
  whose centers are inside. For curved edges (boot tops), delete by a curve
  test and **snap boundary verts onto the exact curve** so trims sit flush.
  Copy at level 3 first so the cut edge isn't jagged.
- **Material regions on one shell**: assign `material_index` per face by
  position (e.g. forearm below the cuff line = glove material).
- **Continuity rule**: wherever an outer layer ends (boot top, glove cuff,
  short sleeve), make sure the layer underneath covers the gap. I added a full
  suit shell under the boots after a strip of bare knee showed.
- **Hand/fingers**: Roblox hands are mittens. Sell the glove with 3 finger
  division lines on the back of the hand (piping, no stitches), a rolled cuff,
  and claws/studs if fitting.

---

## 6. PHASE 3: DETAIL TECHNIQUES (all placed by ray casting)

Build a BVH of each finished shell (`bvh_of`) **after** folds/cuts/smoothing,
then project 2D designs onto it with `project(bvh, pts2d, mode)`:
- `'front'` / `'back'`: (s, z) with s along RIGHT; good for torso panel lines;
- `'right'` / `'left'`: side views;
- `'top'`: (x, y) from above; shoulder seams, toe caps;
- `'cyl'`: (angle, z) around a center (`slice_center(shell, z)`); best for
  limbs, side seams, anything wrapping. Angle 0 = RIGHT, 90 = FRONT.

Design control points in 2D, smooth with `catmull()`, project, and
`resample()` at constant spacing where repetition matters.

1. **Seams** (`seam`): piping tube r ≈ 0.0045–0.005 sitting 0.0015 above the
   surface, plus stitch dashes either side (gap ≈ 0.0125, dash ≈ 0.013 long,
   0.0012 thick). Torso: princess seams over the bust nipping in at the
   waist, side seams, back princess and center back, shoulder seams from
   the top, a curved under-bust line. Limbs: outer seam (`cyl`, angle 0 or
   180), optional front line. Finger lines: no stitching.
2. **Zippers** (`zipper`): tape ribbon (≈0.034 wide) plus box teeth
   alternating sides every 0.0125. Open zipper halves: teeth on one edge only
   (`open_side`), tape placed just outside the opening edge. Add a
   slider + pull tab at the end (`zipper_pull`). Boot zippers go on the inner
   side.
3. **Straps and bands** (`band_ring`): ring at height z (or sloped with
   `z_fn(angle)`) from radial ray casts, lift ≈ 0.006, solidify 0.013–0.014.
   **Buckles** (`buckle`): superellipse frame (wire r ≈ 0.007), center bar,
   prong, and a strap tail running past it. Put them on the outer-front face
   (≈20–50° off the side toward the front), where they read in a 3/4 view.
4. **Belts**: like a band, but use `outer_hit` across *all* surfaces it
   crosses (torso + hips + both thighs). Slope it (`z = base + amp*cos(angle)`)
   for a slung look. Add a buckle, a tip running past it with 2 eyelets, a
   keeper loop, and stitching along both edges. Keep it clear of other trims
   (check the z of the hem trim).
5. **Collars**: build from a profile (radius, z) swept around the neck center,
   with an opening at the front. Round the front corners by easing the upper
   rows toward the base near the ends. Add solidify and subdivision level 2,
   and run piping along the outer edge. **Stay under the head-clearance
   profile.**
6. **Hems and cuffs**: a ring of ray hits at the edge height, then a tube
   (r ≈ 0.011–0.016). Gloves and boot tops get a fatter "rolled cuff".
7. **Boots**: shell over shin + foot; open the top along a curve (slightly
   higher at the front), then add a rolled cuff, an inner zipper, an ankle
   strap with buckle, shin and back seams, and a toe-cap seam (`top`
   projection). **Sole**: `outline_at(foot_bvh, center, z≈0.02, grow≈0.012)`,
   then a front-sole `slab` and a separate chunky **heel** `slab` (tapered,
   pushed ~12% outward and slightly back so it reads from the side and back).
   The sole goes a little below the original foot bottom; tell the user.
8. **Claws/spikes/horns** (`claw`): tapered hooked sweep. Size them so they
   read at full-body distance (on a hand ~0.4 tall: length ≈ 0.085, base
   radius ≈ 0.02). Too small reads as pins.
9. **Folds** (`add_folds`): ellipsoid region, ridge axis, amplitude 0.004–0.013,
   wavelength 0.045–0.06, `face_dir` mask (e.g. FRONT for the inner elbow,
   −FRONT behind the knee). Use `sharp ≈ 1.6` and `wobble ≈ 0.12`;
   higher values look crumpled. Needs dense copies (level ≥ 2). Good spots:
   inner elbows, behind knees, waist sides, boot ankles (all around, slouchy).
   **Avoid** folds on small or curvy parts like gloves and hands; they turn into lumps.
10. **Braided cords / whips / ropes** (`braid`): 3 helical strands + a core
    along a dense path (≥ 8 points per braid period), with a taper function.
    For a **coiled whip**: 4+ loops tightly bundled (small radius jitter, the
    loops stacked across ~0.07 depth), hung from a D-ring on the belt via a leather
    loop wrapping the top of the bundle, with a snap. The handle exits the
    bundle down and forward: leather grip with a criss-cross wrap, a gunmetal
    ferrule with ring accents, a polished pommel, an optional lanyard. The
    thong tapers thick → thin into a short fall and a frayed cracker
    (5 thin splayed strands).
11. **Hanging hardware**: D-rings (half circle + straight bar), snaps (squashed
    spheres), rivets, eyelets (small torus rings).
12. **Parenting groups**: decide per piece which rig part it follows. Hip
    accessories go to hips; thigh straps to the upper leg; ankle straps and
    boot zippers to the lower leg; soles to the foot. Seams belong to the
    part they're on: join per part, never across parts.
13. **Naming**: prefix everything (`CW_Suit_Torso`, `CW_Strap_Thigh0_L_Buckle`)
    so grouping by name is trivial and users can find pieces.
14. **Asymmetric pieces**: mirror by using the `RIGHT` sign. Never hard-code ±X.
15. **SCALE RULES FOR ACCESSORIES** (stylized means bigger than real):
    - hip-hung coil (whip/rope/lasso): outer diameter ≈ **0.75–0.85×** the
      thigh's width. The approved Catwoman whip: thigh 0.45 wide, coil radius
      0.15, about 4.4 loops bundled across ~0.085 depth;
    - braided cord diameter at the thick end ≈ 0.3× the coil radius, tapering
      to ~40%;
    - whip/weapon handle length ≈ 0.45× the hand height; grip radius
      ≈ 0.04× the hand height, with pommel and ferrule ~20% fatter than the grip;
    - buckles: frame height ≈ strap height × 1.0–1.1 (never smaller than the
      strap);
    - claws: length ≈ 12% of the hand height, base radius ≈ 0.25× the length;
    - the first whip (coil radius 0.11, cord 0.039) was rejected as "looks
      like a keychain"; ~35% bigger was right;
    - if an item has to be found with a zoomed-in camera to be noticed,
      it's too small. Check it in the full-body render.

16. **Fit: default to FITTED.** Users rejected a loose, boxy tee as "weird".
    Use a fitted shell (offset ≈ 0.014 for thin fabric) that still behaves like
    cloth: it **bridges** the cleavage (straight span between the two bust peaks
    per height row, slight sag) and the **under-bust crease** (straight line per
    vertical column from the bust apex down ~0.33), and smooths the navel. That's
    what separates a garment from body paint. Only go loose when asked;
    then: start from a shell and make it
    *hang*. Bin vertices by angle around the torso axis, take the max radius over
    the bust band (window-max ±10° so it bridges the cleavage), and push every
    vertex below the bust out to the max of (bust radius → hem radius,
    interpolated), capped at +0.075. Then relax lightly and add vertical drape
    folds (ridges across RIGHT) on the front and back.
17. **Necklines, hems, sleeve ends, shorts legs**: `cut_by_curve`. Delete
    faces on one side of `z(angle)` and snap the boundary onto the curve. Then
    add a binding tube (rib collar, hem) placed **just inside** the cut. A ray
    aimed above a cut you made hits nothing.
18. **Two-tone garments and stripes**: big color regions (raglan shoulders,
    left/right splits): bisect the shell at the boundaries and assign
    `material_index` by position, then **cover every color boundary with a
    seam** (piping + stitches) so any unevenness disappears. **Thin stripes:
    never** material-index them (the edge follows the mesh and looks
    jagged/notched). Build each stripe as its own thin band: several rows of
    radial ray hits across its height, lift ≈ 0.0012, thickness ≈ 0.0012.
    Assign `material_index` by position (raglan red shoulders via a diagonal
    plane, a left/right color split at the RIGHT=0 plane, sleeve stripes via
    horizontal planes). Painted-in stripes look integrated; separate rings
    look like floating hoops. **Keep stripes away from joint overlaps**
    (elbow, knee), where the rig's parts step in and out.
19. **Distressed holes**: make them **horizontal tears** (ellipse rx ≈ 2.5×rz,
    rx 0.06–0.1), delete faces inside, then **snap the boundary verts onto the
    smooth noisy outline** (otherwise the grid gives blocky, pixelated holes),
    add a rolled rim tube (r ≈ 0.0026) along the ordered boundary loop, a few
    threads hanging *down* from the upper lip (gravity), and one sagging thread
    spanning the gap. Older recipe: delete faces inside noisy blobs
    (`R·(1 + 0.28 sin3φ + 0.14 sin5φ + 0.07 sin9φ)`), jitter the boundary verts
    a few mm, and sprout short thin thread tubes into the hole from ~30% of
    the boundary verts. Make holes big enough to read (radius ≥ 0.04 on a
    1.1-wide torso) or they look like stains.
20. **Printed text / logos**: create a FONT curve (`bpy.data.fonts.load` a .ttf;
    OFL fonts like Lobster are fine to bundle), convert it to a mesh,
    triangulate and subdivide twice, then project **every vertex** onto the
    surface and solidify thin. **Seen from the front, the viewer's right is
    the character's left**: map text x → −RIGHT (`s0 - x`), or increasing angle
    in `cyl` mode, or the text comes out mirrored. For an outline or shadow,
    use a second copy shifted down-left in a contrasting color; a curve
    `offset` outline spikes at sharp glyph corners.
21. **Fishnet / mesh / chain-link**: a staggered diamond lattice (rows offset
    half a cell, row height = π·r/N for square diamonds) ray-cast around the
    limb, quads per diamond, then a Wireframe modifier (thickness ~0.003). That
    gives real holes showing the skin, no texture needed. Split it at the knee
    so each half follows its own part.
22. **Wrists and ankles**: the rig's hand usually overlaps the forearm's end
    (likewise foot ↔ shin). Bands, tattoos and bracelets there must project
    onto **both** parts joined, or they sink inside the hand.
23. **Tattoos, patches, decals, glove panels**: build the polygon in the
    projection's 2D space, triangulate + subdivide 3×, then project **every**
    vertex (projecting only the corners leaves a flat plate that floats or
    sinks on curved parts). Lift ~1.5–2 mm, ~1–4 mm thick. Raised panels get a
    piping rim. Avoid glossy coats on small panels; a coat catching the key
    light reads as a grey plate. Diamond grids in
    alternating colors make harlequin patterns.
24. **Garment construction sells clothing** the way piping sold leather: on a
    tee, add raglan seams and side seams (thin same-color piping + tight
    stitches, gap ≈ 0.008), a separate **rib collar band** that rises onto the
    neck (ray against shirt + neck skin) with a rolled top edge and a stitch
    line below, a **double-needle hem** (rolled fold tube + two dashed stitch
    rings) at the bottom and the sleeve ends, an underarm sleeve seam, and a
    stitched cap seam where the sleeve color changes.
25. **Harness/straps over clothes**: ~0.045 wide, 0.008 thick ribbons with
    bevel, edge stitching both sides, metal slide adjusters (a rounded-rect
    frame wider than the strap, plus a bar) on the front, and an O-ring where
    the straps meet at the back.
26. **Fingerless gloves on mitten hands**: shell over the hand down to just
    above the fingertips, a rolled edge at the finger opening, a raised colored
    back panel with piping, and a wrist strap with a snap. Without those it
    reads as a bracelet.
27. **Sneakers**: shell shaft (black) + foot (white, with a black heel counter
    by face position), padded collar tube, tongue ribbon rising above the
    collar, silver eyelet rings in two columns, criss-cross lace tubes between
    them, a bow (two loops + two hanging ends), toe-cap piping, a mudguard
    line, a thick midsole slab plus a thin outsole slab and stripe. Leave out
    brand logos.

---

## 7. MATERIALS (Principled BSDF)

| Use | Base color (linear) | Rough | Metal | Coat (w / rough) | Bump (scale, str) |
|---|---|---|---|---|---|
| Glossy leather suit | 0.011 | 0.40 | 0 | 0.22 / 0.28 | 260, 0.08 |
| Piping | 0.02 | 0.30 | 0 | 0.40 / 0.15 | – |
| Glove (matte) | 0.008 | 0.46 | 0 | 0.15 / 0.30 | 320, 0.10 |
| Boot (high gloss) | 0.008 | 0.28 | 0 | 0.50 / 0.10 | 300, 0.05 |
| Strap leather | 0.016 | 0.36 | 0 | 0.30 / 0.20 | – |
| Sole | 0.018 | 0.65 | 0 | – | – |
| Zipper tape | 0.012 | 0.60 | 0 | – | – |
| Stitching | 0.05 (base +0.04) | 0.60 | 0 | – | – |
| Silver | 0.80 | 0.22 | 1 | – | – |
| Claw steel | 0.62 | 0.18 | 1 | – | – |
| Gunmetal | 0.18 | 0.30 | 1 | – | – |
| Braided whip leather | 0.014 | 0.42 | 0 | 0.35 / 0.20 | 220, 0.15 |

Also set `material.diffuse_color` so Solid mode shows sensible colors. For
colored outfits, keep the same roughness/coat logic and vary the base color.

---

## 8. PHASE 4: RENDER-CRITIQUE LOOP

- **Studio look** (`add_studio_look`): grey world (0.045) + soft area lights
  **positioned from FRONT/RIGHT**: key (front-left-high), fill
  (front-right), two rims (behind), top, and a low front fill that lifts boots
  out of shadow. AgX view transform.
- Render (Cycles CPU, 24–64 samples) **full-body front / 3/4 / back** plus
  close-ups of every detail area (chest, arm, hand, hip/belt, accessory from
  2 angles, legs, boot front, boot back/heel). Assemble **contact sheets** with
  Pillow and inspect them carefully.
- **Critique like an art director.** Every pass, ask:
  - Do any skin gaps show between layers?
  - Is anything floating (cuffs or rings not touching the surface) or
    sunk through?
  - Spikes, jagged edges, pinching?
  - Is any accessory too small to read at full-body distance?
  - Are the folds smooth, or lumpy/crumpled?
  - Are the hardware details visible, or hidden behind the arms? (Hanging
    arms cover the hip sides; move things or accept it if the user does.)
  - Does it match the reference's key features?
  - Is it consistent left/right?
- **Debug by isolation and measurement, never by guessing:**
  - render with only one object visible (`hide_render` the rest);
  - `scene.ray_cast` from a point and list every object it hits, to find what's
    actually there;
  - query the mesh (boundary edges, nearest point, vertex clusters) to
    check that cuts and positions are where you meant them;
  - if a render "looks wrong", first check that the **lights face the front**
    and that the camera framing matches your mental scale.
- Before delivering, do one **EEVEE render** of the saved file (it's what the
  user's viewport shows) and compare it to the Cycles renders.

### Bugs I hit and their fixes

| Symptom | Cause | Fix |
|---|---|---|
| bpy import aborts (glog "InitGoogleLogging twice") | script named `inspect.py` shadowing stdlib | rename the script |
| "incomplete header / newer Blender" | `bpy` older than the file | install a matching `bpy` |
| Whole front looks black and unlit | lights placed behind the character | derive light positions from FRONT |
| Long rod shooting out of the waist | solidify `use_even_offset=True` on a degenerate face | `use_even_offset=False` |
| Navel dent shows through the suit | smoothing centered on the wrong z | measure the dent's vertex cluster, re-center |
| Collar would clip the head | low head on the rig | measure head clearance; flare the collar outward, keep it under the profile |
| Boot cuff floating above the boot | coarse mesh + curved cut | copy at level 3, snap boundary verts to the curve, put the cuff on the same curve |
| Skin strip between boot and knee | outer layer ends with nothing under it | add the underlying suit shell |
| `min() arg is empty` slicing a limb | sparse vertical vertex spacing | widen the slice tolerance (`slice_center` does) |
| Ray missed → None crash | ray height outside the part's z-range | check against `slice_report`; assert hits |
| Folds look crumpled/noisy | high wobble frequency / sharp ridges | sharp ≈ 1.6, wobble ≈ 0.12, longer wavelength |
| Glove looks lumpy | folds on a small curvy part | remove folds there |
| Accessory "looks like a keychain" | real-world proportions | follow the scale rules in §6.15 |
| Whip hidden / reads as a key ring | placed where the arm covers it, too small, flat on a curved hip | offset it from the surface, make it bigger, tight multi-loop bundle with braided strands |
| Projected text reads backwards | text x mapped to +RIGHT | map x → −RIGHT (viewer's right is the character's left) |
| Spikes/ticks around lettering | curve `offset` outline | use a shifted shadow copy instead |
| Ring/band sinks into the wrist | the hand overlaps the forearm end | project onto forearm + hand joined |
| Stripes look like floating hoops | separate rings sitting on a joint step | paint stripes into the shell via bisect + material index, away from joints |
| Ray for a trim hits nothing | aimed above/below a cut you made | aim just inside the remaining fabric |
| Clothing looks "too loose / weird" | boxy drape | default to fitted shells that bridge the cleavage and under-bust |
| Jagged/notched stripe edges | stripes made by material index on the mesh | separate thin band objects hugging the surface |
| Blocky, pixelated holes | faces deleted on a grid | snap the boundary to the smooth outline, add a rim tube |
| Flat plate floating on a curved part | only the patch corners projected | subdivide in 2D, project every vertex |
| User's viewport looks low-quality | Material Preview uses Blender's HDRI; viewport subsurf < render | save studio lights + world in the file and set viewports to use them; viewport level = render level; darker stitches |

---

## 9. PHASE 5: DELIVERY

1. Parent every piece to its rig part with keep-transform (`parent_to_part`),
   which also stores the `morph_target` custom property.
2. Put everything in one collection named after the morph.
3. `add_studio_look()` **in the saved file**: studio lights collection, grey
   world, EEVEE engine, and every 3D viewport set to Material Preview with
   Scene Lights + Scene World. (If you rendered with Cycles in the same
   session, call it again before saving.)
4. `save_deliverables(out, 'Name_Morph')` writes:
   - `Name_Morph.blend`: the rig with the morph on it;
   - `Name_Morph_PiecesOnly.blend`: morph only, unparented, for appending into
     the user's own rig file.
5. Write `attach_to_rig.py` (`ATTACH_SCRIPT` template): after appending the
   collection, it re-parents each piece by its `morph_target`. **Test it**:
   open the original rig, append the collection, run the script, and assert
   every piece has a parent.
6. Write a README: pieces, files, how to append and attach, and notes (sole below
   the foot, viewport tips).
7. Send the user the contact sheet, the EEVEE viewport check, and the `.blend`(s)
   **as downloadable files**. If working in git, commit and push.
8. Close with what changed, what was dropped and why, known limitations, and
   an offer of next steps.

### Roblox-specific notes to tell the user

- Blender materials **don't transfer** to Roblox. Geometry (seams, stitches,
  zippers, buckles, folds) does. In Studio, set colors/materials or bake
  textures into a SurfaceAppearance.
- MeshParts have a **triangle limit** (~20k per mesh). High-subdivision
  pieces need a game-ready pass: apply modifiers at lower levels, decimate,
  join small hardware per body part, and export an FBX per part.
- Pieces must be welded to the matching R15 part in Studio. The per-part
  grouping you did maps 1:1 onto that.

---

## 10. CODE: TEMPLATE + TOOLKIT

Save the toolkit as `morph_toolkit.py` next to your build script (`import
morph_toolkit as mt`). Every helper is rig-agnostic. Fill `PARTS` from
`survey_rig()`, call `set_front(detect_front(foot))`, and measure heights
with `slice_report` before choosing any numbers. All numbers in the example
are for one specific rig (torso ≈ 1.1 wide, about 4.7 tall). **Re-derive them for
yours.**

### 10a. Template build script (`example_build.py`)

```python
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
```

### 10b. Toolkit (`morph_toolkit.py`)

```python
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
```
