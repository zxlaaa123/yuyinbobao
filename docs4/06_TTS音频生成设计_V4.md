# 06_TTS音频生成设计_V4

# AI Study Cast - V4 TTS 音频生成设计

## 1. TTS 原则

V4 继续支持：

```text
mock provider
XiaomiTTSProvider 预留
```

必须遵守：

```text
1. TTS 调用必须走后端。
2. 前端不直接请求外部 TTS。
3. API Key 从配置读取。
4. 不写死真实小米接口地址。
5. mock provider 必须可用。
```

---

## 2. 音频内容格式

V4 音频文本建议：

```text
知识点标题
核心解释
易错提醒
复习问题
```

示例结构：

```text
知识点：xxx。
核心解释：xxx。
易错提醒：xxx。
请你思考：xxx。
```

---

## 3. 批量生成

支持：

```text
按知识点批量生成
按知识库批量生成
按今日复习计划批量生成
```

失败处理：

```text
1. 单个知识点失败不影响其他知识点。
2. 记录每个音频的成功或失败状态。
3. 前端展示成功数量和失败数量。
```

---

## 4. 播放列表

音频页支持：

```text
按知识库筛选
按今日复习筛选
按已听 / 未听筛选
倍速播放
标记已听
重新生成
删除音频
```

删除音频要求：

```text
1. 前端二次确认。
2. 删除数据库记录。
3. 尝试删除本地文件。
4. 本地文件不存在时不报致命错误。
```

---

## 5. 数据保存

audio_files 增强字段：

```text
duration_seconds
listened
listened_at
playlist_name
playback_source
```

音频文件命名继续使用：

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

保存目录：

```text
data/audio/
```

