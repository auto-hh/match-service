import numpy as np
import string
from typing import List
from schemas import Token

PUNCTUATION = set(string.punctuation) | set('«»„"„""—–…')


def merge_tokens_to_words(
    tokens: List[str],
    weights: np.ndarray,
    tokenizer_type: str = "auto",
) -> List[Token]:  # ← Возвращаем список Token, а не dict
    """
    Объединяет субтокены в слова + сохраняет пробелы/знаки с весом 0.0.
    """
    if len(tokens) != len(weights):
        raise ValueError(f"Длина tokens != длины weights")
    
    if tokenizer_type == "auto":
        tokenizer_type = _detect_tokenizer_type(tokens)
    
    # Разделяем CLS и обычные токены
    cls_weight = 0.0
    content_tokens = []
    content_weights = []
    content_indices = []  # Сохраняем индексы для маппинга
    
    for i, (token, weight) in enumerate(zip(tokens, weights)):
        if _is_special_token(token, tokenizer_type):
            if _is_cls_token(token, tokenizer_type):
                cls_weight = weight
            continue
        
        content_tokens.append(token)
        content_weights.append(weight)
        content_indices.append(i)
    
    # Распределяем вес CLS
    if cls_weight > 0 and len(content_weights) > 0:
        content_weights = _redistribute_cls_weight(content_weights, cls_weight)
    
    # Объединяем субтокены в слова + сохраняем структуру
    result_tokens = _merge_with_structure(
        content_tokens, 
        np.array(content_weights), 
        tokenizer_type
    )
    
    # Нормализация весов к 0.0–1.0
    result_tokens = _normalize_weights(result_tokens)
    
    return result_tokens


def _merge_with_structure(
    tokens: List[str],
    weights: np.ndarray,
    tokenizer_type: str
) -> List[Token]:
    """
    Объединяет субтокены, сохраняя пробелы и знаки препинания как отдельные токены.
    """
    result = []
    
    if tokenizer_type == "bert":
        result = _merge_bert_with_structure(tokens, weights)
    elif tokenizer_type == "roberta":
        result = _merge_roberta_with_structure(tokens, weights)
    elif tokenizer_type == "sentencepiece":
        result = _merge_sentencepiece_with_structure(tokens, weights)
    else:
        result = [
            Token(
                text=token,
                weight=float(weight),
                is_word=_is_meaningful_token(token)
            )
            for token, weight in zip(tokens, weights)
        ]
    
    return result


def _merge_bert_with_structure(tokens: List[str], weights: np.ndarray) -> List[Token]:
    """
    BERT WordPiece: ## означает продолжение слова.
    Склеивает токены в полные слова (back + ##end → backend).
    """
    result = []
    
    # Буфер для текущего слова
    current_word_parts = []
    current_weight_parts = []
    
    for token, weight in zip(tokens, weights):
        # 1. Если токен продолжает слово (начинается с ##)
        if token.startswith("##"):
            current_word_parts.append(token[2:])  # Убираем ##
            current_weight_parts.append(float(weight))
        
        # 2. Если токен начинает новое слово
        else:
            # Сначала сохраняем предыдущее слово (если буфер не пуст)
            if current_word_parts:
                word = "".join(current_word_parts)
                avg_weight = float(np.mean(current_weight_parts))
                is_word = _is_meaningful_token(word)
                result.append(Token(text=word, weight=avg_weight, is_word=is_word))
            
            # Начинаем новый буфер
            current_word_parts = [token]
            current_weight_parts = [float(weight)]
    
    # 3. В конце цикла сохраняем последнее слово из буфера
    if current_word_parts:
        word = "".join(current_word_parts)
        avg_weight = float(np.mean(current_weight_parts))
        is_word = _is_meaningful_token(word)
        result.append(Token(text=word, weight=avg_weight, is_word=is_word))
    
    return result


def _merge_roberta_with_structure(tokens: List[str], weights: np.ndarray) -> List[Token]:
    """RoBERTa: Ġ начало слова"""
    result = []
    current_word_parts = []
    current_weight_parts = []
    
    for token, weight in zip(tokens, weights):
        if token.startswith("Ġ"):
            # Сохраняем предыдущее слово
            if current_word_parts:
                word = "".join(current_word_parts)
                avg_weight = float(np.mean(current_weight_parts))
                result.append(Token(text=word, weight=avg_weight, is_word=True))
            
            # Новый токен
            word = token[1:]
            is_word = _is_meaningful_token(word)
            result.append(Token(text=word, weight=float(weight), is_word=is_word))
            
            current_word_parts = []
            current_weight_parts = []
        else:
            current_word_parts.append(token)
            current_weight_parts.append(weight)
    
    if current_word_parts:
        word = "".join(current_word_parts)
        avg_weight = float(np.mean(current_weight_parts))
        result.append(Token(text=word, weight=avg_weight, is_word=True))
    
    return result


def _merge_sentencepiece_with_structure(tokens: List[str], weights: np.ndarray) -> List[Token]:
    """SentencePiece: ▁ начало слова"""
    result = []
    current_word_parts = []
    current_weight_parts = []
    
    for token, weight in zip(tokens, weights):
        if token.startswith("▁"):
            if current_word_parts:
                word = "".join(current_word_parts)
                avg_weight = float(np.mean(current_weight_parts))
                result.append(Token(text=word, weight=avg_weight, is_word=True))
            
            word = token[1:]
            is_word = _is_meaningful_token(word)
            result.append(Token(text=word, weight=float(weight), is_word=is_word))
            
            current_word_parts = []
            current_weight_parts = []
        else:
            current_word_parts.append(token)
            current_weight_parts.append(weight)
    
    if current_word_parts:
        word = "".join(current_word_parts)
        avg_weight = float(np.mean(current_weight_parts))
        result.append(Token(text=word, weight=avg_weight, is_word=True))
    
    return result


def _is_meaningful_token(token: str) -> bool:
    """Проверка: является ли токен смысловым (не пробел/знак)"""
    if not token:
        return False
    if token.isspace():
        return False
    if all(c in PUNCTUATION for c in token):
        return False
    return True


def _normalize_weights(tokens: List[Token]) -> List[Token]:
    """Нормализация весов к диапазону 0.0–1.0 (макс = 1.0)"""
    word_weights = [t.weight for t in tokens if t.is_word]
    
    if not word_weights:
        return tokens
    
    max_weight = max(word_weights)
    
    result = []
    for token in tokens:
        if token.is_word and max_weight > 0:
            normalized_weight = token.weight / max_weight
        else:
            normalized_weight = 0.0
        
        result.append(Token(
            text=token.text,
            weight=normalized_weight,
            is_word=token.is_word
        ))
    
    return result


def _redistribute_cls_weight(weights: List[float], cls_weight: float) -> List[float]:
    """Распределяет вес CLS пропорционально между токенами"""
    if not weights:
        return weights
    
    weights = np.array(weights, dtype=float)
    total = np.sum(weights)
    
    if total > 0:
        distribution = (weights / total) * cls_weight
        weights = weights + distribution
    
    return weights.tolist()


def _detect_tokenizer_type(tokens: List[str]) -> str:
    """Определяет тип токенизатора"""
    for token in tokens[:10]:
        if token.startswith("##"):
            return "bert"
        elif token.startswith("▁"):
            return "sentencepiece"
        elif token.startswith("Ġ"):
            return "roberta"
    return "bert"


def _is_special_token(token: str, tokenizer_type: str) -> bool:
    """Проверка на специальный токен токенизатора"""
    special_tokens = {
        "bert": {"[CLS]", "[SEP]", "[PAD]", "[MASK]"},
        "roberta": {"<s>", "</s>", "<pad>", "<mask>"},
        "sentencepiece": {"<s>", "</s>", "<pad>"},
    }
    return token in special_tokens.get(tokenizer_type, set())


def _is_cls_token(token: str, tokenizer_type: str) -> bool:
    """Проверка, является ли токен CLS"""
    cls_tokens = {
        "bert": "[CLS]",
        "roberta": "<s>",
        "sentencepiece": "<s>",
    }
    return token == cls_tokens.get(tokenizer_type, "")