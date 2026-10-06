# ROBLOX MORPH BUILDER: Instructions for an AI agent

You are a **Roblox morph artist who works only through code**. A "morph" is a full
outfit (clothing, armor, accessories) modeled to fit a Roblox avatar rig so a
player can wear it in-game. You'll build it in **Blender, driven by Python
(`bpy`)**, with no hand sculpting. You may be running **locally** on the
user's computer (their Blender installed) or in a **cloud sandbox** (no GUI,
often no GPU); §2 says what changes. Either way you mostly see your work by
rendering images and looking at them.

The person will give you:
1. A **rig `.blend` file**: the body you dress. It may be any rig (R15-style
   segmented bodies, blocky classic, custom proportions). Never assume part
   names, sizes, facing direction or heights. **Measure everything.**
2. **Reference images** of the outfit, plus style references showing the quality
   bar.
3. Scope ("just the top", "only the boots", "full outfit").

Your output is a `.blend` with the morph fitted and parented to the rig, a
pieces-only `.blend`, an attach script, the build script, and (when wanted)
preview renders: sent as downloads in the cloud, saved next to the user's
project when local.

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

## QUICK-START CHECKLIST (every morph)

1. Work out **local vs cloud** (§2) and get a Blender/`bpy` that **matches the
   rig file's version**.
2. Confirm scope with the user, list the components you'll build, and offer
   optional props instead of assuming them (§1).
3. **Survey + measure the rig** (§3): part names, FRONT, slices, head
   clearance, hand/wrist and foot/shin overlaps.
4. Build in **passes**: top → (user OK) → bottom → (user OK) → head extras.
5. Per pass: fitted shells → openings → color regions → construction details
   (seams, hems, collars) → hardware → accessories (§5–§6).
6. Run **`qa_report`**, then do **quick low-res checks** of what changed, fix,
   and repeat.
7. Save with the **studio look** set in the file, write and **test** the attach
   script, deliver per environment (§9), and summarize what changed and what's
   next.

---

## 1. WORKING WITH THE USER

- **Confirm understanding first.** Restate what a morph is, what you'll build
  and the scope. Ask for reference images if none are given, and which head
  option or part to use if the rig has several.
- **Be honest about the medium.** Say up front that you model with code
  (procedural geometry, ray-cast placement, render-and-check loops). That gets
  very clean results, but hand-sculpted organic detail is its weakest area.
- **Work in passes the user controls.** Default order: **top first** (torso,
  arms, hands), show it, **wait** for "do the bottom", then the lower body, then
  head pieces only if asked. Doing everything at once means rework.
- **Break the reference down for the user before building**: list every
  component you plan, and say what you'll skip (props, logos, hair and makeup
  are head pieces). **Optional accessories the user didn't name** (holsters,
  harnesses, weapons, bags) should be offered, not assumed. If you include
  them, put them behind a flag (`BUILD_HARNESS = True/False`) so they can be
  removed in one line. I built a holster harness from the reference and the
  user asked for it to be removed.
- **Give short progress notes** during long builds ("measuring the rig",
  "first draft, fixing X and Y"). Never go silent for long. Split work into small
  steps and run anything slow in the background so you don't look stuck.
- **Rendering costs the user time.** Do your own checks with **quick low-res
  renders** (≈420×520, ~10 samples, a few seconds each). Only do full-quality
  preview sets when the user asks, or once at the very end. If the user says
  "you don't need to render", deliver the `.blend` and keep only quick
  internal checks.
- **Show, then tell.** When you do show images: a contact sheet (front, 3/4,
  back, close-ups) plus a short list of what changed, what you dropped, and why.
- **Deliver the files the way the environment allows** (§2): downloads in a
  cloud session, saved next to the user's files locally. Commit/push only if
  you're working in a git repo.
- **Intentional "imperfections" can look like bugs.** Rips, frayed edges and
  asymmetry should be clearly deliberate and placed away from focal graphics
  (prints, logos, buckles). When the user reports "a hole", check whether it's
  one of yours (QA report §8) and say so plainly.
- If the user's own Blender looks worse than your renders, it's almost always
  **lighting or viewport settings**, not the model. See §8 and §9.

---

## 2. ENVIRONMENT SETUP: LOCAL OR CLOUD

First work out **where you are running**, then follow only the matching
column. Don't do cloud workarounds on a local machine, and don't assume local
conveniences in the cloud.

| | **LOCAL** (the user's own computer, Blender installed) | **CLOUD / SANDBOX** (remote container, no GUI, often no GPU) |
|---|---|---|
| How to tell | The user's files are on this machine; `blender --version` works (or Blender is in Applications / Program Files); a desktop session | Fresh Linux container, paths like `/home/user`, `/tmp`, no `blender` binary, uploads arrive as attachments |
| Blender | Use the **user's installed Blender** in background mode: `blender -b <rig.blend> --python build.py -- <args>`. No pip install needed. Find it: Windows `C:\Program Files\Blender Foundation\Blender X.Y\blender.exe`, macOS `/Applications/Blender.app/Contents/MacOS/Blender`, Linux `blender` | `pip install bpy==X.Y.*` in a venv with the matching Python (see below). `bpy` is a module: run `python build.py <rig> <out>` and open the file with `bpy.ops.wm.open_mainfile` |
| Arguments | Blender passes your args after `--`: read `sys.argv[sys.argv.index('--') + 1:]` | Plain `sys.argv` (the scripts here use `sys.argv[-2:]`, which works in both) |
| Version match | Use the same Blender version the rig was saved with (the user's own install usually is) | Pick the `bpy` version that matches the file (see the warnings below) |
| GPU / EEVEE | Usually available: EEVEE renders in seconds; the GPU may be used for Cycles | Usually none: Cycles on CPU; EEVEE only with Mesa software EGL (slow, see below) |
| Viewing renders | Save PNGs next to the project; open them or read them with your image tool | Save to a scratch folder, read them with your image tool, send finals to the user as downloads |
| Live Blender | If you're connected to a **running Blender** (e.g. a Blender MCP add-on), you can run the same scripts inside it; the user watches the scene update. **Don't call `open_mainfile` there without asking**: it replaces whatever the user has open (unsaved work is lost). Save first or work in a second Blender instance, and keep the build script re-runnable | n/a |
| Installing things | **Don't** apt-get, change system Python or install drivers on the user's machine. Use what's there; ask before installing anything (Pillow is optional, see below) | Fine to install packages in your sandbox (venv, Pillow, Mesa) |
| Delivering | Save outputs into a folder the user chose (e.g. next to the rig), and tell them the paths. Never overwrite their original rig file | Send the `.blend`(s), attach script and preview sheet as downloadable files; commit + push if in a repo |

**Common to both:**

1. **Match the Blender version to the file.** A warning like *"File written by
   newer Blender binary (502.xx)"* or *"incomplete header, may be from a newer
   version"* means the Blender/`bpy` is too old for the file. Objects can
   silently go missing (armatures, parenting) with the wrong version.
   - Version code `502` means Blender 5.2.
   - Cloud: `pip index versions bpy` lists versions. Each `bpy` needs a specific
     Python (bpy 4.x→3.11, 5.x→3.11 or 3.13; check the wheel tags). Make a
     venv per version: `python3.13 -m venv b52 && b52/bin/pip install "bpy==5.2.*"`.
   - Local: ask the user which Blender version they use, or read it from
     `blender --version`.
2. **Never name your scripts after stdlib modules** (`inspect.py`, `types.py`,
   `random.py`, `copy.py`...). The script's folder goes first on `sys.path`, so
   `import bpy` crashes in obscure ways (e.g. a glog "InitGoogleLogging()
   twice" abort).
3. **Contact sheets**: Pillow if available. Otherwise render several small views
   and look at them one by one; never block on a missing optional library.
4. **Headless rendering:**
   - **Cycles on CPU** always works, at 10 samples for quick checks and 48–64
     for finals, with denoising.
   - **EEVEE** shows *exactly* what the user's Material Preview viewport will look
     like. Local: just use it. Cloud without a GPU: install Mesa
     (`apt-get install libegl1 libegl-mesa0 libgl1-mesa-dri libgbm1`) and run
     with `EGL_PLATFORM=surfaceless`; it takes ~3 min/frame, so do **one** EEVEE
     check before the final delivery, not every iteration.
5. Keep build, render and debug scripts as separate files. The build script
   must be **re-runnable from the original rig file** (deterministic: seed any
   randomness, no manual steps). Iterate by editing parameters and re-running.
   Each run should write to a fresh output folder; never modify the user's
   rig file in place.
6. Fonts for printed text: bundle an open-license font (OFL, e.g. Lobster for
   script) next to the build script with its license; system fonts differ
   between machines.

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
    vertical column from the bust apex down ~0.33), and smooths the navel.
    **Fade the cleavage bridge out slowly** (over ~0.12 above the bust): a short
    fade leaves a pit at the top of the cleavage that renders as a dark "hole"
    right under a chest print. Then run `fill_pits` (fill-only relax along FRONT)
    over the centre front. A normal Laplacian smooth re-digs the groove, because
    smoothing shrinks surfaces. That's
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

28. **Plants: leaves, vines, tendrils** (`leaf`, `vine`, `tendril`,
    `surface_path`):
    - **Leaf** = a grid inside an outline (`pointed`, `ivy` 3-lobed, `round`),
      V-folded along the midrib, a slight tip curl, a petiole stub, and a raised
      midrib plus 3 pairs of side veins in a darker green. Test new shapes on
      their own in an empty scene first.
    - **Size for full-body reading**, like every accessory: on a ~0.38-wide arm,
      vine radius ≈ 0.017 and leaves ≈ 0.13–0.16 long. My first pass (vine
      0.0075, leaves 0.06) read as thread and confetti.
    - **Leaves face the camera**: grow them mostly flat along the surface
      (direction ≈ 0.5·along + sideways + 0.3·normal), lifted ~0.01 above the
      vine, curl ≤ 0.08. A strong curl buries half of each leaf in the surface.
    - **Leaves grow in pairs** at nodes (one ~20% smaller), alternating sides
      along the vine; spirals put half the leaves on the far side, so pair them
      to keep it lush. Add a tendril every ~4 nodes.
    - **Vines across body parts**: build the path with `surface_path` over a
      union of skin + garment BVHs (`bvh_union`), then **split it by part**
      (e.g. z above/below the elbow) so each segment follows its own bone.
    - **Leaf appliqués that rise above a garment edge** (Poison Ivy's leaf cups):
      project onto a *proxy* surface (the body part offset to the garment's outer
      level), not onto skin + garment, or the appliqué kinks at the edge.
    - **Leg/arm vines: project onto the limb only.** Including a neighbouring
      garment (the leotard) in the BVH lets the vine jump onto it, e.g. across
      the crotch. Match the reference's *visible* path: shape the angle/height
      curve so the long diagonal crosses the **front** (outer hip → inner thigh)
      and the wrap-around happens at the back. A constant-rate spiral hides half
      the vine.
    - **Thorny vines**: a darker brown-purple tube, hooked thorns (`claw`,
      hook ≈ 0.25, length ≈ 0.03) every few samples on alternating sides, and
      ivy-leaf clusters of 3.
    - **Leaf-topped boots**: the top edge peaks to a point over the knee
      (`top(a) = base + h·sin(a)^6`). Make sure the boot actually reaches the
      knee joint: knee-high on this rig means a top at ≈0.985–1.1, not 0.93
      (that read as calf boots). Add leaf-panel appliqués (proxy surface,
      outline, midrib, veins) on the shin and the outer side.
    - **High-cut leotard**: bisect the hips shell along two slanted planes
      (crotch width → high hip side) that contain FRONT, delete below, and run
      a rolled edge along `boundary_loops` of the cut.
    - Palette: deep suit green, a brighter leaf green, a mid leaf green, dark
      veins, and a brownish-green stem. Contrast between suit and leaves is what
      makes the leaves read.

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

- **Automated QA before any render** (`qa_report`): it lists unparented
  pieces, leftover `_temp` objects, geometry far below the ground or flung far
  away (failed ray casts), and **every open boundary on a shell that isn't one
  of your intended openings** (necklines, hems, tears, cut-outs). Pass the
  centres of the openings you cut on purpose; anything else is a hole to fix.
  Run it at the end of every build and fix everything it prints.
- **Quick checks**: 420×520, ~10 samples, 2–4 targeted views of what you just
  changed. Full-quality sets only at the end or when asked.
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
- **When the user reports a spot ("a hole", "a dent", "a dark mark")**: first
  run `qa_report` (real openings), then **sample the surface numerically**:
  ray cast a small grid (e.g. 7 columns × 16 rows across the area, ignoring
  decals) and print the depth along FRONT. A pit or groove shows as a value
  lower than its neighbours. Fix, re-sample until the profile is smooth and
  monotonic, then confirm with one close-up render.
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
| Vine jumps across the crotch | the leotard was in the vine's projection BVH | project onto the limb only |
| Boots read as calf boots | top below the knee joint | measure the knee overlap; set the top at the knee |
| Vine wraps behind and misses the reference's diagonal | constant-rate spiral | shape the angle(z) curve so the long run crosses the front |
| Vines look like thread, leaves like confetti | real-world plant scale | vine r ≈ 0.017, leaves 0.13–0.16 on an arm; pairs at nodes |
| Leaves look tiny although their size is right | strong curl/tilt buries half of each leaf | lift ~0.01, curl ≤ 0.08, grow mostly flat; check with a close-up |
| Dark "hole" under the chest print persists after removing rips | pit where the cleavage bridge fades out, re-dug by Laplacian smoothing | longer fade + `fill_pits`; verify with a depth-sample grid |
| User reports "a hole" in the shirt | an intentional rip sitting right under the chest print | keep distressing away from prints and focal graphics; run `qa_report` to tell intended openings from real holes |
| User wants an accessory gone | unrequested prop (holster harness) built from the reference | offer props first; put each behind a `BUILD_*` flag |
| Expected-openings check misfires | mirrored coordinates (back-of-body tears use a mirrored s) | compute expected centres the same way the cut code does |
| Long waits for the user | full-quality render sets after every tweak | quick low-res checks; finals once |
| Build ran but a piece silently vanished | an optional section gated off, or a ray missed and the piece was skipped | QA report + check object counts between builds |
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
7. **Deliver per environment** (§2). Cloud: send the `.blend`(s), attach
   script and (when wanted) the contact sheet as downloadable files. Local: save
   them next to the user's project and give the paths. If working in git,
   commit and push.
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

`render_views.py` (in the same folder as the toolkit) renders named views
for quick checks (`RES=420,520 SAMPLES=10`) or finals. The toolkit now also
contains the generic band/cut/patch helpers (`ring_band`, `ring_points`,
`stitch_ring`, `cut_by_curve`, `patch`, `bvh_union`, `side_dir`) and the plant
generators.

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

RIG, OUT = sys.argv[-2], sys.argv[-1]   # works for `python x.py a b` and `blender -b --python x.py -- a b`
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
mt.qa_report(ground_z=0.0)   # fix everything it prints before showing the user
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


# ------------------------------------------------------------------ bands, cuts, patches (from Harley)
def side_dir(a_deg):
    """Horizontal unit vector at angle a (0 = RIGHT, 90 = FRONT)."""
    a = math.radians(a_deg)
    return RIGHT * math.cos(a) + FRONT * math.sin(a)


def angle_of(co, center):
    d = co - Vector((center[0], center[1], co.z))
    return math.degrees(math.atan2(d.dot(FRONT), d.dot(RIGHT))) % 360


def ring_points(bvhs, center, z, lift, nseg=72, z_fn=None):
    """Closed ring of points on the outermost of several surfaces, at height z
    or z_fn(angle). Misses are skipped. Last point repeats the first."""
    pts = []
    for i in range(nseg + 1):
        a = 360.0 * i / nseg
        r = side_dir(a); zz = z_fn(a) if z_fn else z
        hit = outer_hit(bvhs, Vector((center[0], center[1], zz)) + r * 5, -r)
        if hit is not None:
            pts.append(hit[0] + hit[1] * lift)
    return pts


def ring_band(name, bvhs, center, z, h, lift, thick, mat, nseg=64, z_fn=None, rows=1):
    """Band (strap, cuff, choker, stripe) hugging the outermost surface. rows>1
    adds intermediate rows so wide bands follow curvature (thin stripes: 6)."""
    bm = bmesh.new(); grid = []
    for r_ in range(rows + 1):
        dz = -h / 2 + h * r_ / rows
        row = []
        for i in range(nseg):
            a = 360.0 * i / nseg
            d = side_dir(a); zz = (z_fn(a) if z_fn else z) + dz
            hit = outer_hit(bvhs, Vector((center[0], center[1], zz)) + d * 5, -d)
            row.append(bm.verts.new(hit[0] + hit[1] * lift))
        grid.append(row)
    for r_ in range(rows):
        for i in range(nseg):
            a0, a1 = grid[r_], grid[r_ + 1]
            bm.faces.new((a0[i], a0[(i + 1) % nseg], a1[(i + 1) % nseg], a1[i]))
    ob = mesh_obj(name, bm, mat); add_solidify(ob, thick, offset=1.0); smooth(ob)
    return ob


def stitch_ring(name, bvhs, center, z, lift, mat, nseg=200, dash=0.55, z_fn=None):
    """Dashed stitch line round a body at height z (or z_fn(angle))."""
    pts = ring_points(bvhs, center, z, lift, nseg=nseg, z_fn=z_fn)
    bm = bmesh.new()
    for i in range(0, len(pts) - 1, 2):
        a_, b_ = pts[i], pts[i + 1]
        t = b_ - a_; L_ = t.length
        if L_ < 1e-6: continue
        t.normalize(); c = a_.lerp(b_, 0.5)
        n = (c - Vector((center[0], center[1], c.z))).normalized()
        box(bm, c, t, n.cross(t).normalized(), n, L_ * dash, 0.001, 0.0012)
    return mesh_obj(name, bm, mat)


def cut_by_curve(ob, center, z_fn, keep_above=True, snap=0.06):
    """Delete faces on one side of z_fn(angle) and snap the new edge onto the
    exact curve: clean necklines, hems, sleeve ends, boot tops, shorts legs."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    dead = []
    for f in bm.faces:
        c = f.calc_center_median(); zc = z_fn(angle_of(c, center))
        if (c.z < zc) if keep_above else (c.z > zc):
            dead.append(f)
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    for v in bm.verts:
        if v.is_boundary:
            zc = z_fn(angle_of(v.co, center))
            if abs(v.co.z - zc) < snap:
                v.co.z = zc
    bm.to_mesh(ob.data); bm.free()


def patch(name, bvh, poly2d, lift, thick, mat, mode='cyl', center=(0, 0), subdiv=3):
    """Polygon (tattoo, panel, label, pocket) built in the projection's 2D
    space, subdivided, then EVERY vertex projected so it hugs curved surfaces."""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((u, v, 0))) for u, v in poly2d]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for _ in range(subdiv):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts:
        p = project(bvh, [(v.co.x, v.co.y)], mode, center)
        if not p:
            bm.free(); return None
        v.co = p[0][0] + p[0][1] * lift
    ob = mesh_obj(name, bm, mat); add_solidify(ob, thick, offset=1.0); smooth(ob)
    return ob


def boundary_loops(ob, pred=None):
    """Ordered open-boundary loops of a mesh (world space) as lists of
    (co, normal), optionally only edges whose verts satisfy pred(co). Use it to
    run trims/piping exactly along cut edges (leg openings, tears...)."""
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); bm.normal_update()
    edges = [e for e in bm.edges if e.is_boundary and (pred is None or (pred(e.verts[0].co) and pred(e.verts[1].co)))]
    adj = {}
    for e in edges:
        a, b = e.verts
        adj.setdefault(a.index, []).append(b.index); adj.setdefault(b.index, []).append(a.index)
    co = {v.index: v.co.copy() for v in bm.verts}; nrm = {v.index: v.normal.copy() for v in bm.verts}
    bm.free()
    loops, seen = [], set()
    for start in adj:
        if start in seen: continue
        loop = [start]; seen.add(start); prev, cur = None, start
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            if not nxt: break
            prev, cur = cur, nxt[0]; loop.append(cur); seen.add(cur)
        if len(loop) > 4: loops.append([(co[i], nrm[i]) for i in loop])
    return loops


def bvh_union(objs):
    """One BVH over several meshes (e.g. forearm + hand: the hand overlaps the
    wrist, so anything at the wrist must project onto both)."""
    bm = bmesh.new()
    for ob in objs:
        tmp = bmesh.new(); tmp.from_mesh(ob.data); tmp.transform(ob.matrix_world)
        me = bpy.data.meshes.new('_u'); tmp.to_mesh(me); tmp.free()
        bm.from_mesh(me); bpy.data.meshes.remove(me)
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


# ------------------------------------------------------------------ plants: leaves, vines, tendrils
def leaf(name, base, direction, normal, mat, length=0.07, width=0.04, kind='pointed', fold=0.3,
         curl=0.25, twist=0.0, vein_mat=None, thick=0.0025):
    """Stylized leaf: grid inside an outline, V-folded along the midrib, tip
    curling back, petiole stub, optional raised midrib + side veins.
    kind: 'pointed' (lanceolate), 'ivy' (3-lobed), 'round'."""
    d = direction.normalized()
    n = (normal - d * normal.dot(d)).normalized()
    sd = d.cross(n)
    if twist:
        q = math.radians(twist)
        sd, n = sd * math.cos(q) + n * math.sin(q), n * math.cos(q) - sd * math.sin(q)

    def half_w(u):
        if kind == 'ivy':
            lobe = 1 + 0.45 * max(0.0, math.sin(math.pi * (u - 0.15) / 0.5)) ** 2 if u < 0.65 else 1.0
            return width / 2 * (math.sin(math.pi * min(u, 0.999)) ** 0.55) * lobe * (1.15 - 0.45 * u)
        if kind == 'round':
            return width / 2 * math.sin(math.pi * u) ** 0.5
        return width / 2 * (math.sin(math.pi * u) ** 0.75) * (1.1 - 0.35 * u)

    NU, NV = 14, 6
    bm = bmesh.new(); grid = []
    for i in range(NU + 1):
        u = i / NU; w = half_w(u)
        row = []
        for j in range(-NV, NV + 1):
            v = j / NV
            p = (base + d * (u * length) + sd * (v * w)
                 + n * (fold * abs(v) * w)                      # V fold along the midrib
                 - n * (curl * length * u * u))                 # tip curls back
            row.append(bm.verts.new(p))
        grid.append(row)
    for i in range(NU):
        for j in range(2 * NV):
            a, b, c, e = grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]
            if len({a.co.to_tuple(5), b.co.to_tuple(5), c.co.to_tuple(5), e.co.to_tuple(5)}) == 4:
                bm.faces.new((a, b, c, e))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    ob = mesh_obj(name, bm, mat); add_solidify(ob, thick, offset=0.0); smooth(ob)
    add_subsurf(ob, 1)
    out = [ob]
    stem = [base - d * length * 0.18 - n * 0.004, base - d * length * 0.05, base + d * length * 0.05]
    out.append(tube(name + '_Stem', stem, max(0.0022, width * 0.05), vein_mat or mat, res=1))
    if vein_mat:
        mid = [base + d * (u * length) - n * (curl * length * u * u) + n * (thick * 0.6 + 0.0006)
               for u in [k / 12 * 0.92 for k in range(13)]]
        out.append(tube(name + '_Midrib', mid, max(0.0012, width * 0.035), vein_mat, res=1,
                        radii=[1 - 0.7 * k / 12 for k in range(13)]))
        for k, u0 in enumerate((0.25, 0.45, 0.65)):
            for sg in (-1, 1):
                w0 = half_w(u0 + 0.15) * 0.75
                pts = []
                for t in (0.0, 0.5, 1.0):
                    u = u0 + 0.15 * t; v = sg * 0.75 * t
                    pts.append(base + d * (u * length) + sd * (v * half_w(u)) + n * (fold * abs(v) * half_w(u))
                               - n * (curl * length * u * u) + n * (thick * 0.6 + 0.0005))
                out.append(tube(f'{name}_Vein{k}{sg}', pts, max(0.0008, width * 0.02), vein_mat, res=1))
    return out


def vine(name, path, radius, mat, taper=(1.0, 0.45), res=2):
    """Organic vine/stem tube along a 3D path, tapering from taper[0] to taper[1]."""
    nn = len(path)
    radii = [taper[0] + (taper[1] - taper[0]) * i / max(1, nn - 1) for i in range(nn)]
    return tube(name, path, radius, mat, res=res, radii=radii)


def tendril(name, base, direction, normal, mat, length=0.05, radius=0.0025, turns=1.6):
    """Curly tendril: a tightening spiral that leaves a vine."""
    d = direction.normalized(); n = (normal - d * normal.dot(d)).normalized(); sd = d.cross(n)
    pts = []
    for i in range(40):
        f = i / 39
        ang = 2 * math.pi * turns * f
        r = length * 0.35 * (1 - f) ** 1.2
        pts.append(base + d * (length * 0.6 * f) + (sd * math.cos(ang) + n * math.sin(ang) * 0.6) * r
                   - sd * length * 0.35 + n * 0.0)
    return tube(name, pts, radius, mat, res=1, radii=[1 - 0.75 * i / 39 for i in range(40)])


def surface_path(bvhs, center_fn, samples, lift):
    """Path given as (angle_deg, z) pairs wrapped radially onto the outermost
    of several surfaces; center_fn(z) -> (x, y) axis of the limb/torso.
    Returns list of (co, normal). Misses are skipped."""
    out = []
    for a, z in samples:
        cx, cy = center_fn(z); d = side_dir(a)
        h = outer_hit(bvhs, Vector((cx, cy, z)) + d * 5, -d)
        if h is not None: out.append((h[0] + h[1] * lift, h[1]))
    return out


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
```
