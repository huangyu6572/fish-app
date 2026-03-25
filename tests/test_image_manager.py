"""
测试 - FunnyImageManager 搞怪图片管理
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from core.image_manager import FunnyImageManager


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
