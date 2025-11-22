import json

input_path = "data/raw/raw_reviews.jsonl"
output_path = "data/raw/raw_reviews.json"

data = []
with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done → saved as reviews.json")