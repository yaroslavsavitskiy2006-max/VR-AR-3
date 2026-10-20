# -*- coding: utf-8 -*-
"""
Кейс 12. Бюджет кадра для частоты VR-дисплея

Запуск:  Blender -> Text Editor -> Open -> Run Script (Alt+P)
Рендер:  Render -> Render Image (F12)
Сцена:   столбчатая диаграмма: 3 синих столбца — бюджеты кадра (72/90/120 Гц),
         оранжевый — фактическое время рендера 9.5 мс;
         камера рендера направлена на центр диаграммы (TRACK_TO), добавлен свет.
Вывод:   консоль Blender и текстовый блок "Вывод_Кейс12".
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


def make_bar(name, x, height_m, color, scale=0.5, width=1.2):
    """Столбец диаграммы: высота = значение * scale (моделирование в метрах)."""
    h = height_m * scale
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.0, h / 2.0))
    bar = bpy.context.active_object
    bar.name = name
    bar.scale = (width, width, h)
    add_material(bar, color, name + "_Material")
    return bar


# ----------------------------- задание Кейса 12 -----------------------------
clear_scene()

budgets = []
for hz in (72, 90, 120):
    budgets.append(1000.0 / hz)

render_ms = 9.5
budget_90 = 1000.0 / 90.0
fits = render_ms <= budget_90

task_output = [
    "72 Гц -> бюджет кадра %.2f мс" % budgets[0],
    "90 Гц -> бюджет кадра %.2f мс" % budgets[1],
    "120 Гц -> бюджет кадра %.2f мс" % budgets[2],
    "Рендер %s мс при 90 Гц (%.2f мс): %s"
    % (render_ms, budget_90, "успеваем" if fits else "не успеваем"),
]

# ------------------- визуализация: диаграмма бюджета кадра -------------------
blue = (0.1, 0.35, 0.9, 1.0)
orange = (0.95, 0.45, 0.05, 1.0)

make_bar("Budget_72Hz", -4.5, budgets[0], blue)
make_bar("Budget_90Hz", -1.5, budgets[1], blue)
make_bar("Budget_120Hz", 1.5, budgets[2], blue)
make_bar("Render_Time", 4.5, render_ms, orange)

# ориентир для камеры — по центру диаграммы
focus = bpy.data.objects.new("Focus", None)
bpy.context.scene.collection.objects.link(focus)
focus.location = (0.0, 0.0, 4.5)

# ------------------- камера на объект, свет, настройка рендера -------------------
add_camera(focus, (0.0, -16.0, 5.5), lens=35.0)
add_sun()
setup_render("case12_render.png")

report(task_output, "Вывод_Кейс12")
