# Catwoman morph (full catsuit)

Arkham-style leather catsuit for the Starter 2.0 Rig.

- **Top:** fitted suit with an open V zipper, piped and stitched panel seams, a flared collar, buckled arm straps, and gloves with claws.
- **Lower:** suit over the hips and legs with panel seams, two buckled straps per thigh, and knee-high heeled boots (cuffed top, inner zipper, ankle strap, toe-cap seam, sole and stacked heel).

| File | What it is |
|---|---|
| `Catwoman_Morph.blend` | Your rig with the morph already on it (collection **Catwoman Morph**) |
| `Catwoman_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run this in Blender's Text Editor to parent each piece to its body part |
| `build_catwoman.py` | The script that builds the morph (`python build_catwoman.py <rig.blend> <out_dir>` with the `bpy` 5.2 module) |
| `render_morph.py`, `render_util.py` | Preview rendering |
| `previews/` | Renders |

Every piece is parented to the body part it sits on. The boot soles reach
about 0.05 studs below the original feet.
