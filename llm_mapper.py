import groq
import json
import re
from difflib import get_close_matches

# Use Groq client (uses same API format as OpenAI)
# Please update the key here
client = groq.Groq(api_key="")

def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else "{}"

def get_llm_column_mapping(unmapped_columns, target_schema_dict, confidence_threshold=60):
    schema_fields = list(target_schema_dict.keys())
    field_descriptions = {field: target_schema_dict[field][0] if target_schema_dict[field] else "" for field in target_schema_dict}

    prompt = f"""
You are a data normalization expert. Match inconsistent or messy Excel column names to a target schema used for logistics data.

Each mapping should include:
- target: the best matching field from the schema
- confidence: a number from 0 to 100
- reason: a short explanation of the match

Only include mappings where confidence is >= {confidence_threshold}. Skip anything you're unsure of.

Target schema (field → description):
{json.dumps(field_descriptions, indent=2)}

Columns to map:
{unmapped_columns}

Format:
{{
  "Original Column Name": {{
    "target": "target_field",
    "confidence": 85,
    "reason": "brief explanation"
  }}
}}
"""

    # Send to LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert data mapping assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    print("🔍 LLM raw content:\n", content)

    cleaned = extract_json(content)
    try:
        structured_mapping = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("❌ JSON decode failed:", e)
        return {}

    # Flatten the structure into column_name: target_field
    final_mapping = {}
    unmapped_fallback = []

    for col, details in structured_mapping.items():
        if isinstance(details, dict):
            confidence = details.get("confidence", 0)
            target = details.get("target")
            if confidence >= confidence_threshold and target:
                final_mapping[col] = target
            else:
                unmapped_fallback.append(col)
        else:
            unmapped_fallback.append(col)

    # Fuzzy match anything still unmatched
    for col in unmapped_fallback:
        guess = get_close_matches(col.lower(), [f.lower() for f in schema_fields], n=1, cutoff=0.6)
        if guess:
            final_mapping[col] = next((f for f in schema_fields if f.lower() == guess[0]), None)

    return final_mapping
