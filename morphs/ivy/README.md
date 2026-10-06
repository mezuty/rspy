# Poison Ivy morph

Built on the Starter 2.0 Rig with `../toolkit/morph_toolkit.py`. **Leaves are flat**
like the reference (`flat_leaf`: lying on the surface with a dark outline,
midrib and veins); **vines, tendrils and thorns are 3D** (round tubes, curly
tendrils, hooked thorns).

**Current pass: TOP** (torso, arms, hands). The lower body comes next: the
leotard legs, thorny thigh vines, and green boots with pointed leaf tops.

- **Strapless corset bodice:** deep green, fitted, spanning the cleavage like real fabric.
  - A sweetheart neckline where each cup rises to a pointed leaf tip, with a rolled dark edge.
  - One curved line on each cup, as in the reference.
  - Panel lines: under-cup sweeps, a V converging to the waist, side lines, and back lines.
  - Flat leaves growing along the side and under-cup lines.
- **Opera gloves:** above the elbow, each topped with a tall pointed leaf on the outer arm.
  - Veins and a rolled edge on the leaf point.
  - An outer seam, finger lines, and soft elbow creases.
- **Vines:** round vines spiral from each shoulder down to the wrist, over skin and glove, with paired flat leaves (pointed and ivy-shaped) and curly 3D tendrils. Another vine curls over her left shoulder onto the chest, with a small branch and leaves.

- **High-cut leotard:** the bodice continues into a leotard with leg openings cut high on the hips down to a narrow crotch. Rolled dark edges, center V lines continuing to the crotch, and back lines.
- **Leg vines:**
  - Her right: a round brown-purple thorny vine crossing the front of the thigh diagonally from the outer hip, then wrapping around the back. Hooked thorns and clusters of flat ivy leaves. A second thorny vine wraps across the knee.
  - Her left: a thin green vine climbing the front-outer thigh, with curly tendrils and leaves.
- **Knee-high boots:**
  - Green, each rising to a pointed leaf tip over the knee, with a rolled edge.
  - Line-art leaf panels (outline + midrib) drawn up the shin and on the outer side.
  - A dark sole and toe piping.

The boot soles reach about 0.04 studs below the original feet.

Skin color comes from the rig; a green-skin version would be a rig material
change. The hair is a separate head piece.

| File | What it is |
|---|---|
| `PoisonIvy_Morph.blend` | Rig with the morph on it (collection **Poison Ivy Morph**), studio lights, viewport set to Material Preview with scene lights |
| `PoisonIvy_Morph_PiecesOnly.blend` | Only the morph pieces, to append into your own rig file |
| `attach_to_rig.py` | After appending, run it in Blender's Text Editor to parent each piece to its body part |
| `build_ivy.py` | Builds everything: `python build_ivy.py <rig.blend> <out_dir>` (bpy) or `blender -b --python build_ivy.py -- <rig.blend> <out_dir>` |
| `previews/` | Quick low-res checks |
