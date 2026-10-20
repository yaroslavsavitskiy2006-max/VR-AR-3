# -*- coding: utf-8 -*-
"""
Кейс 14. Полигональный бюджет VR-сцены

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   сетка 15x10 из 150 кубов: первые 125 (в бюджете) — зелёные,
         оставшиеся 25 (превышение) — красные;
         камера рендера направлена на центральный куб Obj_067 (TRACK_TO), свет добавлен.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс14".
"""

import bmesh
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


def make_cube_mesh(name, color, size=0.8):
    """Создаёт один меш-куб с материалом; им будут пользоваться все копии."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh)
    bm.free()

    mat = bpy.data.materials.new(name + "_Material")
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True  # Blender 5+: у новых материалов узлы уже включены
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.5
    mesh.materials.append(mat)
    return mesh


# ----------------------------- задание Кейса 14 -----------------------------
clear_scene()
scene = bpy.context.scene

scene_budget = 1_000_000        # бюджет сцены, треугольников
tris_per_object = 8_000         # треугольников на объект
max_objects = scene_budget // tris_per_object
planned_objects = 150
total_load = planned_objects * tris_per_object
in_budget = total_load <= scene_budget

task_output = [
    "Бюджет сцены: {0:,} тр., на объект: {1:,} тр.".format(scene_budget, tris_per_object),
    "Максимум объектов в бюджете: %d" % max_objects,
    "Сцена из {0} объектов = {1:,} тр. -> {2}".format(
        planned_objects, total_load, "в бюджете" if in_budget else "ПРЕВЫШЕН бюджет"
    ),
]

# ------------------- визуализация: 150 объектов сцены -------------------
mesh_ok = make_cube_mesh("Obj_OK", (0.15, 0.75, 0.25, 1.0))     # в бюджете
mesh_over = make_cube_mesh("Obj_Over", (0.9, 0.15, 0.1, 1.0))    # превышение

cols, rows = 15, 10
step = 1.2
center_obj = None

for i in range(planned_objects):
    col = i % cols
    row = i // cols
    mesh = mesh_ok if i < max_objects else mesh_over
    obj = bpy.data.objects.new("Obj_%03d" % i, mesh)
    obj.location = ((col - (cols - 1) / 2.0) * step,
                    (row - (rows - 1) / 2.0) * step,
                    0.4)
    scene.collection.objects.link(obj)
    if i == 67:                      # куб примерно в центре сетки — цель камеры
        center_obj = obj

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(center_obj, (13.0, -15.0, 11.0), lens=28.0)
add_sun()
setup_render("case14_render.png")

report(task_output, "Вывод_Кейс14")
