from sentence_transformers import losses
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

class Trainer:
    def __init__(
        self,
        epochs: int = 5,
        batch_size: int = 32,
        learning_rate: float = 1e-5,
        warmup_steps: int = 100,
    ):
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.warmup_steps = warmup_steps
    
    def train(
        self, model, train_dataset, output_path: str,
    ):        
        print(f"\n📊 Подготовка данных...")
        print(f"   - Примеров: {len(train_dataset):,}")
        print(f"   - Batch size: {self.batch_size}")
        print(f"   - Epochs: {self.epochs}")
                
        train_loss = losses.MultipleNegativesRankingLoss(model)
        
        print(f"\n🔥 Запуск обучения...")
                
        training_args = SentenceTransformerTrainingArguments(
            output_dir=output_path,
            num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=2,
            learning_rate=self.learning_rate,
            warmup_steps=self.warmup_steps,
            save_strategy="epoch",
            logging_steps=10,
            save_total_limit=2,
        )
        
        trainer = SentenceTransformerTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            loss=train_loss,
        )
        
        trainer.train()
        model.save(output_path, safe_serialization=False)
        
        print(f"✅ Обучение завершено!")
        print(f"📁 Модель сохранена в: {output_path}")
