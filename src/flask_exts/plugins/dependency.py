"""
=============================================================
插件依赖管理
=============================================================
"""
from .base import PluginBase

# ============================================================
#  依赖解析器
# ============================================================

class DependencyNotFoundError(Exception): pass
class CircularDependencyError(Exception): pass


def parse_dependency(dep_str):
    """解析依赖字符串: 'core.db', 'core.cache?', 'core.db>=2.0'"""
    optional = dep_str.endswith("?")
    if optional:
        dep_str = dep_str[:-1]
    version_constraint = None
    for op in (">=", "<=", "==", "!=", ">", "<"):
        if op in dep_str:
            parts = dep_str.split(op, 1)
            dep_str = parts[0]
            version_constraint = (op, parts[1])
            break
    return {"name": dep_str, "optional": optional, "version": version_constraint}


class DependencyResolver:
    """依赖解析：拓扑排序 + 循环检测 + 可选依赖 + 版本约束"""

    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        self._plugins[plugin.full_name] = plugin

    def resolve_order(self) -> list:
        graph = {n: [] for n in self._plugins}
        in_degree = {n: 0 for n in self._plugins}

        for name, plugin in self._plugins.items():
            for dep_str in plugin.dependencies:
                dep = parse_dependency(dep_str)

                # 可选依赖：不存在就跳过
                if dep["optional"] and dep["name"] not in self._plugins:
                    print(f"    [跳过可选] {name} → {dep['name']} (未安装)")
                    continue

                # 必须依赖：不存在就报错
                if dep["name"] not in self._plugins:
                    raise DependencyNotFoundError(f"{name} 依赖 {dep['name']}，但未注册")

                # 版本检查
                if dep["version"]:
                    target = self._plugins[dep["name"]]
                    op, ver = dep["version"]
                    if not self._check_version(target.version, op, ver):
                        raise DependencyNotFoundError(
                            f"{name} 要求 {dep['name']}{op}{ver}，当前 {target.version}")

                graph[dep["name"]].append(name)
                in_degree[name] += 1

        # Kahn 算法拓扑排序
        queue = sorted([n for n, d in in_degree.items() if d == 0])
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in sorted(graph[node]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._plugins):
            remaining = set(self._plugins.keys()) - set(order)
            raise CircularDependencyError(f"循环依赖: {remaining}")

        return order

    @staticmethod
    def _check_version(current, op, required):
        """简单版本比较"""
        def to_tuple(v):
            try:
                return tuple(int(x) for x in v.split("."))
            except ValueError:
                return (0,)
        c, r = to_tuple(current), to_tuple(required)
        ops = {">=": c >= r, "<=": c <= r, "==": c == r,
               "!=": c != r, ">": c > r, "<": c < r}
        return ops.get(op, True)


# ============================================================
#  插件上下文（服务定位器）
# ============================================================

class PluginContext:
    def __init__(self):
        self._resolver = DependencyResolver()
        self._active = {}

    def register(self, plugin):
        self._resolver.register(plugin)

    def get_plugin(self, full_name):
        return self._active.get(full_name)

    def startup(self):
        order = self._resolver.resolve_order()
        for name in order:
            plugin = self._resolver._plugins[name]
            plugin.setup(self)
            plugin.activate()
            self._active[name] = plugin
        return order

    def shutdown(self):
        order = self._resolver.resolve_order()
        for name in reversed(order):
            plugin = self._active.get(name)
            if plugin:
                plugin.deactivate()


# ============================================================
#  演示 1：基本依赖 + 拓扑排序
# ============================================================
print("=" * 60)
print("演示 1：依赖声明 + 拓扑排序")
print("=" * 60)


class DatabasePlugin(PluginBase):
    name = "database"; namespace = "core"
    def setup(self, ctx): self.connection = "db_ok"
    def activate(self): print(f"    ✓ {self.full_name} (conn={self.connection})")
    def get_connection(self): return self.connection


class CachePlugin(PluginBase):
    name = "cache"; namespace = "core"
    dependencies = ["core.database"]
    def setup(self, ctx):
        self.db = ctx.get_plugin("core.database")
    def activate(self):
        print(f"    ✓ {self.full_name} (using db: {self.db.get_connection()})")


class AuthPlugin(PluginBase):
    name = "auth"; namespace = "security"
    dependencies = ["core.database", "core.cache"]
    def setup(self, ctx):
        self.db = ctx.get_plugin("core.database")
        self.cache = ctx.get_plugin("core.cache")
    def activate(self): print(f"    ✓ {self.full_name}")


class AuditLogPlugin(PluginBase):
    name = "audit_log"; namespace = "security"
    dependencies = ["security.auth"]
    def setup(self, ctx): self.auth = ctx.get_plugin("security.auth")
    def activate(self): print(f"    ✓ {self.full_name}")


class TradePlugin(PluginBase):
    name = "trade"; namespace = "business"
    dependencies = ["core.database", "security.auth"]
    def setup(self, ctx):
        self.db = ctx.get_plugin("core.database")
        self.auth = ctx.get_plugin("security.auth")
    def activate(self): print(f"    ✓ {self.full_name}")


ctx = PluginContext()
for p in [TradePlugin(), AuditLogPlugin(), AuthPlugin(), CachePlugin(), DatabasePlugin()]:
    ctx.register(p)

print("\n  拓扑排序 + 启动:")
order = ctx.startup()
print(f"\n  加载顺序: {' → '.join(order)}")

print("\n  验证插件间通信:")
trade = ctx.get_plugin("business.trade")
print(f"    trade.db = {trade.db}")
print(f"    trade.auth = {trade.auth}")


# ============================================================
#  演示 2：循环依赖检测
# ============================================================
print("\n" + "=" * 60)
print("演示 2：循环依赖检测")
print("=" * 60)


class PluginA(PluginBase):
    name = "a"; namespace = "test"; dependencies = ["test.b"]

class PluginB(PluginBase):
    name = "b"; namespace = "test"; dependencies = ["test.a"]


ctx2 = PluginContext()
ctx2.register(PluginA())
ctx2.register(PluginB())

try:
    ctx2.startup()
except CircularDependencyError as e:
    print(f"  ❌ {e}")


# ============================================================
#  演示 3：缺失依赖检测
# ============================================================
print("\n" + "=" * 60)
print("演示 3：缺失依赖检测")
print("=" * 60)


class OrphanPlugin(PluginBase):
    name = "orphan"; namespace = "test"
    dependencies = ["nonexistent.plugin"]


ctx3 = PluginContext()
ctx3.register(OrphanPlugin())
try:
    ctx3.startup()
except DependencyNotFoundError as e:
    print(f"  ❌ {e}")


# ============================================================
#  演示 4：可选依赖 + 版本约束
# ============================================================
print("\n" + "=" * 60)
print("演示 4：可选依赖 + 版本约束")
print("=" * 60)


class DBPlugin2(PluginBase):
    name = "database"; namespace = "core"; version = "2.1.0"
    dependencies = []
    def activate(self): print(f"    ✓ {self.full_name} v{self.version}")


class CachePlugin2(PluginBase):
    name = "cache"; namespace = "core"; version = "1.0.0"
    dependencies = ["core.database>=2.0"]  # 版本约束
    def activate(self): print(f"    ✓ {self.full_name} v{self.version}")


class MetricsPlugin(PluginBase):
    name = "metrics"; namespace = "core"
    dependencies = ["core.cache?", "nonexistent?"]  # 可选
    def activate(self): print(f"    ✓ {self.full_name}")


ctx4 = PluginContext()
ctx4.register(DBPlugin2())
ctx4.register(CachePlugin2())
ctx4.register(MetricsPlugin())

print("\n  解析顺序:")
order = ctx4.startup()
print(f"\n  加载顺序: {' → '.join(order)}")


# ============================================================
#  演示 5：版本不兼容
# ============================================================
print("\n" + "=" * 60)
print("演示 5：版本不兼容")
print("=" * 60)


class OldDB(PluginBase):
    name = "database"; namespace = "core"; version = "1.0.0"
    dependencies = []


class NeedNewDB(PluginBase):
    name = "feature"; namespace = "test"; version = "1.0.0"
    dependencies = ["core.database>=2.0"]  # 要求 2.0+，但只有 1.0.0


ctx5 = PluginContext()
ctx5.register(OldDB())
ctx5.register(NeedNewDB())
try:
    ctx5.startup()
except DependencyNotFoundError as e:
    print(f"  ❌ {e}")


# ============================================================
#  总结
# ============================================================
print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
┌─────────────────────┬──────────────────────────────────────────┐
│ 功能                 │ 实现                                      │
├─────────────────────┼──────────────────────────────────────────┤
│ 声明依赖             │ dependencies = ["core.database"]          │
│ 可选依赖             │ dependencies = ["core.cache?"]            │
│ 版本约束             │ dependencies = ["core.db>=2.0"]           │
│ 加载顺序             │ 拓扑排序（Kahn 算法）                      │
│ 循环依赖             │ 检测并报错                                 │
│ 缺失依赖             │ 必须的报错，可选的跳过                      │
│ 插件间通信           │ setup(context) + context.get_plugin(name)  │
│ 关闭顺序             │ 逆序 deactivate                           │
└─────────────────────┴──────────────────────────────────────────┘

插件定义：
  class AuthPlugin(PluginBase):
      name = "auth"
      namespace = "security"
      dependencies = ["core.database", "core.cache?"]

      def setup(self, context):
          self.db = context.get_plugin("core.database")   # 获取依赖
          self.cache = context.get_plugin("core.cache")   # 可选依赖

      def activate(self):
          self.db.query("...")   # 使用依赖
""")
