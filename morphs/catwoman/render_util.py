import bpy, math
from mathutils import Vector

LIGHTS_COLL = 'CW Studio Lights'
WORLD = 'CW_Studio_World'


def add_studio_look(sc=None):
    """Grey studio background + soft key/fill/rim area lights (rig faces +Y).
    Idempotent: reuses the lights/world if they already exist in the file."""
    sc = sc or bpy.context.scene
    w = bpy.data.worlds.get(WORLD) or bpy.data.worlds.new(WORLD)
    sc.world = w
    nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg is None:
        bg = nt.nodes.new('ShaderNodeBackground')
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None) or nt.nodes.new('ShaderNodeOutputWorld')
        nt.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[0].default_value = (0.045, 0.045, 0.045, 1)
    bg.inputs[1].default_value = 1.0
    sc.view_settings.view_transform = 'AgX'
    if LIGHTS_COLL in bpy.data.collections:
        return
    coll = bpy.data.collections.new(LIGHTS_COLL)
    sc.collection.children.link(coll)

    def light(name, energy, loc, size):
        ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size
        o = bpy.data.objects.new(name, ld); coll.objects.link(o)
        o.location = loc
        d = Vector((0, 0, 2.5)) - Vector(loc)
        o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

    light('CW_Light_Key', 1000, (-3.5, 5, 6), 4)
    light('CW_Light_Fill', 450, (4.5, 4, 3), 5)
    light('CW_Light_Rim', 750, (1.5, -5, 5), 3)
    light('CW_Light_Rim2', 400, (-3, -4, 2), 3)
    light('CW_Light_Top', 250, (0, 1, 8), 4)
    light('CW_Light_Low', 200, (0, 5, 0.3), 4)   # lifts the boots out of the shadows


def setup_render(res=(700, 1000), samples=48):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    add_studio_look(sc)


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
