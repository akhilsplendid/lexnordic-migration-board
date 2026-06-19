from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.permits.catalog import PERMIT_ROUTES, route_families
from app.permits.readiness import match_routes


SCENARIOS = [
    {
        "name": "student found work",
        "query": "I finished higher education in Sweden and found a job",
        "facts": {"is_student": True, "completed_studies": True, "has_job_offer": True},
        "documents": ["passport_copy", "study_progress", "employment_contract"],
    },
    {
        "name": "family partner",
        "query": "I want to live with my partner in Sweden",
        "facts": {"has_family_in_sweden": True},
        "documents": ["passport_copy", "relationship_proof"],
    },
    {
        "name": "appeal rejection",
        "query": "my residence permit was rejected and I need to appeal",
        "facts": {"has_rejection": True, "has_removal_order": True},
        "documents": ["decision_letter"],
    },
    {
        "name": "visit over 90",
        "query": "I want to visit Sweden for six months",
        "facts": {"visit_days": 180},
        "documents": ["passport_copy", "maintenance_proof"],
    },
]


def main() -> int:
    print(f"routes={len(PERMIT_ROUTES)} families={len(route_families())}")
    for scenario in SCENARIOS:
        print(f"\nSCENARIO: {scenario['name']}")
        results = match_routes(
            query=scenario["query"],
            route_id=None,
            facts=scenario["facts"],
            documents=scenario["documents"],
            limit=3,
        )
        for result in results:
            route = result["route"]
            readiness = result["readiness"]
            print(
                f"- {result['match_score']:>3} | {readiness['score']:>3} "
                f"| {readiness['status']} | {route['route_id']} | {route['name']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
