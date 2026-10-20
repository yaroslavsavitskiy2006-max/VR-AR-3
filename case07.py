# -*- coding: utf-8 -*-
"""
Кейс 7. Анимация вращения (ключевые кадры)

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12) — рендерится текущий кадр 15 (половина оборота)
Камера:  направлена на объект VR_Cube (привязка TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс07".
"""

import math

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


# ----------------------------- задание Кейса 7 -----------------------------
clear_scene()
scene = bpy.context.scene

bpy.ops.mesh.primitive_cube_add(size=2, location=(0.0, 0.0, 1.0))
obj = bpy.context.active_object
obj.name = "VR_Cube"

# полный оборот вокруг Z (2*пи радиан) за 60 кадров — два ключевых кадра
scene.frame_start = 1
scene.frame_end = 60
inserted = 0

obj.rotation_euler = (0.0, 0.0, 0.0)
obj.keyframe_insert(data_path="rotation_euler", frame=1)
inserted += 1

obj.rotation_euler = (0.0, 0.0, 2.0 * math.pi)
obj.keyframe_insert(data_path="rotation_euler", frame=60)
inserted += 1

scene.frame_set(15)  # текущий кадр для рендера — середина анимации

task_output = [
    "Анимация: кадры %d - %d" % (scene.frame_start, scene.frame_end),
    "Ключевых кадров вставлено: %d" % inserted,
]

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(obj, (6.0, -6.0, 4.0), lens=35.0)
add_sun()
setup_render("case07_render.png")

report(task_output, "Вывод_Кейс07")
