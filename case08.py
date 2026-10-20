# -*- coding: utf-8 -*-
"""
Кейс 8. Экспорт сцены в glTF (GLB) для VR-движка

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Камера:  направлена на объект VR_Cube (привязка TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс08".
         Файл vr_scene.glb сохраняется в папку временных файлов Windows.
"""

import os
import tempfile

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
    import math
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


# ----------------------------- задание Кейса 8 -----------------------------
clear_scene()

# --- собираем небольшую VR-сцену: куб + PBR-материал + свет + анимация ---
bpy.ops.mesh.primitive_cube_add(size=2, location=(0.0, 0.0, 1.0))
obj = bpy.context.active_object
obj.name = "VR_Cube"

mat = bpy.data.materials.new("VR_Material")
if bpy.app.version < (5, 0, 0):
    mat.use_nodes = True  # Blender 5+: у новых материалов узлы уже включены
bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf is not None:
    bsdf.inputs["Base Color"].default_value = (0.02, 0.2, 0.9, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
obj.data.materials.append(mat)

# короткая анимация, чтобы в GLB попали и данные анимации
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
obj.rotation_euler = (0.0, 0.0, 0.0)
obj.keyframe_insert(data_path="rotation_euler", frame=1)
obj.rotation_euler = (0.0, 0.0, 6.283185307179586)
obj.keyframe_insert(data_path="rotation_euler", frame=60)
scene.frame_set(1)

# --- экспорт в glTF 2.0 (бинарный .glb) ---
export_path = os.path.join(tempfile.gettempdir(), "vr_scene.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format='GLB')

task_output = [
    "Экспортировано в: %s" % export_path,
]

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(obj, (6.0, -6.0, 4.0), lens=35.0)
add_sun()
setup_render("case08_render.png")

report(task_output, "Вывод_Кейс08")
