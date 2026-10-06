# Catwoman morph (full catsuit)

Arkham-style leather catsuit for the Starter 2.0 Rig.

- **Top:** fitted suit with an open V zipper, piped and stitched panel seams, a flared collar, buckled arm straps, and gloves with claws.
- **Lower:** suit over the hips and legs with panel seams, two buckled straps per thigh, and knee-high heeled boots (cuffed top, inner zipper, ankle strap, toe-cap seam, sole and stacked heel).
- **Whip:** Arkham Knight-style braided bullwhip coiled on her left hip, hanging from a D-ring on a slim slung belt (front buckle, eyelets, keeper). Braided grip, gunmetal ferrule and pommel, tapered fall and cracker.
- **Folds:** stylized leather folds at the inner elbows, behind the knees, at the waist sides and round the boot ankles.

## Why the file looks like the previews

The `.blend` saves a studio setup: the **CW Studio Lights** collection, a grey
**CW_Studio_World**, EEVEE as the render engine, and every 3D viewport set to
Material Preview using those scene lights and world. With Blender's default
Material Preview HDRI, the glossy black leather reflects an outdoor scene and
looks washed out. If a viewport still looks off, open the viewport shading popover
(the arrow next to the shading buttons) and enable **Scene Lights** and **Scene World**.
`previews/viewport_eevee.png` shows the EEVEE look.

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
