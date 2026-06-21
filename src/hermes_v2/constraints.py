"""
Constraint Engine — auto-generates structured constraint prompts.

Layer 4 of Hermes v2.

v2.1: Entity injection — user-specific entities (technology, file_path,
      version, etc.) are injected into the generated constraint prompt.
      No more generic "创建一个 Python 项目" when the user said FastAPI.
"""
from typing import Optional

from .task_registry import TaskDefinition
from .entities import ExtractedEntities


class ConstraintEngine:

    def generate(
        self, task: TaskDefinition, user_input: str,
        lang: str = "zh", entities: Optional[ExtractedEntities] = None,
    ) -> str:
        persona = task.workflow[0].persona if task.workflow else "Assistant"

        sections = []
        sections.append(self._authority(persona, lang))
        sections.append(self._mission(task, user_input, lang, entities))
        sections.append(self._constraints_block(task, lang))
        if task.workflow:
            sections.append(self._workflow_block(task, lang))
        sections.append(self._success_block(task, lang))

        return "\n\n".join(s for s in sections if s)

    def _authority(self, persona: str, lang: str) -> str:
        if lang == "zh":
            return (
                "## Authority\n\n"
                f"你是 {persona}。\n\n"
                "你的职责是完成用户指定的任务。\n\n"
                "按照系统的约束和规则执行。"
            )
        return (
            "## Authority\n\n"
            f"You are the {persona}.\n\n"
            "Your responsibility is to complete the user's task.\n\n"
            "Follow the system's constraints and rules."
        )

    def _mission(self, task: TaskDefinition, user_input: str,
                 lang: str, entities: Optional[ExtractedEntities]) -> str:
        desc = task.description.get(lang, task.description.get("en", ""))

        if lang == "zh":
            lines = [
                "## Mission",
                "",
                f"用户请求：{user_input}",
                f"任务类型：{desc}",
            ]
            # ── Entity injection ──
            if entities and entities.has_any:
                lines.append("")
                lines.append("检测到的实体：")
                if entities.technology:
                    lines.append(f"- 技术栈：{entities.technology}")
                if entities.language:
                    lines.append(f"- 编程语言：{entities.language}")
                if entities.file_path:
                    lines.append(f"- 文件路径：{entities.file_path}")
                if entities.version:
                    lines.append(f"- 版本号：{entities.version}")
                if entities.doc_type:
                    lines.append(f"- 文档类型：{entities.doc_type}")
                if entities.project_type:
                    lines.append(f"- 项目类型：{entities.project_type}")

            lines.append("")
            lines.append("请按照下面的工作流步骤执行。")
            return "\n".join(lines)
        else:
            lines = [
                "## Mission",
                "",
                f"User request: {user_input}",
                f"Task type: {desc}",
            ]
            if entities and entities.has_any:
                lines.append("")
                lines.append("Detected entities:")
                if entities.technology:
                    lines.append(f"- Technology: {entities.technology}")
                if entities.language:
                    lines.append(f"- Language: {entities.language}")
                if entities.file_path:
                    lines.append(f"- File: {entities.file_path}")
                if entities.version:
                    lines.append(f"- Version: {entities.version}")
                if entities.doc_type:
                    lines.append(f"- Doc type: {entities.doc_type}")
                if entities.project_type:
                    lines.append(f"- Project type: {entities.project_type}")
            lines.append("")
            lines.append("Follow the workflow steps below.")
            return "\n".join(lines)

    def _constraints_block(self, task: TaskDefinition, lang: str) -> str:
        if not task.constraints:
            return ""
        header = "## Constraints"
        lines = [header, ""]
        for c in task.constraints:
            lines.append(f"- {c}")
        return "\n".join(lines)

    def _workflow_block(self, task: TaskDefinition, lang: str) -> str:
        header = "## Execution Rules"
        lines = [header, ""]
        for i, step in enumerate(task.workflow, 1):
            lines.append(f"{i}. Step {i}: {step.description}")
        return "\n".join(lines)

    def _success_block(self, task: TaskDefinition, lang: str) -> str:
        if not task.success_criteria:
            return ""
        header = "## Success Criteria"
        lines = [header, ""]
        for c in task.success_criteria:
            lines.append(f"- {c}")
        return "\n".join(lines)

    def generate_simple(self, task: TaskDefinition, user_input: str,
                        lang: str = "zh",
                        entities: Optional[ExtractedEntities] = None) -> str:
        persona = task.workflow[0].persona if task.workflow else "Assistant"
        desc = task.description.get(lang, "")

        # Entity-aware simple prompt
        entity_context = ""
        if entities and entities.has_any:
            parts = []
            if entities.technology:
                parts.append(f"{entities.technology}")
            if entities.language:
                parts.append(f"{entities.language}")
            if entities.project_type:
                parts.append(f"{entities.project_type}")
            if parts:
                entity_context = f"（{'/'.join(parts)}）"

        if lang == "zh":
            return (
                f"用户想：{user_input}\n\n"
                f"作为 {persona}，请完成{entity_context}：{desc}\n\n"
                f"约束：{'；'.join(task.constraints[:3])}。\n"
                f"完成后检查：{'；'.join(task.success_criteria[:3])}。"
            )
        return (
            f"User wants to: {user_input}\n\n"
            f"As {persona}, complete{entity_context}: {desc}\n\n"
            f"Constraints: {'; '.join(task.constraints[:3])}.\n"
            f"Verify: {'; '.join(task.success_criteria[:3])}."
        )
