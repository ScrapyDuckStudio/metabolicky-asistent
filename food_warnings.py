from logic import txt


def detect_food_warnings(food_name: str, health_conditions: dict) -> list:
    name_lower = food_name.lower()
    warnings = []
    gluten_kw = ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten', 'psenica', 'jacmen', 'raz', 'muka', 'chlieb', 'lepok']
    dairy_kw = ['milk', 'cheese', 'yogurt', 'cream', 'soy', 'mlieko', 'syr', 'jogurt', 'smotana', 'soja']
    histamine_kw = ['tomato', 'spinach', 'avocado', 'eggplant', 'cheese', 'wine', 'vinegar', 'sauerkraut',
                    'fermented', 'shrimp', 'tuna', 'paradaj', 'spenat', 'sir', 'vino']
    gastritis_kw = ['chili', 'pepper', 'coffee', 'lemon', 'onion', 'garlic', 'fried', 'korenie', 'kava',
                    'citron', 'cesnak', 'cibuľa', 'vypraz']
    purine_kw = ['beef', 'pork', 'liver', 'beer', 'shrimp', 'sardine', 'hovadz', 'bravcov', 'pecen', 'pivo', 'krevet', 'sardyn']
    oxalate_kw = ['spinach', 'rhubarb', 'chocolate', 'nuts', 'spenat', 'rebarbora', 'cokolada', 'orech']
    candida_kw = ['sugar', 'cukor', 'fruit', 'ovocie', 'honey', 'med', 'sirup', 'syrup', 'chocolate', 'cokolada']
    osteo_kw = ['caffeine', 'coffee', 'kava', 'soda', 'cola', 'energy', 'limonada']

    if (health_conditions.get('has_celiakia') or health_conditions.get('has_hashi')) and any(x in name_lower for x in gluten_kw):
        warnings.append(txt("warn_gluten"))
    if health_conditions.get('has_hashi') and any(x in name_lower for x in dairy_kw):
        warnings.append(txt("warn_milk"))
    if health_conditions.get('has_hit') and any(x in name_lower for x in histamine_kw):
        warnings.append(txt("warn_hit"))
    if (health_conditions.get('has_gastritis') or health_conditions.get('has_sibo')) and any(x in name_lower for x in gastritis_kw):
        warnings.append(txt("warn_gastritis"))
    if health_conditions.get('has_gout') and any(x in name_lower for x in purine_kw):
        warnings.append(txt("warn_purines"))
    if health_conditions.get('has_kidney_stones') and any(x in name_lower for x in oxalate_kw):
        warnings.append(txt("warn_oxalates"))
    if health_conditions.get('has_candida') and any(x in name_lower for x in candida_kw):
        warnings.append(txt("warn_candida"))
    if health_conditions.get('has_leaky_gut') and any(x in name_lower for x in gluten_kw + dairy_kw):
        warnings.append(txt("warn_leaky_gut"))
    if health_conditions.get('has_osteo') and any(x in name_lower for x in osteo_kw):
        warnings.append(txt("warn_osteo"))
    return warnings
