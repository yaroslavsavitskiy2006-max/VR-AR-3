# -*- coding: utf-8 -*-
"""
Кейс 11. Кватернионы: поворот вектора взгляда

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   голова (Head), зелёный луч «взгляд вперёд» (+Y) до поворота
         и оранжевый луч после поворота на 90° по Z (-X);
         камера рендера направлена на объект Head (TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс11".
"""

import math

import bpy
import numpy as np


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


# ----------------------------- задание Кейса 11 -----------------------------
clear_scene()

# кватернион поворота на 90° вокруг оси Z: w = cos(t/2), xyz = ось * sin(t/2)
axis = np.array([0.0, 0.0, 1.0])
theta = math.radians(90.0)
w = math.cos(theta / 2.0)
x, y, z = axis * math.sin(theta / 2.0)
q = np.array([w, x, y, z])                      # (w, x, y, z)

# матрица поворота из кватерниона
rot = np.array([
    [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
    [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
    [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
])

forward = [0, 1, 0]                             # вектор взгляда «вперёд»
rotated = rot.dot(np.array(forward, dtype=float))
rotated[np.abs(rotated) < 1e-9] = 0.0           # убираем численный мусор (2e-16)

task_output = [
    "Кватернион (w,x,y,z): %s" % str(np.round(q, 3)),
    "Вектор взгляда до поворота: %s" % forward,
    "После поворота на 90 по Z: %s" % str(rotated),
]

# ------------------- визуализация направлений взгляда -------------------
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, 0.0, 1.0))
head = bpy.context.active_object
head.name = "Head"
head.scale = (0.5, 0.5, 0.5)
add_material(head, (0.7, 0.55, 0.45, 1.0), "Head_Material")

# взгляд «вперёд» (+Y) — до поворота
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, 1.0, 1.0))
before = bpy.context.active_object
before.name = "Gaze_Before"
before.scale = (0.15, 1.2, 0.15)
add_material(before, (0.15, 0.8, 0.25, 1.0), "Gaze_Before_Material")

# тот же взгляд после поворота на 90° по Z — «влево» (-X)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.0, 0.0, 1.0))
after = bpy.context.active_object
after.name = "Gaze_After"
after.scale = (1.2, 0.15, 0.15)
add_material(after, (0.95, 0.5, 0.1, 1.0), "Gaze_After_Material")

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(head, (3.5, -4.0, 3.5), lens=28.0)
add_sun()
setup_render("case11_render.png")

report(task_output, "Вывод_Кейс11")
