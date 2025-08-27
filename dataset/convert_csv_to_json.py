#!/usr/bin/env python3
"""
Convert the CSV dataset to JSON format for evaluation.
"""
import csv
import json
import sys

def convert_csv_to_json(csv_path='datasetQ1.csv', json_path='Q1-dataset.json'):
    """Convert CSV dataset to JSON format."""
    dataset = []
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Skip empty rows or rows without proper data
            if not row.get('Original Query ') or not row.get('Target Text'):
                continue
            
            # Only include Type 1 queries
            if row.get('Query Type') != '1':
                continue
                
            # Create the JSON entry
            entry = {
                "inputs": {
                    "question": row['Original Query '].strip()
                },
                "outputs": {
                    "answer": row['Target Text'].strip() + (f"\n\n{row['Source']}" if row.get('Source') else "")
                }
            }
            dataset.append(entry)
    
    # Save to JSON file
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(dataset, jsonfile, ensure_ascii=False, indent=4)
    
    print(f"Converted {len(dataset)} entries from CSV to JSON")
    print(f"Saved to: {json_path}")
    
    return dataset

if __name__ == "__main__":
    convert_csv_to_json()
