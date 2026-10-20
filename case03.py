# -*- coding: utf-8 -*-
"""
Кейс 3. Настройка стереокамеры для VR (multiview)

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12) — кадры для левого и правого глаза.
Камера:  "VR_Camera" направлена на объект VR_Cube (TRACK_TO).
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс03".
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
    """Настройки рендера: 1920x1080, путь для итогового PNG (движок задаётся ниже)."""
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


# ----------------------------- задание Кейса 3 -----------------------------
clear_scene()
scene = bpy.context.scene

# объект — чтобы камера и рендер имели на что смотреть
bpy.ops.mesh.primitive_cube_add(size=2, location=(0.0, 0.0, 1.0))
obj = bpy.context.active_object
obj.name = "VR_Cube"

# стереокамера (настройки стерео — ПОСЛЕ setup_render, он сбрасывает multiview)
cam = add_camera(obj, (0.0, -5.0, 2.0), lens=35.0, name="VR_Camera")

add_sun(energy=4.0)
setup_render("case03_render.png")

scene.render.use_multiview = True
scene.render.views_format = 'STEREO_3D'
cam.data.stereo.interocular_distance = 0.065

task_output = [
    "Стерео включено: %s" % scene.render.use_multiview,
    "Межзрачковое расстояние, м: %s" % round(cam.data.stereo.interocular_distance, 3),
]

# стереоскопия (multiview) надёжнее всего работает в Cycles
try:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
except Exception:
    pass

report(task_output, "Вывод_Кейс03")
