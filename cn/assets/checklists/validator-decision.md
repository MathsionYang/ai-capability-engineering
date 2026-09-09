# Validator Decision Checklist

| 路径 | 观测信号 | 处理策略 | 恢复点 | 是否回流 Eval |
| --- | --- | --- | --- | --- |
| 输入不完整 | 必填字段缺失 | 请求补充输入并停止工具调用 | input_received | 是 |
| 工具超时 | deadline exceeded | 按幂等键有限重试 | 最近 checkpoint | 是 |
| 验证失败 | expected/evidence 不满足 | 保留证据并重规划或退出 | validation_failed | 是 |
| 权限拒绝 | policy decision = deny | 不重试，转人工审批 | permission_denied | 是 |
| 重复执行 | 幂等键已存在 | 读取已有结果，禁止副作用 | 已完成事件 | 是 |
