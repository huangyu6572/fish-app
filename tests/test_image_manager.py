"""
测试 - FunnyImageManager 搞怪图片管理
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from core.image_manager import FunnyImageManager, ALL_REMINDER_TYPES, SUPPORTED_IMAGE_EXTS


class TestFunnyImageManager:
    """搞怪图片管理器测试"""

    @pytest.fixture
    def temp_cache(self, tmp_path):
        return str(tmp_path / "test_images")

    @pytest.fixture
    def manager(self, temp_cache):
        return FunnyImageManager(cache_dir=temp_cache)

    def test_creates_cache_dir(self, temp_cache):
        FunnyImageManager(cache_dir=temp_cache)
        assert os.path.isdir(temp_cache)

    def test_creates_type_subdirs(self, manager, temp_cache):
        """每个提醒类型都应该有独立的子目录"""
        for rtype in ALL_REMINDER_TYPES:
            subdir = os.path.join(temp_cache, rtype)
            assert os.path.isdir(subdir), f"Missing subdir for {rtype}"

    def test_online_urls_has_all_types(self, manager):
        expected_types = ["drink_water", "kegel", "fish_touch", "rest_eyes", "stretch"]
        for t in expected_types:
            assert t in FunnyImageManager.ONLINE_IMAGE_URLS

    def test_each_type_has_urls(self):
        for key, urls in FunnyImageManager.ONLINE_IMAGE_URLS.items():
            assert len(urls) >= 2, f"{key} should have at least 2 image URLs"

    def test_urls_are_valid_format(self):
        for key, urls in FunnyImageManager.ONLINE_IMAGE_URLS.items():
            for url in urls:
                assert url.startswith("https://"), f"URL should start with https: {url}"
                assert any(ext in url for ext in [".png", ".svg", ".jpg"]), \
                    f"URL should be an image format: {url}"

    def test_generate_placeholder_image(self, manager):
        try:
            img = manager.generate_placeholder_image("喝水啦!", "💧")
            if img is not None:
                assert img.size == (300, 300)
        except ImportError:
            pytest.skip("Pillow not installed")

    def test_generate_placeholder_custom_size(self, manager):
        try:
            img = manager.generate_placeholder_image(
                "Test", "🐟", size=(200, 200)
            )
            if img is not None:
                assert img.size == (200, 200)
        except ImportError:
            pytest.skip("Pillow not installed")

    def test_download_image_with_invalid_url(self, manager):
        result = manager.download_image("https://invalid.url.test/image.png")
        assert result is None

    def test_get_cached_or_download_invalid_url(self, manager):
        result = manager.get_cached_or_download("https://invalid.url.test/img.png")
        assert result is None

    def test_get_cached_returns_cached_file(self, manager, temp_cache):
        # 手动创建一个缓存文件
        import hashlib
        url = "https://example.com/test.png"
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(temp_cache, f"{url_hash}.png")
        with open(cache_path, 'wb') as f:
            f.write(b"fake png data")

        result = manager.get_cached_or_download(url)
        assert result == cache_path

    def test_get_images_for_unknown_type(self, manager):
        paths = manager.get_images_for_type("unknown_type")
        assert paths == []

    def test_find_images_in_dir_empty(self, manager):
        """空目录应返回空列表"""
        assert manager._find_images_in_dir("drink_water") == []

    def test_find_images_in_dir_picks_up_images(self, manager, temp_cache):
        """子目录中放入图片后能正确发现"""
        subdir = os.path.join(temp_cache, "kegel")
        for name in ["a.png", "b.jpg", "c.gif", "d.txt", "e.bmp"]:
            with open(os.path.join(subdir, name), "wb") as f:
                f.write(b"dummy")
        found = manager._find_images_in_dir("kegel")
        basenames = {os.path.basename(p) for p in found}
        assert "a.png" in basenames
        assert "b.jpg" in basenames
        assert "c.gif" in basenames
        assert "e.bmp" in basenames
        assert "d.txt" not in basenames  # 不是图片格式

    def test_find_images_in_dir_unknown_type(self, manager):
        """未知类型不应崩溃"""
        result = manager._find_images_in_dir("nonexistent")
        assert result == []

    def test_get_random_meme_generates_when_empty(self, manager):
        """子目录无图片时应自动生成"""
        try:
            result = manager.get_random_meme("drink_water")
            if result is not None:
                assert os.path.exists(result)
                assert "drink_water" in result
        except ImportError:
            pytest.skip("Pillow not installed")

    def test_get_random_meme_picks_existing(self, manager, temp_cache):
        """子目录有图片时应从中随机选取"""
        subdir = os.path.join(temp_cache, "fish_touch")
        test_file = os.path.join(subdir, "user_meme.png")
        with open(test_file, "wb") as f:
            f.write(b"fake image")
        result = manager.get_random_meme("fish_touch")
        assert result == test_file

    def test_preload_memes(self, manager, temp_cache):
        """预加载后每个类型目录应有图片"""
        try:
            manager.preload_memes(count=2)
            for rtype in ALL_REMINDER_TYPES:
                imgs = manager._find_images_in_dir(rtype)
                assert len(imgs) >= 2, f"{rtype} should have >=2 images after preload"
        except ImportError:
            pytest.skip("Pillow not installed")

    def test_preload_skips_existing(self, manager, temp_cache):
        """预加载时已有足够图片的类型不再生成"""
        try:
            subdir = os.path.join(temp_cache, "stretch")
            for i in range(5):
                manager.generate_meme_image("stretch")
            before = len(manager._find_images_in_dir("stretch"))
            manager.preload_memes(count=3)
            after = len(manager._find_images_in_dir("stretch"))
            assert after == before  # 已经够了，不再生成新的
        except ImportError:
            pytest.skip("Pillow not installed")

    def test_get_cached_or_download_with_type(self, manager, temp_cache):
        """下载缓存应保存到类型子目录"""
        import hashlib
        url = "https://example.com/test.png"
        url_hash = hashlib.md5(url.encode()).hexdigest()
        # 手动在子目录创建缓存文件
        subdir = os.path.join(temp_cache, "drink_water")
        cache_path = os.path.join(subdir, f"{url_hash}.png")
        with open(cache_path, 'wb') as f:
            f.write(b"fake png")
        result = manager.get_cached_or_download(url, "drink_water")
        assert result == cache_path

    def test_type_dir(self, manager, temp_cache):
        """_type_dir 返回正确路径"""
        expected = os.path.join(temp_cache, "rest_eyes")
        assert manager._type_dir("rest_eyes") == expected
