from .base import PluginBase
from .engine import PluginEngine


# --- security/plugins/audit_log.py ---
class AuditLogPlugin(PluginBase):
    name = "audit_log"
    version = "1.0.0"

    def setup(self, context):
        self.logger = context.get("logger")

    def activate(self):
        print("    审计日志插件已激活")

    def log(self, action, user):
        print(f"    [审计] {user} 执行了 {action}")


# --- security/plugins/access_control.py ---
class AccessControlPlugin(PluginBase):
    name = "access_control"
    version = "2.0.0"

    def activate(self):
        print("    访问控制插件已激活")

    def check_permission(self, user, resource):
        print(f"    [权限] 检查 {user} 是否有权访问 {resource}")
        return True


# --- trade/plugins/price_feed.py ---
class PriceFeedPlugin(PluginBase):
    name = "price_feed"
    version = "1.0.0"

    def activate(self):
        print("    行情数据插件已激活")

    def get_price(self, symbol):
        return {"symbol": symbol, "price": 100.5}


# --- trade/plugins/risk_check.py ---
class RiskCheckPlugin(PluginBase):
    name = "risk_check"

    def setup(self, context):
        self.max_amount = context.get("max_amount", 10000)

    def activate(self):
        print("    风控检查插件已激活")

    def check(self, amount):
        return amount <= self.max_amount


# English: use / ============ 使用 ============

print("=" * 60)
print("方案 C：全局注册 + 模块隔离")
print("=" * 60)

engine = PluginEngine()

print("\n  加载 security 插件:")
engine.load_from_directory("project/security/plugins", namespace="security")

print("\n  加载 trade 插件:")
engine.load_from_directory("project/trade/plugins", namespace="trade")

print("\n  激活所有插件:")
engine.activate_all()

print("\n  按模块查询插件:")
security_plugins = engine.registry.get_all("security")
print(f"    security: {list(security_plugins.keys())}")
trade_plugins = engine.registry.get_all("trade")
print(f"    trade: {list(trade_plugins.keys())}")

print("\n  跨模块通信（通过钩子）:")
engine.registry.hook("trade_executed", lambda **kw: print(f"    [security] 收到交易事件: {kw}"))
engine.registry.emit("trade_executed", order_id="001", amount=5000)