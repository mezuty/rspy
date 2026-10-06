import bpy
# Run in Blender's Text Editor after appending the morph collection.
COLL_NAME = "Harley Quinn Morph"
for ob in bpy.data.collections[COLL_NAME].objects:
    target = bpy.data.objects.get(ob.get("morph_target", ""))
    if target is None:
        print("no target for", ob.name); continue
    mw = ob.matrix_world.copy()
    ob.parent = target
    ob.matrix_parent_inverse = target.matrix_world.inverted()
    ob.matrix_world = mw
print("morph attached")
