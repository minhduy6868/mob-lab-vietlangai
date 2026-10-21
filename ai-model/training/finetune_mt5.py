"""Fine-tune one mT5 model for ethnic <-> Vietnamese text.

The input prefix is `{source_lang} {target_lang}: {sentence}`.
Vietnamese <-> English stays on NLLB and is not trained here.
Run validate-only first:

    python training/finetune_mt5.py --train training/sample_vi_en.csv --dry-run
"""

import argparse
from pathlib import Path

from validate_pairs import validate_pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--base", default="google/mt5-small")
    parser.add_argument("--output", default="models/mt5-ethnic")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-unverified", action="store_true")
    args = parser.parse_args()
    summary = validate_pairs(args.train, allow_unverified=args.allow_unverified)
    print(summary)
    if args.dry_run:
        return
    from datasets import Dataset
    import csv
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        DataCollatorForSeq2Seq,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
    )

    records = []
    with args.train.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            records.append(
                {
                    "input": f"{row['source_lang'].strip()} {row['target_lang'].strip()}: {row['source'].strip()}",
                    "target": row["target"].strip(),
                }
            )
    tokenizer = AutoTokenizer.from_pretrained(args.base)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.base)

    def tokenize(batch: dict) -> dict:
        inputs = tokenizer(batch["input"], truncation=True, max_length=128)
        labels = tokenizer(batch["target"], truncation=True, max_length=128)
        inputs["labels"] = labels["input_ids"]
        return inputs

    dataset = Dataset.from_list(records).map(tokenize, batched=True, remove_columns=["input", "target"])
    trainer = Seq2SeqTrainer(
        model=model,
        args=Seq2SeqTrainingArguments(
            output_dir=args.output,
            num_train_epochs=args.epochs,
            per_device_train_batch_size=8,
            save_strategy="epoch",
            predict_with_generate=True,
        ),
        train_dataset=dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )
    trainer.train()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)


if __name__ == "__main__":
    main()
