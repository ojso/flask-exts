# Bootstrap 5 Phase 2-4 迁移计划

## 🎯 总体目标
将 Bootstrap 4 + jQuery 环境完全迁移到 Bootstrap 5 + 原生 JavaScript

## 📋 迁移矩阵

| 组件 | 当前 | 替代品 | 优势 | 难度 | 兼容性 |
|------|------|--------|------|------|--------|
| jQuery | jQuery 3.x | 原生 JS | 无依赖 | ⭐⭐ | ✅ |
| Select | Select2 | Tom Select | 更轻量 | ⭐⭐⭐ | ✅ |
| 日期范围 | daterangepicker | Flatpickr | 更小 | ⭐⭐ | ✅ |
| 时间库 | Moment.js | Day.js | 更快 | ⭐ | ✅ |
| 内联编辑 | X-Editable | 原生实现 | 完全控制 | ⭐⭐⭐⭐ | ✅ |

## Phase 2：Select2 → Tom Select 迁移

### Tom Select 特性
- ✅ 无依赖（不需要 jQuery）
- ✅ 轻量级（~8KB min+gzip）
- ✅ Bootstrap 5 兼容主题
- ✅ 搜索、过滤、分组功能
- ✅ 异步加载支持

### 迁移步骤

1. **创建 tom_select_plugin.py**
   - 替代 select2_plugin.py
   - 从 CDN 加载 Tom Select

2. **更新表单字段**
   - Select2Field → TomSelectField
   - Select2TagsField → TomSelectTagsField
   - 更新 JavaScript 初始化

3. **更新模板**
   - 移除 jQuery 依赖的 select 初始化
   - 添加原生 JS 初始化代码

4. **兼容性处理**
   - 保留旧字段为已弃用
   - 提供迁移指南

## Phase 3：时间库迁移

### Flatpickr（日期范围选择）
- 替代 daterangepicker
- 配合 Day.js 使用
- 原生 JS，无依赖

### Day.js（时间处理）
- 替代 Moment.js
- 大小仅 2KB
- API 兼容 Moment.js

### 迁移步骤

1. **创建 flatpickr_plugin.py**
2. **创建 dayjs_plugin.py**
3. **更新所有日期相关字段**
4. **更新模板中的日期初始化**

## Phase 4：X-Editable 替代

### 选项
1. **原生实现**：直接使用 HTML contenteditable + 原生 JS
2. **轻量级库**：如 inline-edit.js
3. **Bootstrap 组件**：使用 Bootstrap 模态框

### 推荐方案
原生实现 + 简单的 JavaScript 处理

### 实现流程

1. 创建 HTMLElement.prototype 扩展
2. 实现内联编辑 JavaScript
3. 更新相关模板
4. 创建内联编辑插件

## 📊 工作量估计

- Tom Select 迁移：3-4 天
- Flatpickr + Day.js：2-3 天
- X-Editable 替代：4-5 天
- 测试和兼容性：2-3 天

**总计：11-15 天（中等难度项目）**

## ✅ 验收标准

- [ ] 所有选择器功能正常
- [ ] 日期选择正常
- [ ] 内联编辑功能完整
- [ ] 无 jQuery 依赖
- [ ] 浏览器兼容性测试通过
- [ ] 性能不低于当前版本
- [ ] 向后兼容性保证

## 🔄 进度跟踪

- Phase 2：[ ] 计划 [ ] 实施 [ ] 测试 [ ] 完成
- Phase 3：[ ] 计划 [ ] 实施 [ ] 测试 [ ] 完成
- Phase 4：[ ] 计划 [ ] 实施 [ ] 测试 [ ] 完成

## 📝 相关文件

- src/flask_exts/plugins/tom_select_plugin.py (待创建)
- src/flask_exts/plugins/flatpickr_plugin.py (待创建)
- src/flask_exts/plugins/dayjs_plugin.py (待创建)
- src/flask_exts/plugins/inline_edit_plugin.py (待创建)
- src/flask_exts/forms/fields/select.py (待更新)
- docs/bootstrap5_migration.rst (待创建)
