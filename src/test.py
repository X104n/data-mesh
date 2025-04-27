import json
with open("src/platform1/marketplace.json", "w") as f:
    platform_up = '{"platform": {"domain": "10.0.3.5"} }'
    json.dump(json.loads(platform_up), f, indent=4)