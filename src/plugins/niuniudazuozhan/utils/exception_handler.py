"""异常处理工具模块

提供统一的异常处理机制，特别是针对 NoneBot2 的 FinishedException 处理。
"""

import logging
from functools import wraps
from typing import Any, Callable, TypeVar, Union

from nonebot.exception import MatcherException, FinishedException
from nonebot_plugin_alconna import AlconnaMatcher

# 设置日志记录器
logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class NiuniuExceptionHandler:
    """牛牛大作战异常处理器"""
    
    @staticmethod
    def handle_matcher_exception(func: F) -> F:
        """装饰器：处理 Matcher 相关异常
        
        正确处理 matcher.finish() 抛出的 FinishedException，
        避免在 try-except 块中意外捕获导致程序流程异常。
        
        Args:
            func: 要装饰的异步函数
            
        Returns:
            装饰后的函数
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MatcherException:
                # 重新抛出 MatcherException（包括 FinishedException）
                # 这是 NoneBot2 的正常流程控制异常，不应该被捕获
                raise
            except Exception as e:
                # 记录其他异常
                logger.error(f"在函数 {func.__name__} 中发生异常: {e}", exc_info=True)
                # 根据函数参数判断是否有 matcher 可用
                matcher = None
                for arg in args:
                    if isinstance(arg, AlconnaMatcher):
                        matcher = arg
                        break
                
                if matcher:
                    await matcher.finish("操作失败，请稍后重试")
                else:
                    # 如果没有 matcher，重新抛出异常
                    raise
        
        return wrapper
    
    @staticmethod
    async def safe_finish(matcher: AlconnaMatcher, message: Union[str, Any], 
                         fallback_message: str = "操作失败，请稍后重试") -> None:
        """安全地调用 matcher.finish()
        
        在异常情况下提供备用消息。
        
        Args:
            matcher: AlconnaMatcher 实例
            message: 要发送的消息
            fallback_message: 发送失败时的备用消息
        """
        try:
            await matcher.finish(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}", exc_info=True)
            try:
                await matcher.finish(fallback_message)
            except Exception as fallback_e:
                logger.error(f"发送备用消息也失败: {fallback_e}", exc_info=True)
                # 最后的保险措施：重新抛出原始异常
                raise e
    
    @staticmethod
    def log_and_finish(error_message: str = "操作失败，请稍后重试"):
        """装饰器：记录异常并发送错误消息
        
        Args:
            error_message: 发送给用户的错误消息
            
        Returns:
            装饰器函数
        """
        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except MatcherException:
                    # 重新抛出 MatcherException
                    raise
                except Exception as e:
                    # 记录异常详情
                    logger.error(
                        f"函数 {func.__name__} 执行失败: {e}", 
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'args': str(args)[:200],  # 限制日志长度
                            'kwargs': str(kwargs)[:200]
                        }
                    )
                    
                    # 查找 matcher 参数
                    matcher = None
                    for arg in args:
                        if isinstance(arg, AlconnaMatcher):
                            matcher = arg
                            break
                    
                    if matcher:
                        await NiuniuExceptionHandler.safe_finish(matcher, error_message)
                    else:
                        raise
            
            return wrapper
        return decorator


# 便捷的装饰器别名
handle_exceptions = NiuniuExceptionHandler.handle_matcher_exception
log_and_finish = NiuniuExceptionHandler.log_and_finish
safe_finish = NiuniuExceptionHandler.safe_finish


# 常用的错误消息常量
class ErrorMessages:
    """错误消息常量"""
    
    OPERATION_FAILED = "操作失败，请稍后重试"
    INVALID_USER = "用户信息无效"
    INVALID_GROUP = "群组信息无效"
    INVALID_TARGET = "目标用户信息无效"
    COOLDOWN_ACTIVE = "操作冷却中，请稍后再试"
    DAILY_LIMIT_REACHED = "今日操作次数已达上限"
    PERMISSION_DENIED = "权限不足，无法执行此操作"
    DATABASE_ERROR = "数据库操作失败，请稍后重试"
    VALIDATION_ERROR = "输入数据验证失败"
    NETWORK_ERROR = "网络连接异常，请稍后重试"