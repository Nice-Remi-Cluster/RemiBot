from io import BytesIO
from pathlib import Path
from typing import Any

from nonebot import logger
from maimai_py import SongType
from PIL import Image, ImageDraw, ImageFont


class B50ImageGenerator:
    # 静态资源路径
    STATIC_PATH = Path("resources/yuzu/static")
    MAI_PIC_PATH = STATIC_PATH / "mai" / "pic"
    MAI_COVER_PATH = STATIC_PATH / "mai" / "cover"
    FONT_HR_PATH = STATIC_PATH / "ResourceHanRoundedCN-Bold.ttf"
    FONT_TORUS_PATH = STATIC_PATH / "Torus SemiBold.otf"

    # 难度配置
    DIFFICULTY_COLORS = [
        "#22BB5B",  # Basic - 绿色
        "#FB9C2D",  # Advanced - 橙色
        "#F64861",  # Expert - 红色
        "#9A5ACD",  # Master - 紫色
        "#BA55D3",  # Re:Master - 紫红色
    ]

    DIFFICULTY_NAMES = ["Basic", "Advanced", "Expert", "Master", "Re:Master"]

    # 布局配置
    CARD_SIZE = (270, 114)
    COVER_SIZE = (75, 75)
    CANVAS_SIZE = (1400, 1600)

    def __init__(self):
        self.background_image: Image.Image | None = None
        self.fonts = {}
        self.difficulty_backgrounds = []
        self._initialize_resources()

    def _initialize_resources(self):
        """初始化所有静态资源"""
        try:
            self._load_background_image()
            self._load_fonts()
            self._load_difficulty_backgrounds()
        except Exception as e:
            logger.error(f"初始化资源失败: {e}")
            self._create_fallback_resources()

    def _load_background_image(self):
        """加载背景图片"""
        bg_path = self.MAI_PIC_PATH / "b50_bg.png"
        if bg_path.exists():
            self.background_image = Image.open(bg_path).convert("RGBA")
        else:
            self.background_image = Image.new(
                "RGBA", self.CANVAS_SIZE, (255, 255, 255, 255)
            )

    def _load_fonts(self):
        """加载字体文件"""
        # 加载基础字体文件
        self.font_files = {}

        if self.FONT_HR_PATH.exists():
            self.font_files["hr"] = str(self.FONT_HR_PATH)
        else:
            self.font_files["hr"] = None

        if self.FONT_TORUS_PATH.exists():
            self.font_files["torus"] = str(self.FONT_TORUS_PATH)
        else:
            self.font_files["torus"] = None

        # 创建常用字体实例
        self.fonts = {
            "hr_large": self._create_font("hr", 28),
            "hr_medium": self._create_font("hr", 14),
            "hr_small": self._create_font("hr", 13),
            "torus_large": self._create_font("torus", 30),
            "torus_medium": self._create_font("torus", 14),
            "torus_small": self._create_font("torus", 13),
        }

    def _create_font(self, font_type: str, size: int) -> ImageFont.ImageFont:
        """创建指定类型和大小的字体"""
        font_path = self.font_files.get(font_type)
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"加载字体失败 {font_path}: {e}")
        return ImageFont.load_default()

    def get_font(self, font_type: str, size: int) -> ImageFont.ImageFont:
        """获取指定类型和大小的字体（动态创建）"""
        return self._create_font(font_type, size)

    def _load_difficulty_backgrounds(self):
        """加载难度背景图片"""
        difficulty_files = [
            "b50_score_basic.png",
            "b50_score_advanced.png",
            "b50_score_expert.png",
            "b50_score_master.png",
            "b50_score_remaster.png",
        ]

        for i, filename in enumerate(difficulty_files):
            bg_path = self.MAI_PIC_PATH / filename
            if bg_path.exists():
                self.difficulty_backgrounds.append(Image.open(bg_path).convert("RGBA"))
            else:
                # 创建默认背景
                color = (
                    self.DIFFICULTY_COLORS[i]
                    if i < len(self.DIFFICULTY_COLORS)
                    else self.DIFFICULTY_COLORS[3]
                )
                default_bg = Image.new("RGBA", self.CARD_SIZE, color)
                self.difficulty_backgrounds.append(default_bg)

    def _create_fallback_resources(self):
        """创建备用资源"""
        self.background_image = Image.new(
            "RGBA", self.CANVAS_SIZE, (255, 255, 255, 255)
        )

        # 创建默认字体文件映射
        self.font_files = {"hr": None, "torus": None}

        # 创建默认字体实例
        default_font = ImageFont.load_default()
        self.fonts = {
            "hr_large": default_font,
            "hr_medium": default_font,
            "hr_small": default_font,
            "torus_large": default_font,
            "torus_medium": default_font,
            "torus_small": default_font,
        }

        # 创建默认难度背景
        self.difficulty_backgrounds = []
        for color in self.DIFFICULTY_COLORS:
            default_bg = Image.new("RGBA", self.CARD_SIZE, color)
            self.difficulty_backgrounds.append(default_bg)

    def _get_difficulty_background(self, level_index: int) -> Image.Image:
        """获取难度背景图片"""
        if 0 <= level_index < len(self.difficulty_backgrounds):
            return self.difficulty_backgrounds[level_index]
        # 返回Master难度背景作为默认值
        return (
            self.difficulty_backgrounds[3]
            if len(self.difficulty_backgrounds) > 3
            else Image.new("RGBA", self.CARD_SIZE, self.DIFFICULTY_COLORS[3])
        )

    def _truncate_text(
        self, text: str, max_width: int, font: ImageFont.ImageFont = None
    ) -> str:
        """按像素宽度截断文本"""
        if not font:
            font = self.fonts.get("hr_medium", ImageFont.load_default())

        # 创建临时图像用于测量文本宽度
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)

        # 如果文本宽度小于等于最大宽度，直接返回
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return text

        # 计算省略号的宽度
        ellipsis_bbox = temp_draw.textbbox((0, 0), "...", font=font)
        ellipsis_width = ellipsis_bbox[2] - ellipsis_bbox[0]

        # 可用于文本的宽度
        available_width = max_width - ellipsis_width

        # 二分查找最佳截断位置
        left, right = 0, len(text)
        best_length = 0

        while left <= right:
            mid = (left + right) // 2
            test_text = text[:mid]

            test_bbox = temp_draw.textbbox((0, 0), test_text, font=font)
            test_width = test_bbox[2] - test_bbox[0]

            if test_width <= available_width:
                best_length = mid
                left = mid + 1
            else:
                right = mid - 1

        return f"{text[:best_length]}..." if best_length > 0 else "..."

    def _get_song_cover(self, song_id: int) -> Image.Image | None:
        """获取歌曲封面图片"""
        try:
            # 处理ID：对10000取余，确保与maimai.py的ID一致
            normalized_id = song_id % 10000 if song_id >= 10000 else song_id

            # 尝试加载封面图片
            for cover_id in [song_id, normalized_id]:
                cover_path = self.MAI_COVER_PATH / f"{cover_id}.png"
                if cover_path.exists():
                    cover = Image.open(cover_path).convert("RGBA")
                    return cover.resize(self.COVER_SIZE, Image.Resampling.LANCZOS)

            logger.warning(f"未找到歌曲ID {song_id} (标准化ID: {normalized_id}) 的封面")
            return None

        except Exception as e:
            logger.error(f"加载歌曲封面失败 (ID: {song_id}): {e}")
            return None

    def _convert_score_to_dict(self, score) -> dict[str, Any]:
        """将maimai_py的Score对象转换为字典格式"""
        # 将 LevelIndex 枚举转换为整数
        level_index = score.level_index
        if hasattr(level_index, "value"):
            level_index = level_index.value
        elif not isinstance(level_index, int):
            level_index = int(level_index)

        # 获取歌曲ID
        song_id = getattr(score, "id", None) or getattr(score, "song_id", None)

        # 获取铺面类型
        song_type = getattr(score, "type", None)

        return {
            "song_id": song_id,
            "title": score.title,
            "level_index": level_index,
            "level": score.level_value,
            "achievement": score.achievements,
            "rating": score.dx_rating,
            "combo_status": getattr(score, "fc", None),
            "sync_status": getattr(score, "fs", None),
            "song_type": song_type,
        }

    def _get_text_colors(self, level_index: int) -> tuple:
        """获取文本和ID颜色"""
        text_colors = [
            (255, 255, 255, 255),  # Basic - 白色
            (255, 255, 255, 255),  # Advanced - 白色
            (255, 255, 255, 255),  # Expert - 白色
            (255, 255, 255, 255),  # Master - 白色
            (138, 0, 226, 255),  # Re:Master - 紫色
        ]

        id_colors = [
            (129, 217, 85, 255),  # Basic - 绿色
            (245, 189, 21, 255),  # Advanced - 橙色
            (255, 129, 141, 255),  # Expert - 红色
            (159, 81, 220, 255),  # Master - 紫色
            (138, 0, 226, 255),  # Re:Master - 深紫色
        ]

        index = level_index if level_index < len(text_colors) else 3
        return text_colors[index], id_colors[index]

    def _draw_song_cover_or_placeholder(
        self,
        img: Image.Image,
        draw: ImageDraw.Draw,
        song_id: str | None,
        x: int,
        y: int,
        text_color: tuple,
        id_color: tuple,
    ):
        """绘制歌曲封面或占位符"""
        if not song_id:
            return

        try:
            song_id_int = int(song_id)
            cover = self._get_song_cover(song_id_int)

            cover_x, cover_y = x + 12, y + 12

            if cover:
                img.alpha_composite(cover, (cover_x, cover_y))
            else:
                # 绘制占位符
                placeholder_color = id_color[:3] + (128,)  # 半透明
                draw.rectangle(
                    [
                        (cover_x, cover_y),
                        (
                            cover_x + self.COVER_SIZE[0] - 12,
                            cover_y + self.COVER_SIZE[1] - 12,
                        ),
                    ],
                    fill=placeholder_color,
                    outline=id_color,
                    width=2,
                )
        except (ValueError, TypeError):
            logger.warning(f"无效的歌曲ID: {song_id}")

    def _get_rank_image_path(self, achievement: float) -> Path | None:
        """根据达成率获取评级图片路径"""
        try:
            if achievement >= 100.5:
                rank_name = "SSSp"
            elif achievement >= 100.0:
                rank_name = "SSS"
            elif achievement >= 99.5:
                rank_name = "SSp"
            elif achievement >= 99.0:
                rank_name = "SS"
            elif achievement >= 98.0:
                rank_name = "Sp"
            elif achievement >= 97.0:
                rank_name = "S"
            elif achievement >= 94.0:
                rank_name = "AAA"
            elif achievement >= 90.0:
                rank_name = "AA"
            elif achievement >= 80.0:
                rank_name = "A"
            elif achievement >= 75.0:
                rank_name = "BBB"
            elif achievement >= 70.0:
                rank_name = "BB"
            elif achievement >= 60.0:
                rank_name = "B"
            elif achievement >= 50.0:
                rank_name = "C"
            else:
                rank_name = "D"

            rank_path = self.MAI_PIC_PATH / f"UI_TTR_Rank_{rank_name}.png"
            return rank_path if rank_path.exists() else None
        except Exception as e:
            logger.error(f"获取评级图片路径失败: {e}")
            return None

    def _get_combo_status_image_path(
        self, combo_status: str | None
    ) -> Path | None:
        """根据单人评价状态获取图片路径"""
        if not combo_status:
            return None

        try:
            # 单人评价映射
            combo_mapping = {"fc": "FC", "fcp": "FCp", "ap": "AP", "app": "APp"}

            # 处理枚举类型或字符串类型
            if hasattr(combo_status, "name"):
                status_str = combo_status.name.lower()  # 枚举类型
            else:
                status_str = str(combo_status).lower()  # 字符串类型

            bonus_name = combo_mapping.get(status_str)
            if bonus_name:
                bonus_path = self.MAI_PIC_PATH / f"UI_CHR_PlayBonus_{bonus_name}.png"
                return bonus_path if bonus_path.exists() else None
            return None
        except Exception as e:
            logger.error(f"获取单人评价图片路径失败: {e}")
            return None

    def _get_sync_status_image_path(self, sync_status: str | None) -> Path | None:
        """根据多人评价状态获取图片路径"""
        if not sync_status:
            return None

        try:
            # 多人评价映射
            sync_mapping = {
                "sync": "Sync",
                "fs": "FS",
                "fsp": "FSp",
                "fsd": "FSD",
                "fsdp": "FSDp",
            }

            # 处理枚举类型或字符串类型
            if hasattr(sync_status, "name"):
                status_str = sync_status.name.lower()  # 枚举类型
            else:
                status_str = str(sync_status).lower()  # 字符串类型

            bonus_name = sync_mapping.get(status_str)
            if bonus_name:
                bonus_path = self.MAI_PIC_PATH / f"UI_CHR_PlayBonus_{bonus_name}.png"
                return bonus_path if bonus_path.exists() else None
            return None
        except Exception as e:
            logger.error(f"获取多人评价图片路径失败: {e}")
            return None

    def _draw_score_card(
        self, img: Image.Image, score_data: dict[str, Any], x: int, y: int
    ):
        """绘制单个成绩卡片"""
        try:
            level_index = score_data.get("level_index", 3)
            song_id = score_data.get("song_id")

            # 获取难度背景并粘贴
            card_background = self._get_difficulty_background(level_index)
            img.alpha_composite(card_background, (x, y))

            draw = ImageDraw.Draw(img)
            text_color, id_color = self._get_text_colors(level_index)

            # 绘制歌曲封面或占位符
            self._draw_song_cover_or_placeholder(
                img, draw, song_id, x, y, text_color, id_color
            )

            # 文本绘制起始位置
            text_x = x + 96  # 封面右侧

            # 绘制歌曲标题
            title = self._truncate_text(
                score_data.get("title", "Unknown"), 150, self.fonts["hr_medium"]
            )
            draw.text(
                (text_x, y + 14),
                title,
                fill=text_color,
                font=self.fonts["hr_medium"],
                anchor="lm",
            )

            # 绘制成绩
            achievement = score_data.get("achievement", 0)
            achievement_text = f"{achievement:.4f}%"
            draw.text(
                (text_x, y + 38),
                achievement_text,
                fill=text_color,
                font=self.fonts["torus_large"],
                anchor="lm",
            )

            # 绘制难度和Rating
            level_value = score_data.get("level", "0")
            rating = score_data.get("rating", 0)
            ds_ra_text = f"{level_value} -> {rating}"
            draw.text(
                (text_x, y + 66),
                ds_ra_text,
                fill=text_color,
                font=self.fonts["torus_medium"],
                anchor="lm",
            )

            # 绘制评级图片
            rank_path = self._get_rank_image_path(achievement)
            if rank_path and rank_path.exists():
                try:
                    rank_img = Image.open(rank_path)
                    # 调整评级图片大小（可根据需要调整）
                    rank_img = rank_img.resize((63, 28), Image.Resampling.LANCZOS)
                    img.alpha_composite(rank_img, (x + 90, y + 80))
                except Exception as e:
                    logger.warning(f"绘制评级图片失败: {e}")

            # 绘制单人评价图标
            combo_status = score_data.get("combo_status")
            combo_path = self._get_combo_status_image_path(combo_status)
            if combo_path and combo_path.exists():
                try:
                    combo_img = Image.open(combo_path)
                    # 调整单人评价图片大小
                    combo_img = combo_img.resize((34, 34), Image.Resampling.LANCZOS)
                    img.alpha_composite(combo_img, (x + 152, y + 76))
                except Exception as e:
                    logger.warning(f"绘制单人评价图片失败: {e}")

            # 绘制多人评价图标
            sync_status = score_data.get("sync_status")
            sync_path = self._get_sync_status_image_path(sync_status)
            if sync_path and sync_path.exists():
                try:
                    sync_img = Image.open(sync_path)
                    # 调整多人评价图片大小
                    sync_img = sync_img.resize((34, 34), Image.Resampling.LANCZOS)
                    img.alpha_composite(sync_img, (x + 184, y + 76))
                except Exception as e:
                    logger.warning(f"绘制多人评价图片失败: {e}")

            # 绘制歌曲类型图标（SD/DX）
            song_type = score_data.get("song_type")
            if song_type:
                try:
                    # 根据歌曲类型选择对应的图片
                    if hasattr(song_type, "name"):
                        type_name = song_type.name  # 如果是枚举类型
                    else:
                        type_name = str(song_type)  # 如果是字符串类型

                    # 映射枚举名称到图片文件名
                    type_mapping = {
                        "STANDARD": "SD",
                        "DX": "DX",
                        "UTAGE": "UTAGE",  # 如果有宴会场模式的图片
                    }

                    image_name = type_mapping.get(type_name)
                    if image_name:
                        type_path = self.MAI_PIC_PATH / f"{image_name}.png"
                        if type_path.exists():
                            type_img = Image.open(type_path)
                            # 调整歌曲类型图片大小为 37x14
                            type_img = type_img.resize(
                                (37, 14), Image.Resampling.LANCZOS
                            )
                            img.alpha_composite(type_img, (x + 50, y + 90))
                except Exception as e:
                    logger.warning(f"绘制歌曲类型图片失败: {e}")

            # 绘制歌曲ID
            if song_id:
                # 判断是否为DX铺面，如果是则ID+10000
                display_id = song_id
                song_type = score_data.get("song_type")
                if song_type == SongType.DX:
                    display_id = song_id + 10000

                draw.text(
                    (x + 10, y + 96),
                    str(display_id),
                    fill=id_color,
                    font=self.fonts["torus_small"],
                    anchor="lm",
                )

        except Exception as e:
            logger.error(f"绘制成绩卡片失败: {e}")

    def _draw_header(
        self,
        img: Image.Image,
        player_data: dict[str, Any],
        b35_scores: list[dict[str, Any]],
        b15_scores: list[dict[str, Any]],
    ):
        """绘制头部信息"""
        draw = ImageDraw.Draw(img)

        # 绘制logo
        logo_path = self.MAI_PIC_PATH / "logo.png"
        if logo_path.exists():
            logo = Image.open(logo_path).resize((249, 120))
            img.alpha_composite(logo, (14, 60))

        # 绘制玩家名称
        player_name = player_data.get("name", "Unknown Player")
        draw.text(
            (445, 135),
            player_name,
            fill=(0, 0, 0, 255),
            font=self.fonts["hr_large"],
            anchor="lm",
        )

        # 绘制Rating信息
        b35_rating = sum(score.get("rating", 0) for score in b35_scores)
        b15_rating = sum(score.get("rating", 0) for score in b15_scores)
        player_rating = player_data.get("rating", 0)
        rating_text = f"B35: {b35_rating} + B15: {b15_rating} = {player_rating}"
        draw.text(
            (570, 172),
            rating_text,
            fill=(0, 0, 0, 255),
            font=self.fonts["hr_medium"],
            anchor="mm",
        )

    def _draw_footer(self, img: Image.Image):
        """绘制底部信息"""
        draw = ImageDraw.Draw(img)
        footer_text = "Designed by Yuri-YuzuChaN & BlueDeer233. Generated by RemiBot"
        draw.text(
            (700, 1570),
            footer_text,
            fill=(124, 129, 255, 255),
            font=self.fonts["hr_small"],
            anchor="mm",
        )

    def generate_b50_image(
        self,
        player_data: dict[str, Any],
        b35_scores: list[dict[str, Any]],
        b15_scores: list[dict[str, Any]],
    ) -> bytes:
        """生成B50图片"""
        try:
            img = self.background_image.copy()

            # 绘制各个部分
            self._draw_header(img, player_data, b35_scores, b15_scores)
            self._draw_scores(img, b35_scores, is_b35=True)
            self._draw_scores(img, b15_scores, is_b35=False)
            self._draw_footer(img)

            # 转换为字节
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format="PNG")
            return img_byte_arr.getvalue()

        except Exception as e:
            logger.error(f"生成B50图片失败: {e}")
            return self._create_error_image(str(e))

    def _create_error_image(self, error_message: str) -> bytes:
        """创建错误图片"""
        error_img = Image.new("RGB", (800, 600), (255, 255, 255))
        error_draw = ImageDraw.Draw(error_img)
        error_draw.text(
            (50, 50),
            f"生成图片失败: {error_message}",
            fill="black",
            font=self.fonts["hr_medium"],
        )

        img_byte_arr = BytesIO()
        error_img.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def _draw_scores(
        self, img: Image.Image, scores: list[dict[str, Any]], is_b35: bool
    ):
        """绘制成绩列表"""
        start_y = 235 if is_b35 else 1085
        row_height = 114

        for index, score in enumerate(scores):
            row = index // 5
            col = index % 5

            x = 16 + col * 276
            y = start_y + row * row_height

            self._draw_score_card(img, score, x, y)
