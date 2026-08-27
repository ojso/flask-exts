### 2.3 发现的 Bug 和代码问题

| 问题 | 位置 | 严重程度 |
|------|------|---------|
| `on_model_change` 未定义 | `template/forms/fields/sqla.py:325` | 高 -- 运行时 AttributeError |
| 死代码（不可达） | `admin/sqla/form.py:442` | 低 |
| 变量遮蔽 `name` | `template/forms/fields/inline.py:114` | 低 |
| `contribute()` 重复代码 | `InlineModelConverter` vs `InlineOneToOneModelConverter` | 中 |
| `InlineFieldList.__init__` 无实际功能 | `template/forms/fields/inline.py:11` | 低 |

### 2.4 缺失的测试（按优先级）

1. `InlineModelFormListField` -- CRUD 操作（新增/修改/删除子记录）
2. `InlineModelConverter` -- 关系发现、表单生成完整流程
3. `InlineFieldList` -- 删除标记检测、validate跳过
4. `InlineOneToOneModelConverter` -- 一对一关系场景
5. 集成测试 -- 完整HTTP请求创建/编辑带inline子记录的父记录


## 三、Bootstrap 5 迁移方案

### 3.1 当前依赖状态

| 库 | jQuery依赖 | 替代方案 |
|---|---|---|
| jQuery 3.x | -- | 移除 |
| Bootstrap 4 | 需要 jQuery | Bootstrap 5（已预置） |
| Select2 | **强依赖** | Tom Select |
| daterangepicker | **强依赖 jQuery + Moment** | Flatpickr |
| Moment.js | 不需要（但已废弃） | Day.js |
| vanilla-editor (X-Editable) | **强依赖** | 自建轻量方案 |

#### Select2 --> Tom Select

推荐理由：API 设计直接兼容 Select2（AJAX/tags/allowClear等高级功能），迁移成本最低。

#### daterangepicker --> Flatpickr

推荐理由：覆盖全部场景（单日期/范围/时间），无 jQuery 依赖，16KB 体积。

#### Moment.js --> Day.js

推荐理由：API 几乎一致，2KB 体积，近乎 drop-in 替换。

#### X-Editable --> 自建轻量方案

推荐理由：当前仅使用4种 case（text/combodate/select2-multiple/boolean），可针对性重写。

### 3.4 模板 Breaking Changes

#### data-* 属性变更

```html
<!-- BS4 --> data-toggle="modal" data-target="#id" data-dismiss="modal"
<!-- BS5 --> data-bs-toggle="modal" data-bs-target="#id" data-bs-dismiss="modal"
```

影响文件: `admin/master.html`, `macro/menu.html`, `macro/modal.html`, `macro/form.html`, `macro/message.html`, `macro/layout.html`, `admin/model/list.html`

#### CSS 类名变更

```
mr-auto --> me-auto
ml-3 --> ms-3
float-left --> float-start
input-group-append --> 直接嵌套
close --> btn-close
form-group --> mb-3
```

---

## 四、文档与测试完善建议

### 4.1 文档现状 (评分: 2/10)

**已有**: index.rst, configure.rst(9个配置项), develop.rst, api.rst(仅Admin/View两个类autodoc)

**完全缺失**: Security/UserCenter使用指南、Admin ModelView教程、表单字段参考、信号使用、CLI命令、插件系统、架构说明、Getting Started教程

### 4.2 文档优先级

1. **Getting Started 教程** -- 从安装到完整应用（含认证+Admin）
2. **Security & UserCenter 指南** -- 认证/授权/2FA/邮件验证流程
3. **Admin ModelView 教程** -- 创建自定义数据管理视图
4. **完整配置参考** -- 整理所有 `app.config` 项
5. **完整API Reference** -- 所有公共模块 autodoc

### 4.3 测试现状 (评分: 5/10)

**优秀覆盖**: User流程(325行)、Admin SQLA(1149行)、ModelView(634行)

**完全无测试的关键模块**:

| 模块 | 重要性 |
|------|--------|
| `security/authorizer/` | 安全关键 |
| `commands.py` | 生产环境关键操作 |
| `admin/sqla/test_inlineform.py` | 空文件(复杂功能) |
| `datastore/sqla/utils/paginate.py` | 列表核心逻辑 |
| `template/forms/fields/` (inline, ajax_select, taglist, select) | 自定义字段无独立测试 |
| `email/` (sender, verify, reset) | 核心发送逻辑 |
| `admin/model/rowaction*.py` | 行操作 |
| `template/plugins/` | 15个插件全部无测试 |

### 4.4 测试优先级

1. `security/authorizer/` -- 授权是安全关键
2. `commands.py` -- CLI命令无测试
3. `admin/sqla/test_inlineform.py` -- 已创建文件但为空
4. `datastore/sqla/utils/paginate.py` -- 分页核心
5. `template/forms/fields/inline.py` + `sqla.py` -- 自定义字段
6. `email/` -- 邮件发送逻辑

---

## 五、行动计划建议

### 短期（1-2周）

1. 修复 `actived` -> `is_active` 拼写错误
2. 补充 inline_model 完整测试
3. 在 demo 中添加 inline_model 使用示例
4. 补充 authorizer 和 commands 测试
5. 编写 Getting Started 文档




---

## 六、附录：关键文件路径

```
src/flask_exts/


├── static/js/form.js                # jQuery最密集，迁移核心
├── static/js/filters.js             # jQuery第二密集




```
