# RemiBot 用户指南

## 简介

RemiBot 是一个基于 NoneBot2 框架开发的舞萌DX查分机器人，提供账号绑定、成绩查询、权限管理等功能。

## 核心概念

### 1. 命令系统

RemiBot 使用 Alconna 作为命令解析器，支持两种命令前缀：
- **英文前缀**: `/` (可配置)
- **中文前缀**: `。` (可配置)

### 2. 插件架构

RemiBot 采用模块化插件架构，主要包含以下插件：
- **maicn**: 舞萌DX核心功能插件
- **permission_manager**: 权限管理插件
- **core**: 核心功能插件（帮助系统等）
- **ping**: 连通性测试插件
- **roll**: 随机数生成插件

### 3. 账号系统

RemiBot 集成了 Remi-Service 账号中心，支持：
- 统一的用户身份管理
- 多平台账号绑定
- 档案切换功能

### 4. 查分器集成

支持多个查分器平台：
- **落雪查分器** (lxns)
- **水鱼查分器** (divingfish)
- **官方API** (通过 Wahlap-Mai-Ass-Expander)

## 基础功能

### 连通性测试

**命令**: `/ping` 或 `。在吗`

**功能**: 测试机器人是否在线

**示例**:
```
用户: /ping
机器人: 我在
```

### 随机数生成

**命令**: `/roll [参数]` 或 `。随机数` / `。随机`

**功能**: 生成随机数或从选项中随机选择

**用法**:
- `/roll` - 生成0-100的随机数
- `/roll 50` - 生成0-50的随机数
- `/roll 选项1 选项2 选项3` - 从选项中随机选择

**示例**:
```
用户: /roll
机器人: 42

用户: /roll 苹果 香蕉 橙子
机器人: 苹果
```

### 帮助系统

**命令**: `/help` 或 `。帮助` / `。帮助文档` / `。怎么用`

**功能**: 显示帮助信息

## 舞萌DX功能

### 账号管理

#### 添加舞萌账号

**命令**: `/maicn add <sgwcmaid> [绑定名称]`

**功能**: 绑定舞萌DX官方账号

**参数**:
- `sgwcmaid`: 舞萌账号的SGWC MAID
- `绑定名称`: 可选，为账号设置别名

**示例**:
```
/maicn add 12345678 我的主号
```

#### 绑定查分器账号

**命令**: `/maicn bind <查分器> <绑定名称>`

**功能**: 为已有的舞萌账号绑定查分器账号

**参数**:
- `查分器`: 支持 `lxns`(落雪) 或 `divingfish`(水鱼)
- `绑定名称`: 要绑定的账号名称

**示例**:
```
/maicn bind lxns 我的主号
/maicn bind divingfish 我的主号
```

#### 查看当前档案

**命令**: `/maicn current [档案名]`

**功能**: 查看或切换当前使用的档案

**示例**:
```
/maicn current
/maicn current 我的主号
```

### 查分器管理

#### 落雪查分器

**添加账号**: `/lxns add <好友码> [绑定名称]`

**创建档案**: `/lxns create`

**示例**:
```
/lxns add 123456789 我的落雪账号
/lxns create
```

#### 水鱼查分器

**添加账号**: `/divingfish add <用户名> <密码> [绑定名称]`

**示例**:
```
/divingfish add myusername mypassword 我的水鱼账号
```

### 成绩查询

#### B50查询

**命令**: `/maicn b50 <查分器>`

**功能**: 生成B50成绩图片

**参数**:
- `查分器`: `lxns` 或 `divingfish`

**示例**:
```
/maicn b50 lxns
/maicn b50 divingfish
```

#### 更新查分器

**命令**: `/maicn update [查分器]`

**功能**: 同步成绩到查分器平台

**示例**:
```
/maicn update
/maicn update lxns
```

## 权限管理

### 权限系统概述

RemiBot 使用基于 Casbin 的 RBAC (基于角色的访问控制) 权限系统，支持：
- **多范围权限**: 全局(global)、群组(group)、私聊(private)
- **角色管理**: admin、guest 等角色
- **细粒度控制**: 针对不同功能的权限控制

### 权限范围

- **global**: 全局权限，适用于所有场景
- **group**: 群组权限，仅在特定群组生效
- **private**: 私聊权限，仅在私聊场景生效

### 默认角色

- **admin**: 管理员，拥有所有权限
- **guest**: 访客，拥有所有功能权限

### 权限管理命令

> 注意：以下命令通常需要管理员权限

#### 添加角色

**命令**: `/permission add_role <用户ID> <角色> [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 为用户添加角色

**示例**:
```
# 添加全局管理员
/permission add_role 123456789 admin --scope global

# 添加群组管理员
/permission add_role 123456789 admin --scope group --scope-id 987654321
```

#### 移除角色

**命令**: `/permission remove_role <用户ID> <角色> [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 移除用户角色

**示例**:
```
/permission remove_role 123456789 admin --scope group --scope-id 987654321
```

#### 列出用户角色

**命令**: `/permission list_roles <用户ID> [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 查看用户拥有的角色

**示例**:
```
/permission list_roles 123456789
/permission list_roles 123456789 --scope group --scope-id 987654321
```

#### 列出角色用户

**命令**: `/permission list_users <角色> [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 查看拥有指定角色的用户

**示例**:
```
/permission list_users admin
/permission list_users admin --scope group --scope-id 987654321
```

#### 重载权限策略

**命令**: `/permission reload`

**功能**: 重新加载权限配置文件

#### 检查权限

**命令**: `/permission check`

**功能**: 检查自己的权限信息

#### 权限系统信息

**命令**: `/permission info`

**功能**: 显示权限系统的基本信息

#### 添加黑名单

**命令**: `/permission add_blacklist <用户ID> <功能名> [操作] [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 禁止特定用户使用某个功能

**参数**:
- `用户ID`: 要限制的用户QQ号
- `功能名`: 要禁止的功能名称（如 maicn、ping 等）
- `操作`: 可选，默认为 `*`（所有操作）
- `--scope`: 权限范围（global、group、private）
- `--scope-id`: 范围ID（群号等）

**示例**:
```
# 全局禁止用户123456使用maicn功能
/permission add_blacklist 123456 maicn --scope global

# 在特定群组禁止用户使用ping功能
/permission add_blacklist 123456 ping --scope group --scope-id 987654321
```

#### 移除黑名单

**命令**: `/permission remove_blacklist <用户ID> <功能名> [操作] [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 移除用户的黑名单限制

**示例**:
```
/permission remove_blacklist 123456 maicn --scope global
```

#### 查看黑名单

**命令**: `/permission list_blacklist <用户ID> [--scope <范围>] [--scope-id <范围ID>]`

**功能**: 查看用户的黑名单规则

**示例**:
```
# 查看用户的所有黑名单
/permission list_blacklist 123456

# 查看用户在特定群组的黑名单
/permission list_blacklist 123456 --scope group --scope-id 987654321
```

## 使用技巧

### 1. 命令别名

许多命令支持中文别名，例如：
- `/ping` = `。在吗`
- `/roll` = `。随机数` = `。随机`
- `/help` = `。帮助` = `。帮助文档` = `。怎么用`

### 2. 参数说明

- `<参数>`: 必需参数
- `[参数]`: 可选参数
- `--选项`: 命令选项

### 3. 错误处理

如果命令执行失败，机器人会返回相应的错误信息。常见错误：
- 权限不足
- 参数格式错误
- 账号未绑定
- 网络连接问题

### 4. 最佳实践

- 首次使用前先绑定舞萌账号
- 定期更新查分器数据
- 合理设置权限范围
- 使用有意义的绑定名称

## 常见问题

### Q: 如何绑定第一个账号？
A: 使用 `/maicn add <sgwcmaid>` 命令绑定舞萌官方账号。

### Q: 为什么无法使用某些命令？
A: 可能是权限不足，请联系管理员分配相应权限。

### Q: 如何切换不同的档案？
A: 使用 `/maicn current <档案名>` 命令切换档案。

### Q: B50图片生成失败怎么办？
A: 确保已绑定对应的查分器账号，并且数据已同步。

### Q: 如何成为管理员？
A: 需要现有管理员使用权限管理命令为您分配管理员角色。

## 技术支持

如果遇到问题或需要帮助，请：
1. 查看本文档的常见问题部分
2. 使用 `/help` 命令获取基本帮助
3. 联系机器人管理员
4. 查看项目的 GitHub 仓库

---

*本文档基于 RemiBot 当前版本编写，功能可能会随版本更新而变化。*