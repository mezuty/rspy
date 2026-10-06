# Poison Ivy morph

Built on the Starter 2.0 Rig with `../toolkit/morph_toolkit.py` (leaf / vine /
tendril generators).

**Current pass: TOP** (torso, arms, hands). The lower body comes next: the
leotard legs, thorny thigh vines, and green boots with pointed leaf tops.

- **Strapless corset bodice:** deep green, fitted, spanning the cleavage like real fabric.
  - A sweetheart neckline with a rolled dark edge.
  - Each cup is a big leaf appliqué (dark outline, midrib, three pairs of veins) whose tip rises above the neckline.
  - Vine-style panel lines: under-cup sweeps, a V converging to the waist, side lines, and back lines.
  - Leaves sprouting from the lines, plus an ivy leaf at the center of the neckline.
- **Opera gloves:** above the elbow, each topped with a tall pointed leaf on the outer arm.
  - Veins and a rolled edge on the leaf point.
  - An outer seam, finger lines, soft elbow creases, and a ring of leaves at the wrist.
- **Vines:** thick vines spiral from each shoulder down to the wrist, over skin and glove, with paired leaves (pointed and ivy-shaped) and curly tendrils. Another vine curls over her left shoulder onto the chest, with a small branch and leaves.

Skin color comes from the rig; a green-skin version would be a rig material
change. The hair is a separate head piece.

| File | What it is |
|---|---|
| `PoisonIvy_Morph.blend` | Rig with the morph on it (collection **Poison Ivy Morph**), studio lights, viewport set to Material Preview with scene lights |
| `PoisonIvy_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run it in Blender's Text Editor to parent each piece to its body part |
| `build_ivy.py` | Builds everything: `python build_ivy.py <rig.blend> <out_dir>` (bpy) or `blender -b --python build_ivy.py -- <rig.blend> <out_dir>` |
| `previews/` | Quick low-res checks |
