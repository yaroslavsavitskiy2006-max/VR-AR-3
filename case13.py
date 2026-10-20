# -*- coding: utf-8 -*-
"""
Кейс 13. Выбор уровня детализации (LOD) по расстоянию

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   три сферы-уровня: LOD0 (1280 тр.), LOD1 (80 тр.), LOD2 (20 тр.);
         камера рендера направлена на объект LOD1 (TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс13".
"""

import bpy


# ------------------------- вспомогательные функции -------------------------
def clear_scene():
    """Удаляет все объекты и неиспользуемые данные — сцена готова под задание."""
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                       bpy.data.lights, bpy.data.actions, bpy.data.curves):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def report(lines, block_name):
    """Печатает результат в консоль и записывает его в текстовый блок Blender."""
    for line in lines:
        print(line)
    text = bpy.data.texts.get(block_name)
    if text is None:
        text = bpy.data.texts.new(block_name)
    if hasattr(text, "clear"):
        text.clear()
    text.write("\n".join(lines) + "\n")


def add_camera(target, location, lens=35.0, name="Camera"):
    """Камера, автоматически направленная на объект target."""
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = location
    con = cam.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam


def add_sun(name="Sun", energy=4.0, location=(5.0, -5.0, 8.0)):
    """Направленный свет, чтобы рендер не был чёрным."""
    sun_data = bpy.data.lights.new(name, type='SUN')
    sun_data.energy = energy
    sun = bpy.data.objects.new(name, sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.location = location
    sun.rotation_euler = (0.9, 0.0, 0.6)
    return sun


def setup_render(filename):
    """Быстрый движок рендера, 1920x1080, путь для итогового PNG."""
    import os
    import tempfile
    scene = bpy.context.scene
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.use_multiview = False  # сброс стерео от прошлых прогонов
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(tempfile.gettempdir(), filename)


def add_material(obj, color, name):
    """Назначает объекту простой PBR-материал с заданным цветом."""
    mat = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True  # Blender 5+: у новых материалов узлы уже включены
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.append(mat)


def choose_lod(dist):
    """Пороги по возрастанию: до 10 м — LOD0, до 35 м — LOD1, до 80 м — LOD2."""
    if dist < 10:
        return "LOD0 (высокая детализация)"
    if dist < 35:
        return "LOD1 (средняя)"
    if dist < 80:
        return "LOD2 (низкая)"
    return "culled (не рендерится)"


# ----------------------------- задание Кейса 13 -----------------------------
clear_scene()

task_output = []
for d in (2, 10, 35, 80):
    task_output.append("%3d м -> %s" % (d, choose_lod(d)))

# ------------------- визуализация: три уровня детализации -------------------
lod_specs = (
    ("LOD0", -3.5, 4, (0.15, 0.75, 0.25, 1.0)),   # высокая детализация (1280 тр.)
    ("LOD1", 0.0, 2, (0.95, 0.75, 0.1, 1.0)),     # средняя (80 тр.)
    ("LOD2", 3.5, 1, (0.9, 0.35, 0.1, 1.0)),      # низкая (20 тр.)
)
lod_objects = {}
for name, x, subdiv, color in lod_specs:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=1.0,
                                          location=(x, 0.0, 1.2))
    sphere = bpy.context.active_object
    sphere.name = name
    add_material(sphere, color, name + "_Material")
    lod_objects[name] = sphere

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(lod_objects["LOD1"], (0.0, -9.0, 4.0), lens=35.0)
add_sun()
setup_render("case13_render.png")

report(task_output, "Вывод_Кейс13")
