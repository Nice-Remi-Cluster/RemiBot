"""用户消息配置

统一管理maicn插件中返回给用户的所有消息，使其更加用户友好和简洁。
"""

from typing import Dict, Any


class Messages:
    """消息配置类"""

    # 成功消息
    SUCCESS_MAIMAI_ADDED = "✅ maimai账号添加成功"
    SUCCESS_LXNS_ADDED = "✅ 落雪查分器添加成功"
    SUCCESS_DIVINGFISH_ADDED = "✅ 水鱼查分器添加成功"
    SUCCESS_SHUIYU_ADDED = "✅ 水鱼查分器添加成功"
    SUCCESS_BIND_UPDATED = "✅ 绑定更新成功"
    SUCCESS_PROFILE_SWITCHED = "✅ 档案切换成功"
    SUCCESS_LXNS_PROFILE_CREATED = "✅ 落雪档案创建成功"
    SUCCESS_SCORES_UPDATED = "✅ 成绩数据更新完成"

    # 错误消息
    ERROR_QR_EXPIRED = "❌ 二维码已过期，请重新获取"
    ERROR_QR_INVALID = "❌ 二维码无效，请检查后重试"
    ERROR_ADD_FAILED = "❌ 添加失败，请稍后重试"
    ERROR_BIND_FAILED = "❌ 绑定失败，请稍后重试"
    ERROR_UPDATE_FAILED = "❌ 更新失败，请稍后重试"
    ERROR_SWITCH_FAILED = "❌ 切换失败，请检查档案名称"
    ERROR_CREATE_FAILED = "❌ 创建失败，请稍后重试"
    ERROR_SERVICE_UNAVAILABLE = "❌ 服务暂时不可用，请稍后重试"
    ERROR_ACCOUNT_EXCEPTION = "❌ 账号服务异常，请稍后重试"
    ERROR_BIND_SOURCE_NOT_FOUND = "❌ 未找到绑定源"
    ERROR_UNSUPPORTED_SOURCE = "❌ 不支持的数据源"
    ERROR_DIVINGFISH_FORMAT_ERROR = "❌ 水鱼绑定数据格式错误，请重新绑定"
    ERROR_DIVINGFISH_INCOMPLETE = "❌ 水鱼绑定数据不完整，请重新绑定"
    ERROR_SHUIYU_BIND_FORMAT = "❌ 水鱼绑定数据格式错误或不完整，请重新绑定"
    ERROR_GET_MAIMAI_INFO = "❌ 无法获取您的maimai档案信息，请稍后重试"
    ERROR_CREATE_LXNS_FAILED = "❌ 创建落雪档案失败，请稍后重试"
    ERROR_LXNS_UPDATE_FAILED = "❌ 落雪数据更新失败，请稍后重试"
    ERROR_SHUIYU_UPDATE_FAILED = "❌ 水鱼数据更新失败，请稍后重试"
    ERROR_LXNS_USER_NOT_FOUND = "❌ 您绑定的好友码在落雪查分器中没有找到对应档案"
    ERROR_NO_UPDATE_SOURCE = "❌ 没有可更新的数据源，请检查您的绑定信息"
    ERROR_SCORE_DATA_FETCH_FAILED = "❌ 无法获取您的成绩数据，请检查绑定信息或稍后重试"
    ERROR_B50_GENERATE_FAILED = "❌ 生成B50图片失败，请稍后重试"
    ERROR_LXNS_NOT_FOUND = "❌ 落雪查分器中未找到对应档案"
    ERROR_SCORES_UPDATE_FAILED = "❌ 成绩更新失败，请稍后重试"
    ERROR_B50_GENERATION_FAILED = "❌ B50图片生成失败，请稍后重试"
    ERROR_NO_SCORES_DATA = "❌ 无法获取成绩数据，请检查绑定信息"

    # 提示消息
    HINT_NO_MAIMAI_BIND = "💡 您还没有绑定maimai账号，请先使用绑定命令"
    HINT_NO_QUERY_BIND = "💡 您还没有绑定查分器，请先绑定查分器"
    HINT_NO_LXNS_BIND = "💡 当前档案未绑定落雪查分器，请先绑定"
    HINT_NO_DIVINGFISH_BIND = "💡 您还没有绑定水鱼查分器，请先绑定"
    HINT_NO_SHUIYU_BIND = "💡 您还没有绑定水鱼查分器，请先使用绑定命令"
    HINT_NO_UPDATE_SOURCE = "💡 没有可更新的数据源，请检查绑定信息"
    HINT_LXNS_PROFILE_EXISTS = "💡 该好友码已存在落雪档案，无需重复创建"
    HINT_NO_BIND = "💡 您还没有绑定任何查分器，请先绑定查分器"

    @staticmethod
    def format_current_profile(username: str, rating: int, others_info: str) -> str:
        """格式化当前档案信息"""
        # 解析绑定信息并格式化
        formatted_binds = Messages._format_bind_info(others_info)
        return (
            f"📋 当前maimai档案\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🎮 用户名: {username}\n"
            f"⭐ Rating: {rating}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔗 绑定信息:\n{formatted_binds}"
        )

    @staticmethod
    def format_bind_update_success(username: str, rating: int, others_info: str) -> str:
        """格式化绑定更新成功信息"""
        formatted_binds = Messages._format_bind_info(others_info)
        return (
            f"✅ 绑定更新成功\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🎮 用户名: {username}\n"
            f"⭐ Rating: {rating}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔗 绑定信息:\n{formatted_binds}"
        )

    @staticmethod
    def format_profile_switch_success(
        username: str, rating: int, others_info: str
    ) -> str:
        """格式化档案切换成功信息"""
        formatted_binds = Messages._format_bind_info(others_info)
        return (
            f"✅ 档案切换成功\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🎮 用户名: {username}\n"
            f"⭐ Rating: {rating}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔗 绑定信息:\n{formatted_binds}"
        )

    @staticmethod
    def format_lxns_profile_exists(profile_name: str) -> str:
        """格式化落雪档案已存在信息"""
        return f"💡 该好友码已存在落雪档案：{profile_name}，无需重复创建"

    @staticmethod
    def format_lxns_create_success(bind_name: str, friend_code: str) -> str:
        """格式化落雪档案创建成功信息"""
        return f"✅ 创建落雪档案成功\n档案名称：{bind_name}\n好友码：{friend_code}"

    @staticmethod
    def format_lxns_create_success_with_info(player_info: str) -> str:
        """格式化落雪档案创建成功信息（带详细信息）"""
        return f"✅ 创建落雪档案成功\n{player_info}"

    @staticmethod
    def format_score_update_success(name: str) -> str:
        """格式化成绩更新成功信息"""
        return f"✅ 已成功更新{name}的数据"

    @staticmethod
    def _format_bind_info(others_info: str) -> str:
        """格式化绑定信息，隐藏敏感信息"""
        import json
        import ast

        try:
            # 尝试解析字符串为列表
            if isinstance(others_info, str):
                # 如果是字符串表示的列表，使用ast.literal_eval安全解析
                bind_list = ast.literal_eval(others_info)
            else:
                bind_list = others_info

            if not isinstance(bind_list, list):
                return "🔗 绑定信息格式错误"

            formatted_lines = []
            for i, bind in enumerate(bind_list, 1):
                bind_type = bind.get("bind_type", "未知")
                bind_name = bind.get("bind_name", "默认")
                is_default = bind.get("is_default", False)

                # 根据绑定类型显示不同信息
                if bind_type == "luoxue":
                    type_icon = "❄️"
                    type_name = "落雪查分器"
                    # 隐藏好友码的部分数字
                    friend_code = bind.get("bind_content", "")
                    if len(friend_code) > 6:
                        masked_code = friend_code[:3] + "***" + friend_code[-3:]
                    else:
                        masked_code = "***"
                    detail = f"好友码: {masked_code}"
                elif bind_type == "divingfish":
                    type_icon = "🐟"
                    type_name = "水鱼查分器"
                    # 解析用户名，隐藏密码
                    try:
                        bind_content = json.loads(bind.get("bind_content", "{}"))
                        username = bind_content.get("username", "未知")
                        detail = f"用户名: {username}"
                    except:
                        detail = "绑定信息解析失败"
                else:
                    type_icon = "🔗"
                    type_name = bind_type
                    detail = "已绑定"

                default_mark = " (当前)" if is_default else ""
                formatted_lines.append(
                    f"  {type_icon} {type_name} - {bind_name}{default_mark}\n"
                    f"     {detail}"
                )

            return "\n".join(formatted_lines) if formatted_lines else "暂无绑定信息"

        except Exception as e:
            return f"🔗 绑定信息解析失败: {str(e)}"
