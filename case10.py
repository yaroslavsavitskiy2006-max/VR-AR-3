# -*- coding: utf-8 -*-
"""
Кейс 10. Поле зрения (FOV) и размер объекта в кадре

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   камера с FOV = 100° смотрит на объект шириной 2 м с расстояния 5 м
         (камера направлена на объект через TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс10".
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


# ----------------------------- задание Кейса 10 -----------------------------
clear_scene()

fov_deg = 100.0          # поле зрения VR-шлема, град
distance = 5.0           # расстояние до объекта, м
obj_width = 2.0          # ширина объекта, м

visible_width = 2.0 * distance * math.tan(math.radians(fov_deg) / 2.0)
share_pct = obj_width / visible_width * 100.0

task_output = [
    "FOV = %s град, расстояние = %s м" % (fov_deg, distance),
    "Ширина видимой области: %.2f м" % visible_width,
    "Объект шириной %.1f м занимает %.1f%% ширины кадра" % (obj_width, share_pct),
]

# ------------------- визуализация: объект в кадре камеры -------------------
bpy.ops.mesh.primitive_cube_add(size=obj_width, location=(0.0, 0.0, obj_width / 2.0))
obj = bpy.context.active_object
obj.name = "VR_Object"
add_material(obj, (0.9, 0.55, 0.1, 1.0), "VR_Object_Material")

# камера ровно с заданным FOV и на расстоянии 5 м от центра объекта
cam = add_camera(obj, (0.0, -distance, obj_width / 2.0), lens=35.0)
cam.data.angle = math.radians(fov_deg)

add_sun()
setup_render("case10_render.png")

report(task_output, "Вывод_Кейс10")
