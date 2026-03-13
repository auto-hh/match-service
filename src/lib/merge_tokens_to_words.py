# src/lib/token_parser.py
import numpy as np
import string
from typing import Dict, List

# Знаки препинания для фильтрации (русские + английские)
PUNCTUATION = set(string.punctuation) | set('«»„"„""—–…')


def merge_tokens_to_words(
    tokens: List[str],
    weights: np.ndarray,
    tokenizer_type: str = "auto",
) -> Dict[str, float]:
    """
    Объединяет субтокены в слова + фильтрует пунктуацию.
    """
    if len(tokens) != len(weights):
        raise ValueError(f"Длина tokens != длины weights")
    
    if tokenizer_type == "auto":
        tokenizer_type = _detect_tokenizer_type(tokens)
    
    cls_weight = 0.0
    content_tokens = []
    content_weights = []
    
    for token, weight in zip(tokens, weights):
        if _is_special_token(token, tokenizer_type):
            if _is_cls_token(token, tokenizer_type):
                cls_weight = weight
            continue
        
        if _is_punctuation(token):
            continue
        
        content_tokens.append(token)
        content_weights.append(weight)
    
    if cls_weight > 0 and len(content_weights) > 0:
        content_weights = _redistribute_cls_weight(content_weights, cls_weight)
    
    # Объединяем субтокены в слова
    if tokenizer_type == "bert":
        return _merge_bert_tokens(content_tokens, np.array(content_weights))
    elif tokenizer_type == "roberta":
        return _merge_roberta_tokens(content_tokens, np.array(content_weights))
    elif tokenizer_type == "sentencepiece":
        return _merge_sentencepiece_tokens(content_tokens, np.array(content_weights))
    else:
        return {token: float(weight) for token, weight in zip(content_tokens, content_weights)}

def _detect_tokenizer_type(tokens: List[str]) -> str:
    """Определяет тип токенизатора по структуре токенов"""
    for token in tokens[:10]:  # Проверяем первые 10 токенов
        if token.startswith("##"):
            return "bert"  # WordPiece: ##prefix
        elif token.startswith("▁"):
            return "sentencepiece"  # SentencePiece/BPE: ▁prefix
        elif token.startswith("Ġ"):
            return "roberta"  # RoBERTa: Ġprefix (gpt2 style)
    return "unknown"

def _is_punctuation(token: str) -> bool:
    """
    Проверка токена на пунктуацию.
    Учитывает, что токен может быть склеенным (например, "Developer,")
    """
    # Если токен полностью состоит из знаков препинания
    if all(c in PUNCTUATION for c in token):
        return True
    
    # Если токен начинается или заканчивается на пунктуацию (для слитных случаев)
    if token and (token[0] in PUNCTUATION or token[-1] in PUNCTUATION):
        # Но не фильтруем слова вроде "C++" или "C#"
        if token.isalpha():
            return False
        # Если только один символ и это пунктуация
        if len(token) == 1 and token in PUNCTUATION:
            return True
    
    return False


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


def _merge_bert_tokens(tokens: List[str], weights: np.ndarray) -> Dict[str, float]:
    """BERT WordPiece: ## означает продолжение слова"""
    word_weights = {}
    current_word_parts = []
    current_weight_parts = []
    
    for token, weight in zip(tokens, weights):
        if token.startswith("##"):
            current_word_parts.append(token[2:])
            current_weight_parts.append(weight)
        else:
            if current_word_parts:
                word = "".join(current_word_parts)
                avg_weight = float(np.mean(current_weight_parts))
                word_weights[word] = avg_weight
            current_word_parts = [token]
            current_weight_parts = [weight]
    
    if current_word_parts:
        word = "".join(current_word_parts)
        avg_weight = float(np.mean(current_weight_parts))
        word_weights[word] = avg_weight
    
    return word_weights


def _merge_roberta_tokens(tokens: List[str], weights: np.ndarray) -> Dict[str, float]:
    """RoBERTa/GPT-2: Ġ означает начало нового слова"""
    word_weights = {}
    
    for token, weight in zip(tokens, weights):
        if token.startswith("Ġ"):
            word = token[1:]
        else:
            word = token
        word_weights[word] = float(weight)
    
    return word_weights


def _merge_sentencepiece_tokens(tokens: List[str], weights: np.ndarray) -> Dict[str, float]:
    """SentencePiece: ▁ означает начало нового слова"""
    word_weights = {}
    current_word_parts = []
    current_weight_parts = []
    
    for token, weight in zip(tokens, weights):
        if token.startswith("▁"):
            if current_word_parts:
                word = "".join(current_word_parts)
                avg_weight = float(np.mean(current_weight_parts))
                word_weights[word] = avg_weight
            current_word_parts = [token[1:]]
            current_weight_parts = [weight]
        else:
            current_word_parts.append(token)
            current_weight_parts.append(weight)
    
    if current_word_parts:
        word = "".join(current_word_parts)
        avg_weight = float(np.mean(current_weight_parts))
        word_weights[word] = avg_weight
    
    return word_weights