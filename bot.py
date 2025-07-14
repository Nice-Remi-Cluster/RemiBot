import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OnebotV11Adapter)

# nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()