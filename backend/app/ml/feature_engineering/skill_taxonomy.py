"""
Skill Taxonomy – Hierarchical Skill Mapping
=============================================

Provides a taxonomy of skills organised by domain, with similarity
scoring between skills that belong to the same or related branches.

Used by the feature extractor to give partial credit for related
skills (e.g. "Python" ↔ "Django" in the web-development branch).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ── Taxonomy tree ──────────────────────────────────────────────────
# Each key is a domain; values are lists of skill clusters.
# Skills within the same cluster are considered related.

_TAXONOMY: dict[str, list[list[str]]] = {
    "programming": [
        ["python", "django", "flask", "fastapi"],
        ["javascript", "typescript", "react", "nextjs", "vue", "angular", "node", "express"],
        ["java", "spring", "kotlin"],
        ["c", "cpp", "csharp", "dotnet"],
        ["go", "rust"],
        ["ruby", "rails"],
        ["php", "laravel"],
        ["sql", "postgresql", "mysql", "sqlite", "mongodb", "redis"],
    ],
    "data_science": [
        ["pandas", "numpy", "scipy"],
        ["scikit-learn", "sklearn", "machine learning", "ml"],
        ["tensorflow", "pytorch", "deep learning", "dl"],
        ["nlp", "natural language processing", "transformers", "bert", "gpt"],
        ["statistics", "probability", "hypothesis testing"],
        ["data visualization", "matplotlib", "seaborn", "plotly", "tableau", "powerbi"],
    ],
    "cloud_devops": [
        ["aws", "amazon web services", "ec2", "s3", "lambda"],
        ["gcp", "google cloud", "bigquery"],
        ["azure", "microsoft cloud"],
        ["docker", "kubernetes", "k8s", "containerization"],
        ["ci/cd", "jenkins", "github actions", "gitlab ci"],
        ["terraform", "ansible", "infrastructure as code"],
        ["linux", "bash", "shell scripting"],
    ],
    "design": [
        ["ui", "ux", "user interface", "user experience", "figma", "sketch", "adobe xd"],
        ["graphic design", "photoshop", "illustrator", "indesign"],
        ["web design", "responsive design", "css", "tailwind", "bootstrap"],
    ],
    "business": [
        ["marketing", "digital marketing", "seo", "sem", "social media marketing"],
        ["sales", "business development", "lead generation"],
        ["finance", "accounting", "financial analysis", "excel"],
        ["project management", "agile", "scrum", "kanban", "jira"],
        ["product management", "product strategy", "roadmap"],
    ],
    "domain_specific": [
        ["healthcare", "medical", "clinical", "pharmacy", "nursing"],
        ["agriculture", "farming", "crop science", "agritech"],
        ["legal", "law", "compliance", "regulatory"],
        ["education", "teaching", "curriculum", "training"],
        ["manufacturing", "quality control", "six sigma", "lean"],
    ],
}


class SkillTaxonomy:
    """
    Hierarchical skill taxonomy with similarity scoring.

    Maps each skill to its domain and cluster, then computes a
    similarity score between two skills based on whether they share
    the same cluster, same domain, or are unrelated.

    Similarity range:
        1.0  – same skill (exact match)
        0.8  – same cluster (e.g. Python ↔ Django)
        0.4  – same domain but different cluster
        0.0  – unrelated
    """

    def __init__(self, taxonomy: dict[str, list[list[str]]] | None = None) -> None:
        self._taxonomy = taxonomy or _TAXONOMY
        self._skill_to_domain: dict[str, str] = {}
        self._skill_to_cluster: dict[str, int] = {}
        self._build_indices()

    def _build_indices(self) -> None:
        """Build reverse indices from skill → (domain, cluster_id)."""
        for domain, clusters in self._taxonomy.items():
            for cluster_idx, cluster in enumerate(clusters):
                for skill in cluster:
                    key = skill.lower().strip()
                    self._skill_to_domain[key] = domain
                    self._skill_to_cluster[key] = cluster_idx

    def similarity(self, skill_a: str, skill_b: str) -> float:
        """
        Compute similarity between two skills.

        Returns:
            1.0 if identical (case-insensitive),
            0.8 if in the same cluster,
            0.4 if in the same domain,
            0.0 otherwise.
        """
        a = skill_a.lower().strip()
        b = skill_b.lower().strip()

        if a == b:
            return 1.0

        domain_a = self._skill_to_domain.get(a)
        domain_b = self._skill_to_domain.get(b)

        if domain_a is None or domain_b is None:
            return 0.0

        if domain_a != domain_b:
            return 0.0

        cluster_a = self._skill_to_cluster.get(a)
        cluster_b = self._skill_to_cluster.get(b)

        if cluster_a is not None and cluster_b is not None and cluster_a == cluster_b:
            return 0.8

        return 0.4

    def best_match_score(self, candidate_skills: list[str], required_skills: list[str]) -> float:
        """
        For each required skill, find the best-matching candidate skill
        and return the average best-match score.

        Returns a value in [0, 1].
        """
        if not required_skills:
            return 0.0

        total = 0.0
        for req in required_skills:
            best = 0.0
            for cand in candidate_skills:
                score = self.similarity(cand, req)
                if score > best:
                    best = score
                    if best >= 1.0:
                        break
            total += best

        return total / len(required_skills)

    def get_domain(self, skill: str) -> str | None:
        """Return the domain a skill belongs to, or None."""
        return self._skill_to_domain.get(skill.lower().strip())

    def get_related_skills(self, skill: str) -> list[str]:
        """Return all skills in the same cluster as *skill*."""
        key = skill.lower().strip()
        domain = self._skill_to_domain.get(key)
        cluster_idx = self._skill_to_cluster.get(key)

        if domain is None or cluster_idx is None:
            return []

        return [s for s in self._taxonomy[domain][cluster_idx] if s.lower() != key]

    def expand_skills(self, skills: list[str], max_depth: int = 1) -> list[str]:
        """
        Expand a skill list by adding related skills from the taxonomy.

        With max_depth=1, adds direct cluster neighbours.
        """
        expanded: set[str] = {s.lower().strip() for s in skills}

        if max_depth >= 1:
            for skill in skills:
                related = self.get_related_skills(skill)
                expanded.update(r.lower() for r in related)

        return sorted(expanded)
