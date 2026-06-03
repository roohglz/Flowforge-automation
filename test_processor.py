import sys, os
sys.path.insert(0, os.path.abspath('.'))

from processors.workflow_engine import get_workflow_stats, get_all_workflows

print("=== WORKFLOW STATS ===")
stats = get_workflow_stats()
for k, v in stats.items():
    print(f"{k}: {v}")

print("\n=== ALL WORKFLOWS ===")
workflows = get_all_workflows()
for w in workflows:
    print(f"{w['name']} | {w['status']} | {w['completion_rate']}% complete")