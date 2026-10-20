# -*- coding: utf-8 -*-
"""
Кейс 9. Стереокамеры: расчёт позиций левого и правого глаза

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   голова (Head) и две камеры-глаза (Eye_L, Eye_R) в позициях из расчёта;
         камера рендера направлена на объект Head (TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс09".
"""

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
        bsdf.inputs["Roughness"].default_value = 0.4
    obj.data.materials.append(mat)


# ----------------------------- задание Кейса 9 -----------------------------
clear_scene()

head_pos = np.array([0.0, -2.0, 1.6])      # позиция головы
ipd = 0.065                                # межзрачковое расстояние, м
right_dir = np.array([1.0, 0.0, 0.0])      # локальная ось «вправо»

left_pos = head_pos - right_dir * (ipd / 2.0)
right_pos = head_pos + right_dir * (ipd / 2.0)
distance = float(np.linalg.norm(right_pos - left_pos))

task_output = [
    "Левый глаз:  %s" % str(left_pos),
    "Правый глаз: %s" % str(right_pos),
    "Расстояние между камерами: %s м" % round(distance, 3),
]

# ------------------- визуализация: голова и два «глаза» -------------------
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=tuple(head_pos))
head = bpy.context.active_object
head.name = "Head"
add_material(head, (0.7, 0.55, 0.45, 1.0), "Head_Material")

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=tuple(left_pos))
eye_l = bpy.context.active_object
eye_l.name = "Eye_L"
add_material(eye_l, (0.1, 0.6, 0.9, 1.0), "Eye_L_Material")

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=tuple(right_pos))
eye_r = bpy.context.active_object
eye_r.name = "Eye_R"
add_material(eye_r, (0.9, 0.25, 0.15, 1.0), "Eye_R_Material")

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(head, (0.0, -4.5, 1.75), lens=35.0)
add_sun()
setup_render("case09_render.png")

report(task_output, "Вывод_Кейс09")
