# -*- coding: utf-8 -*-
"""
Кейс 6. Освещение VR-сцены (источник Sun)

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Камера:  направлена на объект VR_Cube (привязка TRACK_TO);
         свет — источник "VR_Sun" типа SUN, мощность 4.0.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс06".
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


# ----------------------------- задание Кейса 6 -----------------------------
clear_scene()

# объект, который освещается
bpy.ops.mesh.primitive_cube_add(size=2, location=(0.0, 0.0, 1.0))
obj = bpy.context.active_object
obj.name = "VR_Cube"

# направленный источник света
bpy.ops.object.light_add(type='SUN', location=(4.0, -4.0, 8.0))
sun_obj = bpy.context.active_object
sun_obj.name = "VR_Sun"
sun_obj.data.energy = 4.0
sun_obj.rotation_euler = (0.9, 0.0, 0.6)

task_output = [
    "Источник света: %s" % sun_obj.name,
    "Тип: %s | Мощность: %s" % (sun_obj.data.type, sun_obj.data.energy),
]

# ------------------- камера на объект и настройка рендера -------------------
add_camera(obj, (6.0, -6.0, 4.0), lens=35.0)
setup_render("case06_render.png")

report(task_output, "Вывод_Кейс06")
