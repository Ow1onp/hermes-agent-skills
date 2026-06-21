"""
Intent Router — classifies natural language input into task_id.

Layer 2 of Hermes v2.

v2.1 (Entity & Confidence Repair):
  - New confidence formula: base + phrase + entity + keyword + version + file
  - Integrated EntityExtractor for richer scoring
  - Clarification threshold raised to 40%
  - Target: average confidence >= 60% for real inputs
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .task_registry import TaskRegistry, TaskDefinition
from .entities import EntityExtractor, ExtractedEntities


@dataclass
class RoutingResult:
    task_id: str
    confidence: float          # 0.0–1.0
    matched_keywords: List[str] = field(default_factory=list)
    entities: Optional[ExtractedEntities] = None
    lang: str = "unknown"
    clarification_needed: bool = False
    clarification_question: str = ""

    @property
    def is_confident(self) -> bool:
        return self.confidence >= 0.5 and not self.clarification_needed


class IntentRouter:
    """Classifies natural language → task_id with calibrated confidence."""

    CONFIDENCE_HIGH = 0.70
    CONFIDENCE_CLARIFY = 0.40   # Below this → ask user
    MIN_KEYWORD_MATCHES = 1

    def __init__(self, registry: Optional[TaskRegistry] = None,
                 extractor: Optional[EntityExtractor] = None):
        self.registry = registry or TaskRegistry()
        self.extractor = extractor or EntityExtractor()

    def route(self, text: str) -> RoutingResult:
        text_lower = text.lower().strip()
        lang = self._detect_lang(text_lower)
        entities = self.extractor.extract(text_lower)

        best_task_id = "general"
        best_score = 0.0
        best_keywords: List[str] = []

        for task in self.registry.list_all():
            score, matched = self._score_task(text_lower, task, lang, entities)
            if score > best_score:
                best_score = score
                best_task_id = task.task_id
                best_keywords = matched

        confidence = min(best_score, 1.0)
        needs_clarification = confidence < self.CONFIDENCE_CLARIFY
        question = ""

        if needs_clarification:
            question = self._generate_clarification(text, best_task_id, lang)

        return RoutingResult(
            task_id=best_task_id,
            confidence=round(confidence, 3),
            matched_keywords=best_keywords,
            entities=entities,
            lang=lang,
            clarification_needed=needs_clarification,
            clarification_question=question,
        )

    def _detect_lang(self, text: str) -> str:
        cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
        return "zh" if cjk >= 2 else "en"

    def _score_task(self, text: str, task: TaskDefinition, lang: str,
                    entities: ExtractedEntities) -> tuple:
        """New calibrated scoring formula.

        base_score (0–30) + phrase_bonus (0–20) + entity_bonus (0–25)
        + keyword_bonus (0–15) + version_bonus (0–10) + file_bonus (0–5)
        = 0–105, then normalized to 0–1.
        """
        keywords = task.keywords_zh if lang == "zh" else task.keywords_en
        if not keywords:
            keywords = task.all_keywords
        if not keywords:
            return 0.0, []

        raw_score = 0.0
        matched = []

        # ── Keyword match scoring (0–40 with base) ──
        any_match = False
        for kw in keywords:
            if kw.lower() in text:
                any_match = True
                matched.append(kw)
                raw_score += 8.0  # Each exact match = 8 points
                raw_score += min(len(kw) / 10, 2.0)  # Length bonus
            elif ' ' in kw:
                parts = kw.split()
                hits = sum(1 for p in parts if p.lower() in text)
                if hits >= len(parts) * 0.5:
                    matched.append(f"{kw}(partial)")
                    raw_score += hits * 3.0

        if any_match:
            raw_score += 40.0  # Strong base bonus for relevance
        raw_score = min(raw_score, 80.0)

        # ── Phrase bonus (0–15) ──
        phrase_bonus = 0.0
        for label_val in task.label.values():
            if label_val.lower() in text:
                phrase_bonus = 15.0
                break
        if phrase_bonus == 0 and task.description:
            for desc_val in task.description.values():
                desc_words = set(desc_val.lower().split())
                text_words = set(text.lower().split())
                overlap = desc_words & text_words
                if len(overlap) >= 3:
                    phrase_bonus = 10.0
                    break
        raw_score += min(phrase_bonus, 15.0)

        # ── Entity bonus (0–25) ──
        entity_bonus = 0.0
        if entities.has_any:
            entity_bonus += 5.0
        if entities.technology and task.task_id == "create_project":
            entity_bonus += 15.0
        if entities.file_path and task.task_id in ("fix_bug", "review_code"):
            entity_bonus += 12.0
        if entities.doc_type and task.task_id == "write_docs":
            entity_bonus += 15.0
        if entities.project_type and task.task_id == "create_project":
            entity_bonus += 10.0
        raw_score += min(entity_bonus, 25.0)

        # ── Version pattern bonus (0–25) ──
        if re.search(r'v?\d+\.\d+(?:\.\d+)?', text):
            if entities.version and task.task_id == "release_version":
                raw_score += 25.0     # Strong — exact version match
            elif task.task_id == "release_version":
                raw_score += 15.0     # Good — version pattern, no exact
            elif task.task_id == "publish_project":
                raw_score += 8.0      # Weaker — could be publish too

        # ── File extension bonus (0–5) ──
        if entities.file_path:
            ext = entities.file_path.rsplit('.', 1)[-1] if '.' in entities.file_path else ''
            if ext in ('py', 'js', 'ts') and task.task_id == "fix_bug":
                raw_score += 5.0
            elif ext in ('md',) and task.task_id == "write_docs":
                raw_score += 5.0

        # ── Normalize to 0–1 (max possible ≈ 125 with all bonuses) ──
        normalized = raw_score / 125.0
        return min(normalized, 1.0), matched

    def _generate_clarification(self, text: str, task_id: str, lang: str) -> str:
        if lang == "zh":
            questions = {
                "publish_project": "是要发布项目吗？请告诉我发布什么版本。",
                "fix_bug": "需要修复什么错误？请粘贴错误信息或描述问题。",
                "create_project": "需要创建什么类型的项目？请告诉我项目名称和技术栈。",
                "release_version": "需要发布哪个版本？例如：v1.2.0",
                "write_docs": "需要写什么文档？README、FAQ、还是教程？",
                "general": "请描述你想做什么。例如：帮我发布项目、修复这个错误、创建一个项目。",
            }
        else:
            questions = {
                "publish_project": "Do you want to publish a project? Which version?",
                "fix_bug": "What bug needs fixing? Please share the error message.",
                "create_project": "What kind of project? Name and tech stack?",
                "release_version": "Which version to release? e.g. v1.2.0",
                "write_docs": "Which document? README, FAQ, or tutorial?",
                "general": "What would you like to do? e.g. publish a project, fix a bug, create a project.",
            }
        return questions.get(task_id, questions.get("general", ""))
