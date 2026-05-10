# 01_需求说明_PRD_V2

# AI 知识点学习与音频播报系统 - V2 需求说明 PRD

## 1. 文档目的

本文档用于规划 V1 完成后的下一阶段功能。

V2 不推翻 `docs/` 中的 V1 设计，而是在已有功能上扩展：

```text
知识库
学习资料
AI 知识点提取
知识点管理
AI 题目生成
刷题练习
错题本
TTS 音频生成
音频播报
系统设置
首页仪表盘
```

V2 的核心目标是：

```text
从“能生成、能练习、能播放”
升级为
“能复习、能统计、能批量听、能导出”
```

---

## 2. 与 V1 的关系

### 2.1 V1 已有基础

V2 默认 V1 已完成以下能力：

```text
1. 知识库 CRUD
2. 学习资料保存
3. AI 从资料提取知识点
4. 知识点列表、详情、编辑、删除
5. AI 为知识点生成题目
6. 刷题练习
7. 答错进入错题本
8. 错题标记掌握 / 取消掌握 / 删除
9. 单个知识点生成 TTS 音频
10. 音频列表和播放
11. AI / TTS 设置
12. 首页基础统计
```

### 2.2 V2 不改动的 V1 规则

V2 继续遵守：

```text
不做登录注册
不做多用户权限
不做云同步
不做支付系统
不做手机 App
不做浏览器插件
前端不直接调用 AI / TTS 外部接口
API Key 不写死到代码
本地数据仍保存在 data/
SQLite 仍作为默认数据库
```

### 2.3 V2 可以新增的能力

V2 重点新增：

```text
复习计划
学习统计
知识点卡片化
批量音频 / 每日音频
AI 长文本分段和去重
导入导出
```

---

## 3. V2 产品目标

V2 的产品目标分为三层。

### 3.1 必做目标

```text
1. 能生成每日复习任务
2. 能看到知识库掌握情况
3. 能把多个知识点生成一个音频包
4. 能降低 AI 重复生成和格式错误带来的失败率
```

### 3.2 推荐目标

```text
1. 支持知识点转闪卡
2. 支持按标签、重要程度、错题状态筛选复习
3. 支持导出知识点和题目
4. 支持学习记录趋势图
```

### 3.3 可选目标

```text
1. 支持 Anki 兼容导出
2. 支持 Markdown 导入
3. 支持简单备份和恢复
4. 支持更完整的 FSRS 复习算法
```

---

## 4. V2 不做内容

V2 暂不做：

```text
账号系统
多端同步
团队协作
复杂 RAG
向量检索问答
PDF 深度解析
Word 深度解析
OCR
桌面客户端打包
移动端 App
插件市场
付费系统
```

说明：

```text
data/vector_store/ 可以继续保留，但 V2 不强制启用 RAG。
data/uploads/ 可以继续保留，但 V2 不强制做复杂文件解析。
```

---

## 5. 用户角色

V2 仍然只有一个角色：

```text
本机学习者
```

用户目标：

```text
1. 导入学习资料
2. 提取知识点
3. 练题
4. 复习错题和重点
5. 听每日音频
6. 查看学习进度
```

---

## 6. 核心业务对象

V2 继续使用 V1 的核心对象：

```text
knowledge_bases
materials
knowledge_points
questions
answer_records
wrong_questions
audio_files
app_settings
```

V2 建议新增对象：

```text
review_tasks
flashcards
study_stats
export_tasks
```

说明：

```text
review_tasks 用于每日复习。
flashcards 用于知识点卡片化。
study_stats 可以先不建表，优先从 answer_records / wrong_questions 聚合。
export_tasks 只有异步导出时才需要，V2 初期可不建。
```

---

# 7. 功能需求

## 7.1 复习计划

### 功能

用户可以看到每日待复习内容，并完成复习。

### 复习来源

```text
1. 错题
2. 标记未掌握的知识点
3. importance = high 的知识点
4. 最近新增但未练习的知识点
```

### 页面

建议新增：

```text
ReviewView
```

菜单名称：

```text
复习计划
```

### 展示内容

```text
今日待复习数量
逾期复习数量
已完成数量
复习任务列表
任务来源
关联知识库
关联知识点
下一次复习时间
```

### 操作

```text
开始复习
标记已掌握
稍后复习
查看知识点详情
查看关联错题
```

### 初版复习规则

V2 初期不强制实现复杂 FSRS。

推荐简单规则：

```text
首次复习：当天
答错后：第 1 天复习
标记未掌握：第 1 天复习
标记已掌握：第 3 天复习
连续掌握 2 次：第 7 天复习
连续掌握 3 次：第 15 天复习
```

后续再升级为 FSRS。

---

## 7.2 学习统计

### 功能

首页和统计页展示学习进度。

### 首页增强

在现有 DashboardView 上增加：

```text
今日新增知识点
今日练题数量
今日正确率
今日复习完成数
待复习数量
错题数量
音频数量
知识库掌握度
```

### 统计页

可选新增：

```text
StatsView
```

### 统计维度

```text
按知识库统计
按日期统计
按题目难度统计
按知识点重要程度统计
按错题状态统计
```

### 图表

V2 初期可以先用 Element Plus 表格和数字卡片。

后续可增加：

```text
折线图
柱状图
掌握度进度条
```

---

## 7.3 知识点卡片化

### 功能

用户可以把知识点转换为闪卡，用于快速记忆。

### 卡片类型

```text
basic 正向卡
reverse 反向卡
cloze 填空卡
```

### 生成方式

```text
手动创建
从知识点一键生成
AI 自动生成
```

### 字段

```text
front 正面
back 背面
card_type 卡片类型
knowledge_point_id 关联知识点
review_status 复习状态
```

### 页面

建议新增：

```text
FlashcardView
```

也可以先集成到知识点详情页。

---

## 7.4 批量音频和每日音频

### 功能

在 V1 单个知识点音频基础上，支持多个知识点合成一个学习音频。

### 音频类型

```text
knowledge_point 单个知识点音频
collection 多知识点合集音频
daily_review 每日复习音频
wrong_question 错题复习音频
```

### 操作入口

```text
知识点列表：勾选多个知识点后生成音频
复习计划页：生成今日复习音频
错题本：生成错题复习音频
音频播报页：查看所有音频
```

### 生成规则

```text
1. 后端拼接播报文本
2. 文本过长时分段调用 TTS
3. 生成多个音频片段
4. V2 初期可以先不合并文件，按顺序播放
5. 后续再做音频合并
```

### 文件命名

继续兼容 V1：

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

V2 新增：

```text
collection_{timestamp}.mp3
daily_review_{date}_{timestamp}.mp3
wrong_questions_{timestamp}.mp3
```

---

## 7.5 AI 长文本分段

### 功能

当资料正文超过 V1 限制时，系统自动分段提取知识点。

### 流程

```text
1. 后端检测 content 长度
2. 超过阈值时自动切分
3. 每段调用 AI 提取知识点
4. 合并结果
5. 按 title / summary 去重
6. 保存到 knowledge_points
```

### 用户提示

```text
资料较长，系统将分段提取，可能需要更长时间。
```

### 限制

```text
单次最多分 10 段
每段建议 5000 到 8000 中文字
超过总限制时仍提示用户拆分
```

---

## 7.6 AI 去重和修复

### 知识点去重

V1 规则：

```text
同一 material_id 下 title 完全相同则跳过
```

V2 增强：

```text
title 标准化后相同则跳过
title 相似度高时提示用户合并
summary 高度相似时提示用户检查
```

### 题目去重

V1 规则：

```text
同一 knowledge_point_id 下 stem 完全相同则跳过
```

V2 增强：

```text
stem 标准化后相同则跳过
选项顺序不同但题干相同也视为重复
```

### JSON 修复

当 AI 返回无法解析的 JSON 时：

```text
自动调用一次 JSON 修复 Prompt
仍失败则返回明确错误
保存原始返回，方便排错
```

---

## 7.7 导入导出

### 导出

V2 建议先支持：

```text
知识点 CSV 导出
题目 CSV 导出
错题 CSV 导出
```

后续支持：

```text
Anki CSV 导出
Anki apkg 导出
Markdown 导出
```

### 导入

V2 可选支持：

```text
Markdown 文本导入
CSV 知识点导入
```

暂不做：

```text
PDF 深度解析
Word 深度解析
OCR
```

---

## 7.8 设置增强

### AI 设置

新增或优化：

```text
最大生成题目数量
资料最大长度
长文本分段开关
JSON 修复开关
AI 原始返回日志开关
```

### TTS 设置

新增：

```text
语速
音色
音频格式
批量音频最大知识点数量
```

### 复习设置

新增：

```text
每日复习上限
是否包含已掌握错题
是否优先复习 high 重要程度知识点
```

---

# 8. V2 页面清单

V2 建议页面：

```text
DashboardView 首页增强
ReviewView 复习计划
StatsView 学习统计
FlashcardView 闪卡
KnowledgePointListView 批量操作增强
KnowledgePointDetailView 卡片和复习状态增强
WrongQuestionView 复习入口增强
AudioView 批量音频增强
SettingsView 设置增强
```

V2 初期必须做：

```text
DashboardView 首页增强
ReviewView 复习计划
AudioView 批量音频增强
SettingsView 设置增强
```

---

# 9. V2 接口清单

建议新增接口：

```text
GET    /api/review/tasks
POST   /api/review/tasks/generate
POST   /api/review/tasks/{id}/complete
POST   /api/review/tasks/{id}/snooze

GET    /api/stats/overview
GET    /api/stats/knowledge-bases

GET    /api/flashcards
POST   /api/flashcards
POST   /api/flashcards/generate-from-point/{knowledge_point_id}
PUT    /api/flashcards/{id}
DELETE /api/flashcards/{id}

POST   /api/tts/generate-batch
POST   /api/tts/generate-daily-review

GET    /api/export/knowledge-points.csv
GET    /api/export/questions.csv
GET    /api/export/wrong-questions.csv
```

命名规则继续遵守 V1：

```text
接口统一放在 /api 下
前端通过 src/api/*.ts 封装
后端 routes 按业务拆分
```

---

# 10. V2 验收标准

V2 第一阶段完成后，应满足：

```text
1. 不破坏 V1 主流程
2. 首页统计仍正常
3. 可以生成今日复习任务
4. 可以完成复习任务
5. 可以按知识库查看学习统计
6. 可以选择多个知识点生成音频
7. AI 长文本分段不会导致重复保存大量知识点
8. 设置页可以保存新增配置
9. 前端 loading / 错误 / 空状态完整
10. 数据重启后仍存在
```

V2 不通过条件：

```text
1. V1 的资料导入、AI 提取、刷题、错题、音频任一主流程不可用
2. API Key 出现在 git 待提交文件中
3. data/、app.db、音频文件出现在 git 待提交文件中
4. 批量 AI / TTS 操作没有数量限制
5. 长任务没有 loading 或重复点击保护
```

---

# 11. 推荐开发顺序

建议按阶段推进：

```text
阶段 19：V1 最终验收和问题修复
阶段 20：首页统计增强
阶段 21：复习计划数据表和接口
阶段 22：复习计划页面
阶段 23：学习统计接口和页面
阶段 24：批量音频生成
阶段 25：AI 长文本分段
阶段 26：AI 去重和 JSON 修复
阶段 27：知识点闪卡
阶段 28：导入导出
阶段 29：V2 整体联调
阶段 30：V2 验收
```

优先级：

```text
能运行 > 不破坏 V1 > 能复习 > 能统计 > 能批量听 > AI 更稳定 > 导入导出 > 更好看
```

---

# 12. 总结

V2 的重点不是增加复杂概念，而是补齐学习闭环：

```text
导入资料
提取知识点
生成题目
刷题
进入错题
生成复习任务
每日复习
生成复习音频
查看学习统计
```

第一批建议只做：

```text
首页统计增强
复习计划
批量音频
AI 长文本分段和去重
```

这些功能与现有 V1 架构最贴合，改动可控，用户收益明显。
