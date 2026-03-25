"""
搞怪图片管理器 - 分目录管理各类型表情包
每个提醒类型有独立的图片目录，弹窗时随机选取一张

目录结构:
  ~/.fish_assistant/images/
    ├── drink_water/    💧 喝水提醒图片
    ├── kegel/          🍑 提肛提醒图片
    ├── fish_touch/     🐟 摸鱼提醒图片
    ├── rest_eyes/      👀 护眼提醒图片
    └── stretch/        🧘 伸展提醒图片

用户可以往对应目录放自己的表情包图片(.png/.jpg/.gif)，
程序会自动识别并随机展示。
"""

import os
import random
import hashlib
import logging
from pathlib import Path
from typing import List, Optional
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

logger = logging.getLogger("fish_assistant.images")

# 支持的图片格式
SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

# 所有提醒类型
ALL_REMINDER_TYPES = ["drink_water", "kegel", "fish_touch", "rest_eyes", "stretch"]


class FunnyImageManager:
    """搞怪图片管理器 - 在线表情包 + 本地占位图"""

    # ── 在线搞怪表情包 URL ──
    # 使用公共 CDN 上的搞笑/提醒风格表情（开源 Emoji + 搞笑贴纸）
    ONLINE_IMAGE_URLS = {
        "drink_water": [
            # 开源 Twemoji 大号表情
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4a7.png",  # 💧
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f964.png",  # 🥤
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6b0.png",  # 🚰
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2615.png",   # ☕
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f376.png",  # 🍶
            # OpenMoji 大号 (256px)
            "https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@15.0/color/svg/1F4A7.svg",  # 💧
            "https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@15.0/color/svg/1F964.svg",  # 🥤
        ],
        "kegel": [
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f351.png",  # 🍑
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4aa.png",  # 💪
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f3cb.png",  # 🏋
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2b06.png",   # ⬆
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2b07.png",   # ⬇
            # OpenMoji
            "https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@15.0/color/svg/1F351.svg",  # 🍑
        ],
        "fish_touch": [
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f41f.png",  # 🐟
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6a8.png",  # 🚨
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4e1.png",  # 📡
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f420.png",  # 🐠
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f421.png",  # 🐡
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f419.png",  # 🐙
            # OpenMoji
            "https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@15.0/color/svg/1F41F.svg",  # 🐟
        ],
        "rest_eyes": [
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f441.png",  # 👁
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f60e.png",  # 😎
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f30f.png",  # 🌏
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f333.png",  # 🌳
        ],
        "stretch": [
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9d8.png",  # 🧘
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f3c3.png",  # 🏃
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f483.png",  # 💃
            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f57a.png",  # 🕺
        ],
    }

    # ── 搞笑表情包文字模板（用于生成本地表情包图片）──
    MEME_TEMPLATES = {
        "drink_water": [
            {"emoji": "💧", "top": "你不喝水", "bottom": "你变干尸"},
            {"emoji": "🥤", "top": "老板都喝3杯了", "bottom": "你还不动？"},
            {"emoji": "🚰", "top": "再不喝水", "bottom": "鱼都替你渴"},
            {"emoji": "💦", "top": "多喝热水", "bottom": "包治百病"},
            {"emoji": "🍵", "top": "喝水不积极", "bottom": "思想有问题"},
        ],
        "kegel": [
            {"emoji": "🍑", "top": "提肛时间到", "bottom": "偷偷提 谁也不知"},
            {"emoji": "💪", "top": "悄悄提肛", "bottom": "惊艳所有人"},
            {"emoji": "🏋️", "top": "菊花一紧", "bottom": "天下我有"},
            {"emoji": "🍑", "top": "提！放！提！放！", "bottom": "你是最棒的"},
            {"emoji": "😏", "top": "办公室最隐蔽", "bottom": "的健身运动"},
        ],
        "fish_touch": [
            {"emoji": "🐟", "top": "你摸鱼了", "bottom": "老板在你身后"},
            {"emoji": "🚨", "top": "摸鱼警报", "bottom": "危险指数MAX"},
            {"emoji": "📡", "top": "摸鱼雷达", "bottom": "已锁定你"},
            {"emoji": "👔", "top": "老板巡视中", "bottom": "快切屏！！"},
            {"emoji": "🐟", "top": "这鱼你摸了1小时", "bottom": "换条鱼摸摸？"},
        ],
        "rest_eyes": [
            {"emoji": "👀", "top": "你的眼睛", "bottom": "快瞎了"},
            {"emoji": "😎", "top": "看远方20秒", "bottom": "拯救你的视力"},
            {"emoji": "🌳", "top": "看看窗外", "bottom": "别当睁眼瞎"},
        ],
        "stretch": [
            {"emoji": "🧘", "top": "你已经坐了", "bottom": "整整一个世纪"},
            {"emoji": "💃", "top": "站起来嗨", "bottom": "脊椎感谢你"},
            {"emoji": "🏃", "top": "再不站起来", "bottom": "椅子跟你长一起"},
        ],
    }

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = str(Path.home() / ".fish_assistant" / "images")
        self._cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # 为每个提醒类型创建独立子目录
        for rtype in ALL_REMINDER_TYPES:
            type_dir = os.path.join(cache_dir, rtype)
            os.makedirs(type_dir, exist_ok=True)

        logger.info(f"Image manager initialized, root: {cache_dir}")
        logger.info(f"  Subdirs: {ALL_REMINDER_TYPES}")

    def _type_dir(self, reminder_type: str) -> str:
        """获取指定类型的图片目录路径"""
        return os.path.join(self._cache_dir, reminder_type)

    # ── 生成表情包风格图片（本地生成，不依赖网络）──

    def generate_meme_image(
        self,
        reminder_type: str,
        size: tuple = (400, 400),
    ) -> Optional[str]:
        """
        生成表情包风格的搞笑提醒图片，保存到对应类型的子目录。
        返回图片文件路径。每次随机选择一个模板。
        """
        templates = self.MEME_TEMPLATES.get(reminder_type, [])
        if not templates:
            templates = [{"emoji": "🐟", "top": "该休息了", "bottom": "你太卷了"}]
        tmpl = random.choice(templates)
        return self._render_meme(
            reminder_type=reminder_type,
            emoji=tmpl["emoji"],
            top_text=tmpl["top"],
            bottom_text=tmpl["bottom"],
            size=size,
        )

    def _render_meme(
        self,
        reminder_type: str,
        emoji: str,
        top_text: str,
        bottom_text: str,
        size: tuple = (400, 400),
    ) -> Optional[str]:
        """渲染一张表情包图片并保存到对应类型的子目录"""
        if Image is None:
            return None

        # 随机选背景色，模拟不同"表情包风格"
        bg_colors = [
            "#FF6B35", "#2EC4B6", "#FF6B9D", "#45B7D1", "#4ECDC4",
            "#FFA62B", "#6C5CE7", "#00B894", "#E17055", "#FDCB6E",
        ]
        bg = random.choice(bg_colors)

        img = Image.new('RGB', size, bg)
        draw = ImageDraw.Draw(img)

        # 查找中文字体
        font_large = None
        font_medium = None
        font_small = None
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font_large = ImageFont.truetype(fp, size[0] // 5)
                    font_medium = ImageFont.truetype(fp, size[0] // 10)
                    font_small = ImageFont.truetype(fp, size[0] // 14)
                    break
                except Exception:
                    continue

        if font_large is None:
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large

        # 白色半透明描边效果
        white = "#FFFFFF"
        shadow = "#00000066"

        # 绘制顶部文字（白色大字 + 阴影）
        top_bbox = draw.textbbox((0, 0), top_text, font=font_medium)
        tw = top_bbox[2] - top_bbox[0]
        tx = (size[0] - tw) // 2
        ty = size[1] // 10
        # 阴影
        draw.text((tx + 2, ty + 2), top_text, fill="#000000", font=font_medium)
        draw.text((tx, ty), top_text, fill=white, font=font_medium)

        # 绘制中间大 Emoji
        emoji_bbox = draw.textbbox((0, 0), emoji, font=font_large)
        ew = emoji_bbox[2] - emoji_bbox[0]
        ex = (size[0] - ew) // 2
        ey = size[1] // 3
        draw.text((ex, ey), emoji, fill=white, font=font_large)

        # 绘制底部文字
        bot_bbox = draw.textbbox((0, 0), bottom_text, font=font_medium)
        bw = bot_bbox[2] - bot_bbox[0]
        bx = (size[0] - bw) // 2
        by = size[1] * 7 // 10
        draw.text((bx + 2, by + 2), bottom_text, fill="#000000", font=font_medium)
        draw.text((bx, by), bottom_text, fill=white, font=font_medium)

        # 保存到对应类型的子目录
        type_dir = self._type_dir(reminder_type)
        filename = f"meme_{random.randint(0, 99999):05d}.png"
        filepath = os.path.join(type_dir, filename)
        try:
            img.save(filepath)
            return filepath
        except Exception:
            return None

    def get_random_meme(self, reminder_type: str) -> Optional[str]:
        """
        获取一张搞笑表情包（从对应类型的子目录随机取）：
        1. 先从子目录中已有图片（用户自定义 + 生成的）随机选
        2. 没有则生成一张并保存
        """
        images = self._find_images_in_dir(reminder_type)
        if images:
            chosen = random.choice(images)
            logger.debug(f"Random meme for [{reminder_type}]: {os.path.basename(chosen)}")
            return chosen
        # 没有任何图片，生成一张
        logger.info(f"No images found for [{reminder_type}], generating...")
        return self.generate_meme_image(reminder_type)

    def generate_placeholder_image(
        self,
        text: str,
        emoji: str,
        size: tuple = (300, 300),
        bg_color: str = "#FF6B35",
        text_color: str = "#FFFFFF",
    ) -> Optional[object]:
        """
        生成一个搞怪的占位图片（Pillow Image对象）
        用于在无法下载在线图片时显示
        """
        if Image is None:
            return None

        img = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(img)

        font_large = None
        font_small = None
        try:
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "/System/Library/Fonts/PingFang.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            ]
            for fp in font_paths:
                if os.path.exists(fp):
                    font_large = ImageFont.truetype(fp, 36)
                    font_small = ImageFont.truetype(fp, 20)
                    break
        except Exception:
            pass

        if font_large is None:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), emoji, font=font_large)
        tw = bbox[2] - bbox[0]
        x = (size[0] - tw) // 2
        draw.text((x, size[1] // 3), emoji, fill=text_color, font=font_large)

        # 绘制小文字（中心偏下）
        for i, line in enumerate(text.split('\n')):
            bbox = draw.textbbox((0, 0), line, font=font_small)
            tw = bbox[2] - bbox[0]
            x = (size[0] - tw) // 2
            y = size[1] // 2 + i * 30
            draw.text((x, y), line, fill=text_color, font=font_small)

        return img

    def download_image(self, url: str) -> Optional[bytes]:
        """下载图片并返回字节数据"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception:
            pass
        return None

    def get_cached_or_download(
        self, url: str, reminder_type: str = ""
    ) -> Optional[str]:
        """获取缓存的图片路径，如果不存在则下载到对应类型子目录"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        ext = os.path.splitext(url)[-1] or ".png"
        # 保存到类型子目录（若有），否则根目录
        if reminder_type and reminder_type in ALL_REMINDER_TYPES:
            save_dir = self._type_dir(reminder_type)
        else:
            save_dir = self._cache_dir
        cache_path = os.path.join(save_dir, f"{url_hash}{ext}")

        if os.path.exists(cache_path):
            return cache_path

        data = self.download_image(url)
        if data:
            try:
                with open(cache_path, 'wb') as f:
                    f.write(data)
                return cache_path
            except IOError:
                pass

        return None

    def get_images_for_type(self, reminder_type: str) -> List[str]:
        """
        获取指定提醒类型的所有可用图片路径。
        1. 先返回子目录中已有的本地图片
        2. 再尝试在线下载到子目录
        """
        # 本地已有
        paths = self._find_images_in_dir(reminder_type)
        # 在线下载
        urls = self.ONLINE_IMAGE_URLS.get(reminder_type, [])
        for url in urls:
            path = self.get_cached_or_download(url, reminder_type)
            if path and path not in paths:
                paths.append(path)
        return paths

    def _find_images_in_dir(self, reminder_type: str) -> List[str]:
        """
        查找指定类型子目录中所有图片文件。
        支持用户自定义放入的图片 + 程序生成的meme图。
        """
        type_dir = self._type_dir(reminder_type)
        results = []
        try:
            for f in os.listdir(type_dir):
                ext = os.path.splitext(f)[1].lower()
                if ext in SUPPORTED_IMAGE_EXTS:
                    results.append(os.path.join(type_dir, f))
        except OSError:
            pass
        return results

    def _find_cached(self, reminder_type: str) -> List[str]:
        """向后兼容：查找缓存目录中已有的图片"""
        return self._find_images_in_dir(reminder_type)

    def preload_memes(self, count: int = 3):
        """预加载每种类型的表情包到各自子目录，启动时调用"""
        for rtype in ALL_REMINDER_TYPES:
            existing = len(self._find_images_in_dir(rtype))
            need = max(0, count - existing)
            for _ in range(need):
                self.generate_meme_image(rtype)
            total = len(self._find_images_in_dir(rtype))
            logger.info(f"  [{rtype}] {total} images ready (generated {need} new)")
