# Harley Quinn morph (Suicide Squad)

Built on the Starter 2.0 Rig with `../toolkit/morph_toolkit.py`. No bat.

Full outfit: top (torso, arms, hands) and lower body (shorts, belt, fishnets,
sneakers). `previews/` holds quick low-res checks.

- **Fitted raglan tee** (no rip under the print): snug, but it bridges the cleavage and under-bust like real fabric.
  - Red raglan shoulders; raglan, side and underarm seams with stitching.
  - Rib collar band with a rolled edge, and double-needle hems at the bottom and sleeves.
  - Sleeves end below the elbow, with clean stripes: red/red on her right, red/blue on her left.
  - Horizontal tears with rolled frayed rims and hanging threads.
  - "Daddy's Lil Monster" print: black script with a red drop shadow, set in Lobster (OFL, see `fonts/OFL.txt`).
- **Choker:** red leather with stitching, gold PUDDIN letters and a ring.
- **Arms:**
  - Her right: harlequin diamond forearm tattoo and a purple stitched wristband with snaps.
  - Her left: spiked black bracelet, a purple band, and a fingerless black glove with a raised red back panel, piping and a wrist strap with a snap.

| File | What it is |
|---|---|
- **Sequin hot pants:** fitted, red on her right and blue on her left.
  - Waistband, belt loops, and a stitched center seam over the color split.
  - Fly stitching, curved front pocket seams, stitched back patch pockets, side seams.
  - Bound and stitched leg hems.
- **Belt:** black with stitched edges, gold pyramid studs and silver grommets, the double-diamond buckle, and a tip with a metal end.
- **Fishnet tights:** a real net (Wireframe modifier) with harlequin tattoos underneath: diamonds and a spade on her right thigh, a heart and a diamond on her left.
- **High-top sneakers:**
  - Black shaft and white foot with a padded collar, a heel pull loop, and a tongue with a pull loop.
  - Silver eyelets, criss-cross laces, and a bow with metal-tipped ends.
  - A stitched black heel counter, toe-cap piping, and a mudguard line.
  - An outer ankle patch with a red diamond, and a two-tone sole. No logos.

The soles reach about 0.06 studs below the original feet.

| `HarleyQuinn_Morph.blend` | Rig with the morph on it (collection **Harley Quinn Morph**), studio lights, viewport set to Material Preview with scene lights |
| `HarleyQuinn_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run it in Blender's Text Editor to parent each piece to its body part |
| `build_harley.py` | Builds everything: `python build_harley.py <rig.blend> <out_dir>` (bpy 5.2) |
| `render_harley.py` | Preview renders |
| `previews/` | Renders |
