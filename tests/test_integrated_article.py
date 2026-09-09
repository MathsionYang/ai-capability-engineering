import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
ARTICLE = ROOT / "cn" / "articles" / "Agent可信执行闭环：从Trace、Evals到可恢复执行.md"


class IntegratedArticleTest(unittest.TestCase):
    def test_article_covers_execution_contract_and_links(self):
        document = ARTICLE.read_text(encoding="utf-8")
        for term in ("Goal", "Plan", "Tool Call", "Observation", "Validation", "Checkpoint", "Artifact", "Trace", "Evals", "Replay", "失败恢复", "发布门禁"):
            self.assertIn(term, document)
        for target in (
            "Agent可观测性实战：从日志、Trace到Replay.md",
            "Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md",
            "Agent的自动化评估体系（Evals）：从单元测试到集成评测.md",
            "Agent状态管理与断点续传：Checkpointer机制深度解析.md",
            "Agent自我纠错与验证机制设计.md",
            "assets/examples/code-repair-agent/README.md",
            "assets/schemas/trace-event.md",
            "assets/schemas/checkpoint-state.yaml",
            "assets/schemas/eval-case.yaml",
            "assets/checklists/validator-decision.md",
            "assets/checklists/regression-report.md",
        ):
            self.assertIn(target, document)
        for command in ("python run_demo.py --scenario success", "python run_demo.py --scenario tool-timeout", "python run_evals.py --cases eval_cases.yaml"):
            self.assertIn(command, document)


if __name__ == "__main__":
    unittest.main()
