import bpy, math
from mathutils import Vector

def setup_render(res=(700, 1000), samples=48):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg is None:
        bg = nt.nodes.new('ShaderNodeBackground')
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None) or nt.nodes.new('ShaderNodeOutputWorld')
        nt.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[0].default_value = (0.045, 0.045, 0.045, 1)
    bg.inputs[1].default_value = 1.0
    # lights: key, fill, rim (studio look similar to Blender's viewport matcap)
    for n in [o for o in bpy.data.objects if o.name.startswith('_RL_')]:
        bpy.data.objects.remove(n)
    def light(name, typ, energy, loc, size=3):
        ld = bpy.data.lights.new(name, typ); ld.energy = energy
        if typ == 'AREA': ld.size = size
        o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o)
        o.location = loc
        d = Vector((0, 0, 2.8)) - Vector(loc)
        o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return o
    # rig faces +Y
    light('_RL_key', 'AREA', 900, (-3.5, 5, 6), 4)
    light('_RL_fill', 'AREA', 400, (4.5, 4, 3), 5)
    light('_RL_rim', 'AREA', 700, (1.5, -5, 5), 3)
    light('_RL_rim2', 'AREA', 350, (-3, -4, 2), 3)
    light('_RL_top', 'AREA', 250, (0, 1, 8), 4)

def render_view(path, loc, target=(0, 0, 2.9), lens=60, res=None):
    sc = bpy.context.scene
    if res: sc.render.resolution_x, sc.render.resolution_y = res
    cam = bpy.data.objects.get('_RL_cam')
    if not cam:
        cam = bpy.data.objects.new('_RL_cam', bpy.data.cameras.new('_RL_cam'))
        sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
