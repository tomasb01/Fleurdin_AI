import pandas as pd
import json
import random
import re

# Configuration
input_file = r"C:\Projects\Fleurdin_AI\Raw_data\Pro_trenovani\EO_prehled oleju_raw data.csv.xlsx"
output_file = r"C:\Projects\Fleurdin_AI\EO_dataset_huggingface.json"

# Load Excel file
print("Loading data...")
df = pd.read_excel(input_file, skiprows=2)
df = df.dropna(how='all')
df = df[df['ID'].notna()]

print(f"Loaded {len(df)} essential oils")

# System message
system_message = "Jsi expert na esenciální oleje a aromaterapii. Odpovídáš přesně a věcně na otázky o esenciálních olejích."

# Question templates with variations
question_templates = {
    'general': [
        "Co je {name}?",
        "Řekni mi o {name}.",
        "Jaké jsou vlastnosti {name}?",
        "Pověz mi o esenciálním oleji {name}.",
        "Co víš o {name}?",
        "Vysvětli mi {name}.",
        "Jaký je esenciální olej {name}?",
        "Co je to {name}?",
    ],
    'body_effects': [
        "Jaké jsou účinky {name} na tělo?",
        "Jak {name} působí na tělo?",
        "K čemu se používá {name} pro tělo?",
        "Jaké má {name} tělesné účinky?",
        "Co dělá {name} s tělem?",
        "Jak {name} ovlivňuje tělo?",
        "Řekni mi účinky {name} na tělo.",
        "Na co je {name} dobrý pro tělo?",
    ],
    'psyche_effects': [
        "Jaké jsou účinky {name} na psychiku?",
        "Jak {name} působí na mysl?",
        "Jak {name} ovlivňuje psychiku?",
        "Co dělá {name} s psychikou?",
        "Jaké má {name} mentální účinky?",
        "Jak {name} působí na emoce?",
        "Co {name} dělá pro duševní zdraví?",
        "Jak {name} ovlivňuje emoce?",
        "Na co je {name} dobrý pro psychiku?",
    ],
    'usage': [
        "Na co se používá {name}?",
        "Kdy použít {name}?",
        "V jakých případech použít {name}?",
        "Při čem pomáhá {name}?",
        "K čemu slouží {name}?",
        "Jak použít {name}?",
    ],
    'specific_effect': [
        "Pomůže {name} při {effect}?",
        "Je {name} dobrý na {effect}?",
        "Můžu použít {name} na {effect}?",
        "Funguje {name} při {effect}?",
        "Pomáhá {name} s {effect}?",
        "Má {name} účinek na {effect}?",
    ],
    'reverse': [
        "Který esenciální olej pomáhá při {effect}?",
        "Co použít na {effect}?",
        "Jaký olej je dobrý na {effect}?",
        "Který olej pomůže s {effect}?",
        "Co je účinné při {effect}?",
        "Jaký esenciální olej použít na {effect}?",
    ],
    'category': [
        "Jaké má {name} účinky v kategorii {category}?",
        "Jak {name} působí na {category}?",
        "Co dělá {name} pro {category}?",
        "Jaké jsou účinky {name} na {category}?",
    ],
    'comparison': [
        "Má {name} antibakteriální účinky?",
        "Je {name} antioxidant?",
        "Působí {name} protizánětlivě?",
        "Má {name} uklidňující účinky?",
        "Je {name} vhodný pro kůži?",
    ]
}

def parse_effects(text):
    """Parse effects text into categories"""
    if pd.isna(text) or not text:
        return {}

    categories = {}
    current_category = "OBECNÉ"

    # Split by category markers
    parts = re.split(r'([A-ZĚŠČŘŽÝÁÍÉÚŮŇ/ ]+:)', str(text))

    for i in range(len(parts)):
        part = parts[i].strip()
        if part.endswith(':'):
            current_category = part[:-1].strip()
        elif part and i > 0:
            if current_category not in categories:
                categories[current_category] = []
            # Split by comma and clean
            effects = [e.strip() for e in part.split(',') if e.strip()]
            categories[current_category].extend(effects)

    return categories

def clean_effect(effect):
    """Clean effect text for questions"""
    effect = effect.lower()
    effect = re.sub(r'^(na |při |proti |p.i )', '', effect)
    return effect.strip()

# Generate dataset
dataset = []

for idx, row in df.iterrows():
    name = str(row['Název EO']).strip()
    eng_name = str(row.get('Anglický název', '')).strip() if pd.notna(row.get('Anglický název')) else ''
    latin_name = str(row.get('Latinský název', '')).strip() if pd.notna(row.get('Latinský název')) else ''
    vibration = str(row.get('Vibrace v MHz', '')).strip() if pd.notna(row.get('Vibrace v MHz')) else ''
    body_effects = str(row.get('Účinky na tělo', '')).strip() if pd.notna(row.get('Účinky na tělo')) else ''
    psyche_effects = str(row.get('Účinky na psychiku / emoce', '')).strip() if pd.notna(row.get('Účinky na psychiku / emoce')) else ''

    if not name or name == 'nan':
        continue

    print(f"Generating Q&A for: {name}")

    # Parse effects into categories
    body_categories = parse_effects(body_effects)
    psyche_categories = parse_effects(psyche_effects)

    # Collect all effects for specific questions
    all_body_effects = []
    for cat_effects in body_categories.values():
        all_body_effects.extend(cat_effects)

    all_psyche_effects = []
    for cat_effects in psyche_categories.values():
        all_psyche_effects.extend(cat_effects)

    # 1. GENERAL QUESTIONS (8 variations)
    for template in question_templates['general']:
        question = template.format(name=name)
        answer = f"{name}"
        if eng_name and eng_name != 'nan':
            answer += f" (anglicky: {eng_name})"
        if latin_name and latin_name != 'nan':
            answer += f" (latinsky: {latin_name})"
        answer += " je esenciální olej"
        if vibration and vibration != 'nan':
            answer += f" s vibrací {vibration}"
        answer += "."

        if body_effects:
            answer += f" Účinky na tělo: {body_effects[:300]}"
            if len(body_effects) > 300:
                answer += "..."

        if psyche_effects:
            answer += f" {psyche_effects[:300]}"
            if len(psyche_effects) > 300:
                answer += "..."

        dataset.append({
            "text": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ]
        })

    # 2. BODY EFFECTS QUESTIONS (8 variations)
    for template in question_templates['body_effects']:
        question = template.format(name=name)
        answer = f"{name} má tyto účinky na tělo: {body_effects}" if body_effects else f"Nemám dostupné informace o účincích {name} na tělo."

        dataset.append({
            "text": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ]
        })

    # 3. PSYCHE EFFECTS QUESTIONS (9 variations)
    for template in question_templates['psyche_effects']:
        question = template.format(name=name)
        answer = f"{name} působí na psychiku následovně: {psyche_effects}" if psyche_effects else f"Nemám dostupné informace o účincích {name} na psychiku."

        dataset.append({
            "text": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ]
        })

    # 4. USAGE QUESTIONS (6 variations)
    for template in question_templates['usage']:
        question = template.format(name=name)
        answer = f"{name} se používá "
        if all_body_effects:
            answer += f"zejména pro: {', '.join(all_body_effects[:8])}"
        if all_psyche_effects:
            answer += f". Na psychiku: {', '.join(all_psyche_effects[:5])}"

        dataset.append({
            "text": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ]
        })

    # 5. SPECIFIC EFFECT QUESTIONS (30-40 variations)
    # Take first 15 body effects
    for effect in all_body_effects[:15]:
        effect_clean = clean_effect(effect)
        if len(effect_clean) > 3:
            # Question about this specific oil
            template = random.choice(question_templates['specific_effect'])
            question = template.format(name=name, effect=effect_clean)
            answer = f"Ano, {name} pomáhá při {effect_clean}."

            dataset.append({
                "text": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })

            # Reverse question
            template = random.choice(question_templates['reverse'])
            question = template.format(effect=effect_clean)
            answer = f"{name} je dobrý na {effect_clean}."

            dataset.append({
                "text": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })

    # 6. PSYCHE SPECIFIC QUESTIONS (10-15 variations)
    for effect in all_psyche_effects[:8]:
        effect_clean = clean_effect(effect)
        if len(effect_clean) > 3:
            template = random.choice(question_templates['specific_effect'])
            question = template.format(name=name, effect=effect_clean)
            answer = f"Ano, {name} pomáhá při {effect_clean}."

            dataset.append({
                "text": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })

    # 7. CATEGORY QUESTIONS (variable, depends on categories)
    for category, effects in body_categories.items():
        if effects:
            template = random.choice(question_templates['category'])
            question = template.format(name=name, category=category.lower())
            answer = f"{name} má v kategorii {category.lower()} tyto účinky: {', '.join(effects[:10])}"

            dataset.append({
                "text": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })

print(f"\nTotal Q&A pairs generated: {len(dataset)}")

# Save to JSON
print(f"Saving to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n=== DATASET STATISTICS ===")
print(f"Total Q&A pairs: {len(dataset)}")
print(f"Essential oils: {len(df)}")
print(f"Average Q&A per oil: {len(dataset) / len(df):.1f}")
print(f"\nDataset saved to: {output_file}")
print(f"\nReady for HuggingFace training!")
