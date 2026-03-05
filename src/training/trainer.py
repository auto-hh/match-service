from sentence_transformers import losses
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer
from pathlib import Path
import shutil

class Trainer:
    def __init__(
        self,
        epochs: int = 5,
        batch_size: int = 32,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        use_lora: bool = True,
    ):
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.warmup_steps = warmup_steps
        self.use_lora = use_lora
    
    def train(
        self, model, train_dataset, output_path: str,
    ):        
        print(f"\nПодготовка данных...")
        print(f"   - Примеров: {len(train_dataset):,}")
        print(f"   - Batch size: {self.batch_size}")
        print(f"   - Epochs: {self.epochs}")
        print(f"   - LoRA enabled: {self.use_lora}")
                
        train_loss = losses.MultipleNegativesRankingLoss(model)
        
        print(f"\nЗапуск обучения...")
                
        training_args = SentenceTransformerTrainingArguments(
            output_dir=output_path,
            num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=2,
            learning_rate=self.learning_rate,
            warmup_steps=self.warmup_steps,
            save_strategy="epoch",
            logging_steps=10,
            save_total_limit=1,
        )
        
        trainer = SentenceTransformerTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            loss=train_loss,
        )
        
        trainer.train()

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        if self.use_lora:
            adapter_path = output_path / "adapter"
            adapter_path.mkdir(parents=True, exist_ok=True)
            model[0].auto_model.save_pretrained(adapter_path)
            print(f"Адаптеры LoRA сохранены в: {adapter_path}")
