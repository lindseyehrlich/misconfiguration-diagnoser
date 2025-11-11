import json

# ----------------------------
# 1. Sample structured policies (from Step 1)
# ----------------------------
# Normally loaded from structured_policies.json
policies = [
    {
        "policy_id": 1,
        "description": "SSH root login must be disabled",
        "target_config": "sshd_config PermitRootLogin",
        "expected_value": "no",
        "notes": ""
    },
    {
        "policy_id": 2,
        "description": "Password authentication must be disabled",
        "target_config": "sshd_config PasswordAuthentication",
        "expected_value": "no",
        "notes": ""
    }
]

# ----------------------------
# 2. Sample system configuration
# ----------------------------
# Normally collected from actual system files
ssh_config = {
    "PermitRootLogin": "yes",
    "PasswordAuthentication": "no",
    "PermitEmptyPasswords": "no"
}

# ----------------------------
# 3. Policy checking function
# ----------------------------
def check_policy(policy, config_dict):
    """
    Compare policy target_config with actual system config.
    Returns compliance result dictionary.
    """
    # Extract the key from target_config (last word)
    target_key = policy["target_config"].split()[-1]
    expected_value = policy["expected_value"]
    
    current_value = config_dict.get(target_key, "NOT SET")
    compliant = str(current_value).lower() == str(expected_value).lower()
    
    explanation = (
        f"{target_key} is set to {current_value}, expected {expected_value}"
        if not compliant else
        "Compliant"
    )
    
    return {
        "policy_id": policy["policy_id"],
        "compliant": compliant,
        "current_value": current_value,
        "explanation": explanation
    }

# ----------------------------
# 4. Check all policies
# ----------------------------
results = [check_policy(p, ssh_config) for p in policies]

# ----------------------------
# 5. Save results to JSON
# ----------------------------
with open("policy_check_results.json", "w") as f:
    json.dump(results, f, indent=2)

# ----------------------------
# 6. Print results
# ----------------------------
print(json.dumps(results, indent=2))
