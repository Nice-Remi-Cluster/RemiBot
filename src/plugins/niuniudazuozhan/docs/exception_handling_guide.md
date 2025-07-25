# 牛牛大作战异常处理指南

## 概述

本指南介绍了牛牛大作战插件中新的异常处理机制，旨在规范化处理 NoneBot2 中的 `FinishedException` 及其他异常。

## 核心组件

### NiuniuExceptionHandler 类

位于 `utils/exception_handler.py`，提供了统一的异常处理工具。

### 主要功能

1. **handle_exceptions 装饰器**：自动处理 `MatcherException` 和其他异常
2. **safe_finish 方法**：安全地调用 `matcher.finish()`
3. **log_and_finish 装饰器**：记录异常并发送错误消息
4. **ErrorMessages 类**：定义常用的错误消息常量

## 使用方法

### 1. 基本装饰器使用

```python
from ..utils import handle_exceptions, ErrorMessages

@command.assign("example")
@handle_exceptions
async def handle_example(matcher: AlconnaMatcher, event: GroupMessageEvent):
    """示例命令处理函数"""
    # 验证输入
    if not valid_input:
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    # 业务逻辑
    result = await some_operation()
    
    # 返回结果
    await matcher.finish(f"操作成功：{result}")
```

### 2. 错误消息常量

```python
class ErrorMessages:
    INVALID_USER = "用户或群组信息无效"
    VALIDATION_ERROR = "操作异常，请稍后重试"
    DATABASE_ERROR = "数据库操作失败，请稍后重试"
    PERMISSION_DENIED = "权限不足，无法执行此操作"
    COOLDOWN_ACTIVE = "操作冷却中，请稍后再试"
    OPERATION_FAILED = "操作失败，请稍后重试"
```

### 3. 安全的 matcher.finish() 调用

```python
from ..utils import safe_finish

# 在需要手动处理异常的地方
try:
    result = await risky_operation()
    await safe_finish(matcher, f"操作成功：{result}")
except SpecificException as e:
    await safe_finish(matcher, ErrorMessages.OPERATION_FAILED)
```

## 异常处理流程

### 1. FinishedException 处理

`handle_exceptions` 装饰器会自动捕获并重新抛出 `FinishedException`，确保正常的消息发送流程不被中断。

### 2. 其他异常处理

对于其他异常，装饰器会：
- 记录详细的错误日志
- 向用户发送友好的错误消息
- 防止异常向上传播

### 3. 日志记录

所有异常都会被记录到日志中，包含：
- 异常类型和消息
- 发生异常的函数名
- 用户和群组信息
- 完整的堆栈跟踪

## 最佳实践

### 1. 统一使用装饰器

所有命令处理函数都应该使用 `@handle_exceptions` 装饰器：

```python
@command.assign("cmd")
@handle_exceptions
async def handle_cmd(matcher: AlconnaMatcher, event: GroupMessageEvent):
    # 函数实现
    pass
```

### 2. 使用预定义错误消息

优先使用 `ErrorMessages` 类中的常量，保持错误消息的一致性：

```python
# 好的做法
await matcher.finish(ErrorMessages.INVALID_USER)

# 避免的做法
await matcher.finish("用户信息无效")
```

### 3. 移除手动异常处理

使用装饰器后，可以移除大部分手动的 try-except 块：

```python
# 旧的做法
try:
    result = await operation()
    await matcher.finish(f"结果：{result}")
except Exception as e:
    await matcher.finish("操作失败")

# 新的做法
@handle_exceptions
async def handle_operation(matcher, event):
    result = await operation()
    await matcher.finish(f"结果：{result}")
```

### 4. 验证逻辑前置

将输入验证放在函数开头，使用 `matcher.finish()` 直接返回错误：

```python
@handle_exceptions
async def handle_command(matcher, event):
    # 验证输入
    if not valid_input:
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    # 业务逻辑
    # ...
```

## 迁移指南

### 从旧代码迁移

1. **添加装饰器**：在所有命令处理函数上添加 `@handle_exceptions`
2. **移除 try-except**：删除手动的异常处理代码
3. **统一错误消息**：使用 `ErrorMessages` 常量替换硬编码的错误消息
4. **简化逻辑**：移除不必要的异常处理逻辑

### 示例迁移

**迁移前：**
```python
async def handle_dao(matcher, event):
    try:
        # 验证
        if not valid:
            await matcher.finish("用户信息无效")
        
        # 业务逻辑
        result = await operation()
        await matcher.finish(f"结果：{result}")
    except Exception as e:
        await matcher.finish("操作失败")
```

**迁移后：**
```python
@handle_exceptions
async def handle_dao(matcher, event):
    # 验证
    if not valid:
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    # 业务逻辑
    result = await operation()
    await matcher.finish(f"结果：{result}")
```

## 注意事项

1. **FinishedException 是正常现象**：`matcher.finish()` 抛出 `FinishedException` 是 NoneBot2 的正常行为
2. **不要捕获 FinishedException**：让装饰器处理这个异常
3. **保持日志清洁**：避免记录正常的 `FinishedException`
4. **测试异常处理**：确保异常处理逻辑正确工作

## 总结

新的异常处理机制提供了：
- 统一的异常处理方式
- 更清洁的代码结构
- 更好的错误日志记录
- 更友好的用户体验

通过使用这套机制，可以显著提高代码的可维护性和用户体验。