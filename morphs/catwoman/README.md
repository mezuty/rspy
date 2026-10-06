# Catwoman morph: top (torso + arms + gloves)

Arkham-style leather catsuit top for the Starter 2.0 Rig.

| File | What it is |
|---|---|
| `Catwoman_Top_Morph.blend` | Your rig with the morph already on it (collection **Catwoman Morph (Top)**) |
| `Catwoman_Top_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run this in Blender's Text Editor to parent each piece to its body part |
| `build_catwoman_top.py` | The script that builds the morph (`python build_catwoman_top.py <rig.blend> <out_dir>` with the `bpy` 5.2 module) |
| `previews/` | Renders |

Pieces are parented to the body part they sit on (torso → `Robloxian2014`,
upper/lower arm and hand → `Robloxian2012/2011/2010` and `Robloxian209/208/207`).
