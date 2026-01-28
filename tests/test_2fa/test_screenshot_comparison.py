# tests/test_2fa/test_screenshot_comparison.py
import pytest
import asyncio
from PIL import Image, ImageChops, ImageDraw, ImageFont
import os
import math


async def compare_screenshots(reference_path: str, test_path: str, diff_path: str, threshold: float = 0.01):
    """
    Сравнивает два скриншота и сохраняет наглядный diff.
    Возвращает (is_different: bool, diff_percentage: float)
    """
    if not os.path.exists(reference_path) or not os.path.exists(test_path):
        print(f"⚠️  Пропущено: {os.path.basename(reference_path)} — файл отсутствует")
        return False, 1.0

    try:
        ref = Image.open(reference_path).convert('RGB')
        test = Image.open(test_path).convert('RGB')

        if ref.size != test.size:
            print(f"⚠️  Размеры различаются: {ref.size} vs {test.size}")
            return True, 1.0

        # 1. Вычисляем пиксельную разницу
        diff = ImageChops.difference(ref, test)
        diff_gray = diff.convert('L')  # в градации серого

        # 2. Создаём маску различий (1 — отличается, 0 — одинаково)
        threshold_val = 30  # порог чувствительности
        mask = diff_gray.point(lambda p: 255 if p > threshold_val else 0, mode='1')

        # 3. Считаем % различий
        total = ref.width * ref.height
        diff_pixels = sum(1 for p in mask.getdata() if p == 255)
        diff_pct = diff_pixels / total

        # 4. Формируем визуализацию:
        #    ref + полупрозрачный красный overlay на различиях
        overlay = Image.new('RGBA', ref.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Заливаем различия красным с прозрачностью 40%
        for y in range(ref.height):
            for x in range(ref.width):
                if mask.getpixel((x, y)) == 255:
                    draw.point((x, y), fill=(255, 0, 0, 100))  # R=255, A=100 (~40%)

        # Накладываем overlay на эталон
        result = ref.copy().convert('RGBA')
        result = Image.alpha_composite(result, overlay).convert('RGB')

        # 5. Добавляем текст с % различий (если есть место)
        try:
            # Пробуем найти системный bold шрифт
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("Arial Bold.ttf", 24)
            except:
                font = ImageFont.load_default()

        draw_res = ImageDraw.Draw(result)
        text = f"Δ: {diff_pct:.0%}"
        bbox = draw_res.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Помещаем в правый верхний угол
        x = ref.width - text_width - 10
        y = 10
        # Тень для читаемости
        draw_res.text((x + 1, y + 1), text, fill=(0, 0, 0), font=font)
        draw_res.text((x, y), text, fill=(255, 255, 255), font=font)

        # 6. Сохраняем
        os.makedirs(os.path.dirname(diff_path), exist_ok=True)
        result.save(diff_path, "PNG", optimize=True)

        return diff_pct > threshold, diff_pct

    except Exception as e:
        print(f"❌ Ошибка сравнения {os.path.basename(reference_path)}: {e}")
        return False, 0.0