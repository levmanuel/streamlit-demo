import pandas as pd
import re

def extract_all_lines_and_percentages(text):
    # Pattern 1: Types de lignes spécifiques suivis de pourcentage
    pattern1 = r'((?:Credit line|Delivery line|FX line)).*?([0-9]+)%'
    
    # Pattern 2: Pourcentage suivi de texte puis ligne
    pattern2 = r'([0-9]+)%.*?((?:FX|Credit|Delivery)\s*line)'
    
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

def expand_dataframe_with_patterns(df, text_column):
    # Liste pour stocker toutes les nouvelles lignes
    new_rows = []
    
    # Pour chaque ligne du DataFrame original
    for idx, row in df.iterrows():
        text = row[text_column]
        patterns = extract_all_lines_and_percentages(text)
        
        if patterns:
            # Créer une nouvelle ligne pour chaque pattern trouvé
            for line_type, percentage in patterns:
                new_row = row.copy()  # Copier toutes les colonnes
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
    'id': [1, 2, 3],
    'description': [
        "Delivery line for CBIB of 100% \n Credit line of 5%",
        "Credit line of something else 5% with 50% of FX line",
        "Complex case with FX line 45% and 20% of Credit line"
    ]
})

# Appliquer la transformation
result_df = expand_dataframe_with_patterns(test_df, 'description')