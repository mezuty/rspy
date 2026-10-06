"""Run in Blender's Text Editor after appending the 'Catwoman Morph (Top)'
collection into your Starter 2.0 Rig file. Parents every morph piece to the
body part it belongs to (stored in its 'morph_target' property), keeping its
current position."""
import bpy

for ob in bpy.data.collections['Catwoman Morph (Top)'].objects:
    target = bpy.data.objects.get(ob.get('morph_target', ''))
    if target is None:
        print('no target for', ob.name)
        continue
    mw = ob.matrix_world.copy()
    ob.parent = target
    ob.matrix_parent_inverse = target.matrix_world.inverted()
    ob.matrix_world = mw
print('Catwoman morph attached')
