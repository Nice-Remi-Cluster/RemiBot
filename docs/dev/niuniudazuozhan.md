# 牛牛大作战插件开发方案

## 1. 项目概述

### 1.1 功能描述
牛牛大作战是一个基于NoneBot2的群聊娱乐插件，提供牛牛长度管理和互动功能。

### 1.2 核心特性
- 支持中英文命令（英文前缀：`/nndzz`）
- 仅限群聊使用
- 每个用户在不同群的数据独立
- 牛牛长度范围：通常30cm以内，特殊情况可超过
- 支持负数长度（称为"深度"）
- 冷却时间机制（10分钟）
- 防刷机制（每日被指定次数限制）

## 2. 技术架构

### 2.1 技术栈
- **框架**: NoneBot2
- **命令解析**: nonebot-plugin-alconna
- **数据库**: nonebot-plugin-orm (SQLAlchemy + Alembic)
- **数据库后端**: MySQL
- **本地存储**: 项目根目录/data

### 2.2 项目结构
```
src/plugins/niuniudazuozhan/
├── __init__.py              # 插件入口
├── commands/                # 命令处理模块
│   ├── __init__.py
│   ├── basic.py            # 基础命令（导、查看等）
│   └── interactive.py      # 互动命令（日群友等）
├── models/                  # 数据模型
│   ├── __init__.py
│   └── user_data.py        # 用户数据模型
├── services/               # 业务逻辑
│   ├── __init__.py
│   ├── game_logic.py       # 游戏逻辑
│   ├── cooldown.py         # 冷却时间管理
│   └── statistics.py      # 统计功能
└── utils/                  # 工具函数
    ├── __init__.py
    ├── random_gen.py       # 随机数生成
    └── validators.py       # 数据验证
```

## 3. 数据库设计

### 3.1 ORM 模型定义

使用 `nonebot-plugin-orm` 和 SQLAlchemy 定义数据模型：

#### 用户牛牛数据模型 (UserNiuniuData)
```python
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from enum import Enum

from nonebot_plugin_orm import Model
from sqlalchemy import String, DECIMAL, DateTime, Date, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class UserNiuniuData(Model):
    """用户牛牛数据模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    length: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal('0.00'), comment="牛牛长度(cm)"
    )
    total_operations: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总操作次数"
    )
    last_operation_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后操作时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index('uk_user_group', 'user_id', 'group_id', unique=True),
        Index('idx_group_id', 'group_id'),
        Index('idx_last_operation', 'last_operation_time'),
    )
```

#### 牛牛操作记录模型 (NiuniuOperation)
```python
class OperationType(str, Enum):
    """操作类型枚举"""
    DAO = "dao"
    RI_QUNYU = "ri_qunyu"


class NiuniuOperation(Model):
    """牛牛操作记录模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    target_user_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="目标用户ID（日群友时使用）"
    )
    operation_type: Mapped[OperationType] = mapped_column(
        nullable=False, comment="操作类型"
    )
    length_change: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="长度变化"
    )
    target_length_change: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, comment="目标用户长度变化"
    )
    operation_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    
    __table_args__ = (
        Index('idx_user_group_time', 'user_id', 'group_id', 'operation_time'),
        Index('idx_target_user_time', 'target_user_id', 'operation_time'),
    )
```

#### 冷却时间模型 (NiuniuCooldown)
```python
class NiuniuCooldown(Model):
    """冷却时间模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    last_dao_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后导操作时间"
    )
    last_ri_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后日群友时间"
    )
    daily_targeted_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="今日被指定次数"
    )
    last_reset_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="最后重置日期"
    )
    
    __table_args__ = (
        Index('uk_user_group', 'user_id', 'group_id', unique=True),
    )
```

## 4. 命令设计

### 4.1 基础命令

#### 4.1.1 导命令
```python
# 使用 shortcut 为英文命令添加中文快捷方式
dao_alc = Alconna("/nndzz", Subcommand("dao"))
# 添加中文快捷方式
dao_alc.shortcut("导", {"command": "/nndzz dao"})

dao_cmd = on_alconna(
    dao_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)
```

#### 4.1.2 查看命令
```python
# 使用 shortcut 为英文命令添加中文快捷方式
view_alc = Alconna("/nndzz", Subcommand("view", Args["target?", At]))
# 添加中文快捷方式
view_alc.shortcut("查看牛牛", {"command": "/nndzz view"})
view_alc.shortcut("查看", {"command": "/nndzz view"})
view_alc.shortcut("牛牛长度", {"command": "/nndzz view"})
# 支持带参数的中文快捷方式
view_alc.shortcut("查看牛牛 (.+)", {"command": "/nndzz view {0}"})

view_cmd = on_alconna(
    view_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)
```

### 4.2 互动命令

#### 4.2.1 日群友命令
```python
# 使用 shortcut 为英文命令添加中文快捷方式
ri_qunyu_alc = Alconna("/nndzz", Subcommand("attack", Args["target?", At]))
# 添加中文快捷方式
ri_qunyu_alc.shortcut("日群友", {"command": "/nndzz attack"})
ri_qunyu_alc.shortcut("日", {"command": "/nndzz attack"})
# 支持带参数的中文快捷方式
ri_qunyu_alc.shortcut("日群友 (.+)", {"command": "/nndzz attack {0}"})
ri_qunyu_alc.shortcut("日 (.+)", {"command": "/nndzz attack {0}"})

ri_qunyu_cmd = on_alconna(
    ri_qunyu_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)
```

### 4.3 命令处理器

#### 4.3.1 导命令处理器
```python
@dao_cmd.assign("dao")
async def handle_dao(matcher: AlconnaMatcher, event: GroupMessageEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    
    # 检查冷却时间
    can_use, remaining = await CooldownManager.check_cooldown(user_id, group_id, "dao")
    if not can_use:
        await matcher.finish(f"冷却中，还需等待 {remaining} 分钟")
    
    # 执行导操作
    length_change = GameLogic.calculate_dao_change()
    user_data = await DatabaseService.create_or_update_user_data(user_id, group_id, Decimal(str(length_change)))
    
    # 记录操作
    await DatabaseService.record_operation(
        user_id, group_id, OperationType.DAO, Decimal(str(length_change))
    )
    
    # 更新冷却时间
    await CooldownManager.update_cooldown(user_id, group_id, "dao")
    
    # 发送结果
    result_msg = f"导操作完成！\n长度变化：{length_change:+.2f}cm\n当前长度：{GameLogic.format_length(float(user_data.length))}"
    await matcher.finish(result_msg)
```

#### 4.3.2 查看命令处理器
```python
@view_cmd.assign("view")
async def handle_view(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    group_id = str(event.group_id)
    
    if target.available:
        # 查看指定用户
        target_user_id = str(target.result.target)
        user_data = await DatabaseService.get_user_data(target_user_id, group_id)
        if user_data is None:
            await matcher.finish("该用户还没有牛牛数据")
        
        length_str = GameLogic.format_length(float(user_data.length))
        await matcher.finish(f"用户 {target.result} 的牛牛长度：{length_str}")
    else:
        # 查看自己
        user_id = str(event.user_id)
        user_data = await DatabaseService.get_user_data(user_id, group_id)
        if user_data is None:
            await matcher.finish("你还没有牛牛数据，使用 '导' 命令开始游戏吧！")
        
        length_str = GameLogic.format_length(float(user_data.length))
        await matcher.finish(f"你的牛牛长度：{length_str}\n总操作次数：{user_data.total_operations}")
```

#### 4.3.3 日群友命令处理器
```python
@ri_qunyu_cmd.assign("attack")
async def handle_ri_qunyu(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    if not target.available:
        await matcher.finish("请指定要日的群友！")
    
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    target_user_id = str(target.result.target)
    
    # 不能日自己
    if user_id == target_user_id:
        await matcher.finish("不能日自己！")
    
    # 检查冷却时间
    can_use, remaining = await CooldownManager.check_cooldown(user_id, group_id, "ri")
    if not can_use:
        await matcher.finish(f"冷却中，还需等待 {remaining} 分钟")
    
    # 检查目标每日被指定次数
    if not await CooldownManager.check_daily_limit(target_user_id, group_id):
        await matcher.finish("该用户今日已被指定次数过多，请明天再试")
    
    # 执行日群友操作
    attacker_gain, target_loss = GameLogic.calculate_ri_changes()
    
    # 更新攻击者数据
    attacker_data = await DatabaseService.create_or_update_user_data(
        user_id, group_id, Decimal(str(attacker_gain))
    )
    
    # 更新目标数据
    target_data = await DatabaseService.create_or_update_user_data(
        target_user_id, group_id, Decimal(str(target_loss))
    )
    
    # 记录操作
    await DatabaseService.record_operation(
        user_id, group_id, OperationType.RI_QUNYU, 
        Decimal(str(attacker_gain)), target_user_id, Decimal(str(target_loss))
    )
    
    # 更新冷却时间
    await CooldownManager.update_cooldown(user_id, group_id, "ri")
    await CooldownManager.update_daily_target_count(target_user_id, group_id)
    
    # 发送结果
    result_msg = (
        f"日群友成功！\n"
        f"你的长度变化：{attacker_gain:+.2f}cm\n"
        f"你的当前长度：{GameLogic.format_length(float(attacker_data.length))}\n"
        f"{target.result} 的长度变化：{target_loss:+.2f}cm\n"
        f"{target.result} 的当前长度：{GameLogic.format_length(float(target_data.length))}"
    )
    await matcher.finish(result_msg)
```

## 5. @ 消息处理

### 5.1 @ 消息段的基本概念

在 NoneBot2 中，@ 功能通过 `nonebot-plugin-alconna` 的 `UniMessage` 和 `At` 消息段来实现。`At` 消息段包含以下属性：
- `type`: 类型，可以是 "user"、"role" 或 "channel"
- `target`: 目标用户/角色/频道的 ID

### 5.2 在命令中处理 @ 消息

#### 5.2.1 提取 @ 消息段

使用 `UniMsg` 依赖注入器获取消息，然后检查和提取 `At` 消息段：

```python
from nonebot_plugin_alconna.uniseg import UniMsg, At

@matcher.handle()
async def _(msg: UniMsg):
    # 检查消息中是否包含 @ 消息段
    if msg.has(At):
        # 获取所有 @ 消息段
        ats = msg.get(At)
        for at in ats:
            print(f"@用户类型: {at.type}, 目标ID: {at.target}")
```

#### 5.2.2 在 Alconna 命令中使用 At 参数

在命令定义中，可以直接使用 `At` 类型作为参数：

```python
from arclet.alconna import Alconna, Args
from nonebot_plugin_alconna.uniseg import At

# 定义接受 @ 参数的命令
view_alc = Alconna("/nndzz", Subcommand("view", Args["target?", At]))
ri_qunyu_alc = Alconna("/nndzz", Subcommand("attack", Args["target?", At]))
```

#### 5.2.3 在命令处理器中获取 @ 目标

```python
from nonebot_plugin_alconna import Match

@view_cmd.assign("view")
async def handle_view(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    if target.available:
        # 获取被 @ 的用户 ID
        target_user_id = str(target.result.target)
        # 处理逻辑...
    else:
        # 没有 @ 任何人，处理自己的数据
        user_id = str(event.user_id)
        # 处理逻辑...
```

### 5.3 发送包含 @ 的消息

#### 5.3.1 创建 @ 消息

```python
from nonebot_plugin_alconna.uniseg import UniMessage, At

# 方法1：直接创建包含 @ 的消息
message = UniMessage([
    At("user", "123456789"),  # @特定用户
    "你好！"
])

# 方法2：使用模板
message = UniMessage.template("{:At(user, target)}你好！").format(target="123456789")

# 发送消息
await message.send()
```

#### 5.3.2 在命令处理器中回复并 @ 用户

```python
@ri_qunyu_cmd.assign("attack")
async def handle_ri_qunyu(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    if not target.available:
        await matcher.finish("请指定要日的群友！")
    
    # 获取目标用户信息
    target_user_id = str(target.result.target)
    
    # 执行游戏逻辑...
    
    # 发送结果时 @ 相关用户
    result_msg = UniMessage([
        "日群友成功！\n",
        "你的长度变化：+1.23cm\n",
        target.result,  # 直接使用 At 消息段
        " 的长度变化：-0.87cm"
    ])
    await matcher.finish(result_msg)
```

### 5.4 提取纯文本（忽略@）

如果需要获取消息的纯文本内容（忽略 @ 等特殊消息段）：

```python
@matcher.handle()
async def _(msg: UniMsg):
    # 提取纯文本，忽略 @ 和其他特殊消息段
    plain_text = msg.extract_plain_text()
    print(plain_text)  # 只包含文本内容，不包含@信息
```

### 5.5 在牛牛大作战中的应用示例

#### 5.5.1 查看命令的完整实现

```python
@view_cmd.assign("view")
async def handle_view(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    group_id = str(event.group_id)
    
    if target.available:
        # 查看指定用户（通过@）
        target_user_id = str(target.result.target)
        user_data = await DatabaseService.get_user_data(target_user_id, group_id)
        if user_data is None:
            # 回复时 @ 目标用户
            reply_msg = UniMessage([
                target.result,
                " 还没有牛牛数据"
            ])
            await matcher.finish(reply_msg)
        
        length_str = GameLogic.format_length(float(user_data.length))
        reply_msg = UniMessage([
            target.result,
            f" 的牛牛长度：{length_str}"
        ])
        await matcher.finish(reply_msg)
    else:
        # 查看自己
        user_id = str(event.user_id)
        user_data = await DatabaseService.get_user_data(user_id, group_id)
        if user_data is None:
            await matcher.finish("你还没有牛牛数据，使用 '导' 命令开始游戏吧！")
        
        length_str = GameLogic.format_length(float(user_data.length))
        await matcher.finish(f"你的牛牛长度：{length_str}\n总操作次数：{user_data.total_operations}")
```

#### 5.5.2 日群友命令的 @ 处理

```python
@ri_qunyu_cmd.assign("attack")
async def handle_ri_qunyu(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    if not target.available:
        await matcher.finish("请指定要日的群友！使用方法：日群友 @某人")
    
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    target_user_id = str(target.result.target)
    
    # 不能日自己
    if user_id == target_user_id:
        await matcher.finish("不能日自己！")
    
    # 游戏逻辑处理...
    
    # 发送结果时 @ 目标用户
    result_msg = UniMessage([
        "日群友成功！\n",
        f"你的长度变化：{attacker_gain:+.2f}cm\n",
        f"你的当前长度：{GameLogic.format_length(float(attacker_data.length))}\n",
        target.result,
        f" 的长度变化：{target_loss:+.2f}cm\n",
        target.result,
        f" 的当前长度：{GameLogic.format_length(float(target_data.length))}"
    ])
    await matcher.finish(result_msg)
```

### 5.6 注意事项

1. **类型检查**：在处理 `Match[At]` 时，务必先检查 `target.available` 确保参数存在
2. **用户验证**：获取到 `target.result.target` 后，建议验证用户是否在群内
3. **错误处理**：当用户没有按正确格式 @ 时，提供清晰的使用说明
4. **消息构建**：发送包含 @ 的消息时，可以直接使用 `target.result` 或创建新的 `At` 消息段
5. **权限控制**：在某些场景下可能需要检查用户是否有权限 @ 特定角色或频道

## 6. 业务逻辑实现

### 6.1 游戏逻辑 (game_logic.py)
```python
class GameLogic:
    @staticmethod
    def calculate_dao_change() -> float:
        """计算导操作的长度变化"""
        # 50%概率增长，50%概率缩短
        # 变化范围：-5.0 到 +5.0 cm
        direction = random.choice([-1, 1])
        change = random.uniform(0.1, 5.0) * direction
        return round(change, 2)
    
    @staticmethod
    def calculate_ri_changes() -> tuple[float, float]:
        """计算日群友操作的长度变化"""
        # 攻击者增加：0.1-1.0cm
        # 被攻击者减少：0.1-1.0cm
        attacker_gain = random.uniform(0.1, 1.0)
        target_loss = -random.uniform(0.1, 1.0)
        return round(attacker_gain, 2), round(target_loss, 2)
    
    @staticmethod
    def format_length(length: float) -> str:
        """格式化长度显示"""
        if length >= 0:
            return f"{length:.2f}cm"
        else:
            return f"{abs(length):.2f}cm深度"
```

### 6.2 冷却时间管理 (cooldown.py)
```python
from datetime import datetime, date, timedelta
from typing import Optional, Tuple

from nonebot_plugin_orm import get_session
from sqlalchemy import select, update

from ..models import NiuniuCooldown, OperationType


class CooldownManager:
    COOLDOWN_MINUTES = 10
    MAX_DAILY_TARGETED = 3
    
    @classmethod
    async def check_cooldown(cls, user_id: str, group_id: str, operation_type: OperationType) -> Tuple[bool, int]:
        """检查冷却时间
        
        Returns:
            tuple: (是否可以操作, 剩余冷却时间分钟数)
        """
        async with get_session() as session:
            result = await session.execute(
                select(NiuniuCooldown).where(
                    NiuniuCooldown.user_id == user_id,
                    NiuniuCooldown.group_id == group_id
                )
            )
            cooldown_data = result.scalar_one_or_none()
            
            if cooldown_data is None:
                return True, 0
            
            now = datetime.now()
            last_operation_time = None
            
            if operation_type == OperationType.DAO:
                last_operation_time = cooldown_data.last_dao_time
            elif operation_type == OperationType.RI_QUNYU:
                last_operation_time = cooldown_data.last_ri_time
            
            if last_operation_time is None:
                return True, 0
            
            time_diff = now - last_operation_time
            cooldown_seconds = cls.COOLDOWN_MINUTES * 60
            
            if time_diff.total_seconds() >= cooldown_seconds:
                return True, 0
            else:
                remaining_seconds = cooldown_seconds - time_diff.total_seconds()
                remaining_minutes = int(remaining_seconds / 60) + 1
                return False, remaining_minutes
    
    @classmethod
    async def update_cooldown(cls, user_id: str, group_id: str, operation_type: OperationType):
        """更新冷却时间"""
        async with get_session() as session:
            result = await session.execute(
                select(NiuniuCooldown).where(
                    NiuniuCooldown.user_id == user_id,
                    NiuniuCooldown.group_id == group_id
                )
            )
            cooldown_data = result.scalar_one_or_none()
            
            now = datetime.now()
            
            if cooldown_data is None:
                # 创建新的冷却记录
                cooldown_data = NiuniuCooldown(
                    user_id=user_id,
                    group_id=group_id
                )
                if operation_type == OperationType.DAO:
                    cooldown_data.last_dao_time = now
                elif operation_type == OperationType.RI_QUNYU:
                    cooldown_data.last_ri_time = now
                
                session.add(cooldown_data)
            else:
                # 更新现有记录
                if operation_type == OperationType.DAO:
                    cooldown_data.last_dao_time = now
                elif operation_type == OperationType.RI_QUNYU:
                    cooldown_data.last_ri_time = now
            
            await session.commit()
    
    @classmethod
    async def check_daily_limit(cls, target_user_id: str, group_id: str) -> bool:
        """检查每日被指定次数限制
        
        Returns:
            bool: True表示未达到限制，False表示已达到限制
        """
        async with get_session() as session:
            result = await session.execute(
                select(NiuniuCooldown).where(
                    NiuniuCooldown.user_id == target_user_id,
                    NiuniuCooldown.group_id == group_id
                )
            )
            cooldown_data = result.scalar_one_or_none()
            
            if cooldown_data is None:
                return True
            
            today = date.today()
            
            # 检查是否需要重置每日计数
            if cooldown_data.last_reset_date != today:
                cooldown_data.daily_targeted_count = 0
                cooldown_data.last_reset_date = today
                await session.commit()
                return True
            
            return cooldown_data.daily_targeted_count < cls.MAX_DAILY_TARGETED
    
    @classmethod
    async def increment_daily_targeted(cls, target_user_id: str, group_id: str):
        """增加每日被指定次数"""
        async with get_session() as session:
            result = await session.execute(
                select(NiuniuCooldown).where(
                    NiuniuCooldown.user_id == target_user_id,
                    NiuniuCooldown.group_id == group_id
                )
            )
            cooldown_data = result.scalar_one_or_none()
            
            today = date.today()
            
            if cooldown_data is None:
                # 创建新记录
                cooldown_data = NiuniuCooldown(
                    user_id=target_user_id,
                    group_id=group_id,
                    daily_targeted_count=1,
                    last_reset_date=today
                )
                session.add(cooldown_data)
            else:
                # 检查是否需要重置
                if cooldown_data.last_reset_date != today:
                    cooldown_data.daily_targeted_count = 1
                    cooldown_data.last_reset_date = today
                else:
                    cooldown_data.daily_targeted_count += 1
            
            await session.commit()
```

## 7. 数据库集成

### 7.1 模型定义

在 `src/plugins/niuniudazuozhan/models/` 目录下创建数据模型：

```python
# models/__init__.py
from .user_data import UserNiuniuData
from .operations import NiuniuOperation, OperationType
from .cooldowns import NiuniuCooldown

__all__ = ["UserNiuniuData", "NiuniuOperation", "OperationType", "NiuniuCooldown"]
```

```python
# models/user_data.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from nonebot_plugin_orm import Model
from sqlalchemy import String, DECIMAL, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class UserNiuniuData(Model):
    """用户牛牛数据模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    length: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal('0.00'), comment="牛牛长度(cm)"
    )
    total_operations: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总操作次数"
    )
    last_operation_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后操作时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index('uk_user_group', 'user_id', 'group_id', unique=True),
        Index('idx_group_id', 'group_id'),
        Index('idx_last_operation', 'last_operation_time'),
    )
```

```python
# models/operations.py
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from nonebot_plugin_orm import Model
from sqlalchemy import String, DECIMAL, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class OperationType(str, Enum):
    """操作类型枚举"""
    DAO = "dao"
    RI_QUNYU = "ri_qunyu"


class NiuniuOperation(Model):
    """牛牛操作记录模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    target_user_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="目标用户ID（日群友时使用）"
    )
    operation_type: Mapped[OperationType] = mapped_column(
        nullable=False, comment="操作类型"
    )
    length_change: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="长度变化"
    )
    target_length_change: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, comment="目标用户长度变化"
    )
    operation_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    
    __table_args__ = (
        Index('idx_user_group_time', 'user_id', 'group_id', 'operation_time'),
        Index('idx_target_user_time', 'target_user_id', 'operation_time'),
    )
```

```python
# models/cooldowns.py
from datetime import datetime, date
from typing import Optional

from nonebot_plugin_orm import Model
from sqlalchemy import String, Integer, DateTime, Date, Index
from sqlalchemy.orm import Mapped, mapped_column


class NiuniuCooldown(Model):
    """冷却时间模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    last_dao_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后导操作时间"
    )
    last_ri_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后日群友时间"
    )
    daily_targeted_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="今日被指定次数"
    )
    last_reset_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="最后重置日期"
    )
    
    __table_args__ = (
        Index('uk_user_group', 'user_id', 'group_id', unique=True),
    )
```

### 7.2 数据库服务层

```python
# services/database.py
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from nonebot_plugin_orm import get_session
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserNiuniuData, NiuniuOperation, NiuniuCooldown, OperationType


class DatabaseService:
    """数据库服务类"""
    
    @staticmethod
    async def get_user_data(user_id: str, group_id: str) -> Optional[UserNiuniuData]:
        """获取用户数据"""
        async with get_session() as session:
            result = await session.execute(
                select(UserNiuniuData).where(
                    UserNiuniuData.user_id == user_id,
                    UserNiuniuData.group_id == group_id
                )
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_or_update_user_data(
        user_id: str, 
        group_id: str, 
        length_change: Decimal
    ) -> UserNiuniuData:
        """创建或更新用户数据"""
        async with get_session() as session:
            user_data = await DatabaseService.get_user_data(user_id, group_id)
            
            if user_data is None:
                user_data = UserNiuniuData(
                    user_id=user_id,
                    group_id=group_id,
                    length=length_change,
                    total_operations=1,
                    last_operation_time=datetime.now()
                )
                session.add(user_data)
            else:
                user_data.length += length_change
                user_data.total_operations += 1
                user_data.last_operation_time = datetime.now()
            
            await session.commit()
            await session.refresh(user_data)
            return user_data
    
    @staticmethod
    async def record_operation(
        user_id: str,
        group_id: str,
        operation_type: OperationType,
        length_change: Decimal,
        target_user_id: Optional[str] = None,
        target_length_change: Optional[Decimal] = None
    ) -> NiuniuOperation:
        """记录操作"""
        async with get_session() as session:
            operation = NiuniuOperation(
                user_id=user_id,
                group_id=group_id,
                target_user_id=target_user_id,
                operation_type=operation_type,
                length_change=length_change,
                target_length_change=target_length_change
            )
            session.add(operation)
            await session.commit()
            await session.refresh(operation)
            return operation
```

### 7.3 数据库迁移

使用 NoneBot2 的 ORM 迁移功能：

```bash
# 生成迁移文件
uv run nb orm heads

# 执行迁移
uv run nb orm upgrade

# 检查迁移状态
uv run nb orm check

# 回滚迁移（如需要）
uv run nb orm downgrade
```

## 8. 错误处理和用户体验

### 8.1 错误消息
- 冷却时间未到："牛牛还在休息中，请{remaining_minutes}分钟后再试"
- 每日限制："今天已经被日够了，明天再来吧"
- 群聊限制："牛牛大作战只能在群聊中使用哦"

### 8.2 成功消息模板
- 导操作："你的牛牛{增长/缩短}了{change}cm，当前长度：{current_length}"
- 日群友："你成功日了@{target}，你的牛牛增长{gain}cm，对方缩短{loss}cm"

## 9. 部署和配置

### 9.1 依赖安装
```bash
uv add nonebot-plugin-orm
uv add nonebot-plugin-alconna
```

### 9.2 配置文件
```python
# .env.prod
DATABASE_URL=mysql+asyncmy://username:password@localhost:3306/nonebot
ALEMBIC_STARTUP_CHECK=true
```

## 10. 测试计划

### 10.1 单元测试
- 游戏逻辑测试
- 冷却时间管理测试
- 数据库操作测试

### 10.2 集成测试
- 命令响应测试
- 多用户并发测试
- 跨群数据隔离测试

## 11. 扩展功能（后期）

### 11.1 排行榜系统
- 群内排行榜
- 全服排行榜
- 历史记录查询

### 11.2 成就系统
- 长度里程碑
- 操作次数成就
- 特殊事件成就

### 11.3 道具系统
- 保护道具
- 增强道具
- 特殊效果道具

---

**开发优先级**：
1. 核心数据模型和数据库设计
2. 基础命令实现（导、查看）
3. 冷却时间和限制机制
4. 互动命令实现（日群友）
5. 错误处理和用户体验优化
6. 测试和部署
7. 扩展功能开发
