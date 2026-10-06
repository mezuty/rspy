# Harley Quinn morph (Suicide Squad)

Built on the Starter 2.0 Rig with `../toolkit/morph_toolkit.py`. No bat.

**Current pass: TOP** (torso, arms, hands). The lower body is the next pass;
the first draft of it is in `lower_v1_draft.py`.

- **Fitted raglan tee:** snug, but it bridges the cleavage and under-bust like real fabric.
  - Red raglan shoulders; raglan, side and underarm seams with stitching.
  - Rib collar band with a rolled edge, and double-needle hems at the bottom and sleeves.
  - Sleeves end below the elbow, with clean stripes: red/red on her right, red/blue on her left.
  - Horizontal tears with rolled frayed rims and hanging threads.
  - "Daddy's Lil Monster" print: black script with a red drop shadow, set in Lobster (OFL, see `fonts/OFL.txt`).
- **Shoulder holster harness:** stitched straps with silver slide adjusters and a back O-ring. A stitched holster with a welt, a retention strap with a snap, and a pistol grip under her left arm.
- **Choker:** red leather with stitching, gold PUDDIN letters and a ring.
- **Arms:**
  - Her right: harlequin diamond forearm tattoo and a purple stitched wristband with snaps.
  - Her left: spiked black bracelet, a purple band, and a fingerless black glove with a raised red back panel, piping and a wrist strap with a snap.

| File | What it is |
|---|---|
| `HarleyQuinn_Morph.blend` | Rig with the morph on it (collection **Harley Quinn Morph**), studio lights, viewport set to Material Preview with scene lights |
| `HarleyQuinn_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run it in Blender's Text Editor to parent each piece to its body part |
| `build_harley.py` | Builds everything: `python build_harley.py <rig.blend> <out_dir>` (bpy 5.2) |
| `render_harley.py` | Preview renders |
| `previews/` | Renders |
