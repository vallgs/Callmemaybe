from src.llm_sdk.llm_sdk import Small_LLM_Model
from pydantic import ValidationError
from .models import FunctionDefinition
from .util import is_valide
import json


class GenerationEngine:
    def __init__(self, model: Small_LLM_Model,
                 function: list[FunctionDefinition]):
        self.model = model
        vocab_path = self.model.get_path_to_vocab_file()
        self.functions = function

        try:
            with open(vocab_path, "r", encoding="utf-8") as f:
                self.vocab = json.load(f)
                self.id_to_token = {v: k for k, v in self.vocab.items()}
                self.decoded_tokens = {tid: self.model.decode([tid])
                                       for tid in self.id_to_token}

        except OSError as e:
            print(f"{e}")
        except ValidationError as e:
            print(f"{e}")

    def generate_step(self, current_token_ids: list[int]) -> int:
        logits = self.model.get_logits_from_input_ids(current_token_ids)

        valid_mask = self.get_mask_for_current_states(current_token_ids)

        constrained_logits = self.apply_mask(logits, valid_mask)

        next_token_id = self.selected_best_token(constrained_logits)

        return next_token_id

    def get_mask_for_current_states(
            self, current_token_ids: list[int]
            ) -> list[float]:
        current_token = self.model.decode(current_token_ids)
        mask = []
        for token_id in self.id_to_token:
            decoded = self.decoded_tokens[token_id]
            if is_valide(current_token, decoded, self.functions):
                mask.append(0.0)
            else:
                mask.append(float('-inf'))
        return mask

    def apply_mask(self, logits: list[float],
                   mask: list[float]) -> list[float]:
        return [logit + mask_value for logit, mask_value in zip(logits, mask)]

    def selected_best_token(self, constrained_logits: list[float]) -> int:
        return constrained_logits.index(max(constrained_logits))
