# Harley Quinn morph (Suicide Squad)

Built on the Starter 2.0 Rig with `../toolkit/morph_toolkit.py`. No bat.

- **Shirt:** loose, distressed white raglan tee.
  - Red raglan shoulders and a ribbed red collar.
  - Sleeves end below the elbow, with stripes above the elbow: red/red on her right, red/blue on her left. Matching cuff bindings.
  - Torn holes with frayed threads.
  - "Daddy's Lil Monster" print: black script with a red drop shadow, set in Lobster (an open font license, see `fonts/OFL.txt`).
- **Shoulder holster:** straps over both shoulders crossing at a back ring, stitched, with a holster, flap, snap and pistol grip under her left arm.
- **Choker:** red, with gold "PUDDIN" letters and a ring.
- **Shorts:** sequin hot pants, red on her right and blue on her left, with bound leg openings.
- **Belt:** black, with two rows of gold pyramid studs and the gold double-diamond buckle.
- **Fishnet tights:** a real mesh net (Wireframe modifier) over the legs. Small diamond tattoos on her right thigh.
- **Arms:**
  - Her right: red/black harlequin diamond tattoo on the forearm and a purple wristband.
  - Her left: spiked black bracelet, a purple band, and a fingerless black/red glove.
- **Sneakers:** black and white high-tops with a padded collar, tongue, silver eyelets, criss-cross laces and a bow, toe-cap piping, a mudguard line, and a thick two-tone sole. No brand logos.

| File | What it is |
|---|---|
| `HarleyQuinn_Morph.blend` | Rig with the morph on it (collection **Harley Quinn Morph**), studio lights, viewport set to Material Preview with scene lights |
| `HarleyQuinn_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run it in Blender's Text Editor to parent each piece to its body part |
| `build_harley.py` | Builds everything: `python build_harley.py <rig.blend> <out_dir>` (bpy 5.2) |
| `render_harley.py` | Preview renders |
| `previews/` | Renders |

The soles reach about 0.06 studs below the original feet.
