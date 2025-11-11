import json

def classify_risk(policy_result, policy_description=None):
    """
    Assigns risk level to a policy based on known rules.
    """
    if policy_result["compliant"]:
        return "None"  # no risk if compliant

    # Simple rule-based example
    if "PermitRootLogin" in policy_result["explanation"]:
        return "High"
    elif "PasswordAuthentication" in policy_result["explanation"]:
        return "Medium"
    else:
        return "Low"

# Load compliance results from Step 2
with open("policy_check_results.json") as f:
    results = json.load(f)

# Apply risk classifier
for r in results:
    r["risk_level"] = classify_risk(r)

# Save updated results
with open("policy_check_results_with_risk.json", "w") as f:
    json.dump(results, f, indent=2)

# Print for review
print(json.dumps(results, indent=2))
