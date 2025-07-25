"""异常处理机制测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from nonebot.exception import FinishedException

from ..utils.exception_handler import (
    NiuniuExceptionHandler,
    handle_exceptions,
    safe_finish,
    ErrorMessages
)


class TestNiuniuExceptionHandler:
    """测试 NiuniuExceptionHandler 类"""
    
    def test_error_messages(self):
        """测试错误消息常量"""
        assert ErrorMessages.INVALID_USER == "用户或群组信息无效"
        assert ErrorMessages.VALIDATION_ERROR == "操作异常，请稍后重试"
        assert ErrorMessages.DATABASE_ERROR == "数据库操作失败，请稍后重试"
        assert ErrorMessages.PERMISSION_DENIED == "权限不足，无法执行此操作"
        assert ErrorMessages.COOLDOWN_ACTIVE == "操作冷却中，请稍后再试"
        assert ErrorMessages.OPERATION_FAILED == "操作失败，请稍后重试"
    
    @pytest.mark.asyncio
    async def test_safe_finish_success(self):
        """测试 safe_finish 正常情况"""
        matcher = AsyncMock()
        message = "测试消息"
        
        # 模拟 matcher.finish 抛出 FinishedException
        matcher.finish.side_effect = FinishedException
        
        # safe_finish 应该重新抛出 FinishedException
        with pytest.raises(FinishedException):
            await safe_finish(matcher, message)
        
        # 验证 matcher.finish 被调用
        matcher.finish.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_safe_finish_with_exception(self):
        """测试 safe_finish 处理其他异常"""
        matcher = AsyncMock()
        message = "测试消息"
        
        # 模拟 matcher.finish 抛出其他异常
        matcher.finish.side_effect = RuntimeError("测试异常")
        
        # safe_finish 应该捕获异常并记录日志
        await safe_finish(matcher, message)
        
        # 验证 matcher.finish 被调用
        matcher.finish.assert_called_once_with(message)


class TestHandleExceptionsDecorator:
    """测试 handle_exceptions 装饰器"""
    
    @pytest.mark.asyncio
    async def test_normal_execution(self):
        """测试正常执行流程"""
        matcher = AsyncMock()
        
        @handle_exceptions
        async def test_func(matcher_param):
            await matcher_param.finish("正常消息")
        
        # 模拟 matcher.finish 抛出 FinishedException
        matcher.finish.side_effect = FinishedException
        
        # 应该重新抛出 FinishedException
        with pytest.raises(FinishedException):
            await test_func(matcher)
        
        matcher.finish.assert_called_once_with("正常消息")
    
    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """测试异常处理"""
        matcher = AsyncMock()
        
        @handle_exceptions
        async def test_func(matcher_param):
            raise RuntimeError("测试异常")
        
        # 应该捕获异常并发送错误消息
        await test_func(matcher)
        
        # 验证发送了错误消息
        matcher.finish.assert_called_once_with(ErrorMessages.OPERATION_FAILED)
    
    @pytest.mark.asyncio
    async def test_finish_exception_passthrough(self):
        """测试 FinishedException 直接传递"""
        matcher = AsyncMock()
        
        @handle_exceptions
        async def test_func(matcher_param):
            raise FinishedException
        
        # FinishedException 应该直接传递
        with pytest.raises(FinishedException):
            await test_func(matcher)
        
        # 不应该调用 matcher.finish
        matcher.finish.assert_not_called()


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_command_handler_simulation(self):
        """模拟命令处理函数的异常处理"""
        matcher = AsyncMock()
        event = MagicMock()
        event.user_id = 12345
        event.group_id = 67890
        
        @handle_exceptions
        async def mock_command_handler(matcher_param, event_param):
            # 模拟验证失败
            if event_param.user_id == 12345:
                await matcher_param.finish(ErrorMessages.INVALID_USER)
            
            # 模拟正常操作
            await matcher_param.finish("操作成功")
        
        # 模拟 matcher.finish 抛出 FinishedException
        matcher.finish.side_effect = FinishedException
        
        # 应该重新抛出 FinishedException
        with pytest.raises(FinishedException):
            await mock_command_handler(matcher, event)
        
        # 验证调用了正确的错误消息
        matcher.finish.assert_called_once_with(ErrorMessages.INVALID_USER)
    
    @pytest.mark.asyncio
    async def test_database_error_simulation(self):
        """模拟数据库错误的处理"""
        matcher = AsyncMock()
        
        @handle_exceptions
        async def mock_database_operation(matcher_param):
            # 模拟数据库操作失败
            raise ConnectionError("数据库连接失败")
        
        # 应该捕获异常并发送错误消息
        await mock_database_operation(matcher)
        
        # 验证发送了通用错误消息
        matcher.finish.assert_called_once_with(ErrorMessages.OPERATION_FAILED)


if __name__ == "__main__":
    # 运行测试的示例
    import asyncio
    
    async def run_basic_test():
        """运行基本测试"""
        print("开始测试异常处理机制...")
        
        # 测试错误消息
        print(f"错误消息测试: {ErrorMessages.INVALID_USER}")
        
        # 测试 safe_finish
        matcher = AsyncMock()
        matcher.finish.side_effect = FinishedException
        
        try:
            await safe_finish(matcher, "测试消息")
        except FinishedException:
            print("safe_finish 测试通过: 正确重新抛出 FinishedException")
        
        print("异常处理机制测试完成")
    
    # 如果直接运行此文件，执行基本测试
    asyncio.run(run_basic_test())