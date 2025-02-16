import pandas as pd
import re

# Liste des types de lignes
list_limits = [
    'Delivery line',
    'Credit line',
    'FX line']

def build_patterns(limit_types):
    """
    Construit les patterns regex à partir de la liste des types de lignes.
    """
    # Échapper les espaces dans les types de lignes pour la regex
    escaped_types = [re.escape(t) for t in limit_types]
    
    # Joindre tous les types avec le OR (|)
    types_pattern = '|'.join(escaped_types)
    
    # Construire les deux patterns
    pattern1 = f'({types_pattern}).*?([0-9]+)%'
    pattern2 = f'([0-9]+)%.*?({types_pattern})'
    
    return pattern1, pattern2

def extract_all_lines_and_percentages(text, patterns):
    pattern1, pattern2 = patterns
    results = []
    remaining_text = text
    
    def find_and_remove_next_match(text, pattern):
        match = re.search(pattern, text)
        if match:
            start, end = match.span()
            new_text = text[:start] + text[end:]
            return match, new_text
        return None, text

    while remaining_text:
        match1, new_text1 = find_and_remove_next_match(remaining_text, pattern1)
        match2, new_text2 = find_and_remove_next_match(remaining_text, pattern2)
        
        if match1 and match2:
            if match1.start() <= match2.start():
                remaining_text = new_text1
                results.append((match1.group(1).strip(), f"{match1.group(2)}%"))
            else:
                remaining_text = new_text2
                results.append((match2.group(2).strip(), f"{match2.group(1)}%"))
        elif match1:
            remaining_text = new_text1
            results.append((match1.group(1).strip(), f"{match1.group(2)}%"))
        elif match2:
            remaining_text = new_text2
            results.append((match2.group(2).strip(), f"{match2.group(1)}%"))
        else:
            break
            
    return results

def expand_dataframe_with_patterns(df, text_column, limit_types):
    # Construire les patterns une seule fois
    patterns = build_patterns(limit_types)
    
    # Liste pour stocker toutes les nouvelles lignes
    new_rows = []
    
    # Pour chaque ligne du DataFrame original
    for idx, row in df.iterrows():
        text = row[text_column]
        matches = extract_all_lines_and_percentages(text, patterns)
        
        if matches:
            # Créer une nouvelle ligne pour chaque pattern trouvé
            for line_type, percentage in matches:
                new_row = row.copy()
                new_row['line_type'] = line_type
                new_row['percentage'] = percentage
                new_rows.append(new_row)
        else:
            # Si aucun pattern n'est trouvé, garder la ligne avec des valeurs null
            new_row = row.copy()
            new_row['line_type'] = None
            new_row['percentage'] = None
            new_rows.append(new_row)
    
    # Créer un nouveau DataFrame avec toutes les nouvelles lignes
    result_df = pd.DataFrame(new_rows)
    
    # Réorganiser les colonnes pour plus de clarté
    cols = ['line_type', 'percentage'] + \
           [col for col in result_df.columns if col not in ['line_type', 'percentage']]
    result_df = result_df[cols]
    
    return result_df

# Test avec un exemple de DataFrame
test_df = pd.DataFrame({
    'description': [
        "Delivery line for CBIB of 100% and Credit line of 5%",
        "Credit line of something else 5% with 50% of FX line",
        "Complex case with FX line 45% and 20% of Credit line"
    ]
})

# Appliquer la transformation avec la liste des types
result_df = expand_dataframe_with_patterns(test_df, 'description', list_limits).reset_index(drop=True)