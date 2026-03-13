import os
import json
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split

def make_splits(df, strategy="stratified", seed=42, target_col="target"):
    """
    Розділяє датафрейм на train/val/test.
    """
    if strategy == "stratified":
        train_df, temp_df = train_test_split(
            df, 
            test_size=0.20, 
            random_state=seed, 
            stratify=df[target_col]
        )
        
        val_df, test_df = train_test_split(
            temp_df, 
            test_size=0.50, 
            random_state=seed, 
            stratify=temp_df[target_col]
        )
    else:
        raise ValueError(f"Стратегія '{strategy}' наразі не підтримується.")

    manifest_info = {
        "seed": seed,
        "strategy": strategy,
        "target_column_for_stratification": target_col,
        "split_sizes": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df),
            "total": len(df)
        },
        "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "manifest_info": manifest_info
    }

def save_splits(splits, data_out_dir="sentiment/data/sample", docs_out_dir="sentiment/docs", id_col=None):
    """
    Зберігає ID записів у .txt файли та генерує JSON маніфест.
    """
    os.makedirs(data_out_dir, exist_ok=True)
    os.makedirs(docs_out_dir, exist_ok=True)

    def save_ids(df, filename):
        filepath = os.path.join(data_out_dir, filename)
        ids_to_save = df[id_col] if id_col in df.columns else df.index
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for item_id in ids_to_save:
                f.write(f"{item_id}\n")

    save_ids(splits["train"], "splits_train_ids.txt")
    save_ids(splits["val"], "splits_val_ids.txt")
    save_ids(splits["test"], "splits_test_ids.txt")

    manifest_path = os.path.join(docs_out_dir, "splits_manifest_lab5.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(splits["manifest_info"], f, indent=4, ensure_ascii=False)

    print(f"ID сплітів збережено у папку: {data_out_dir}/")
    print(f"Маніфест збережено: {manifest_path}")