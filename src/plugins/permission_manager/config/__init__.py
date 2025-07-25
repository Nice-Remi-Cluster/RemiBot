"""权限管理插件配置模块

包含权限管理的配置文件。
"""

from pathlib import Path

# 配置文件目录
CONFIG_DIR = Path(__file__).parent

# 配置文件路径
MODEL_PATH = CONFIG_DIR / "rbac_model.conf"
POLICY_PATH = CONFIG_DIR / "rbac_policy.csv"

__all__ = ["CONFIG_DIR", "MODEL_PATH", "POLICY_PATH"]