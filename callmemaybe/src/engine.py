from src import Small_LLM_Model
from pydantic import ValidationError
from models import PromptTest, FunctionDefinition, Parameter
import json


class GenerationEngine:
    def __init__(self, model: Small_LLM_Model):
        self.model = model
        vocab_path = self.model.get_path_to_vocab_file()

        try:
            with open(vocab_path, "r", encoding="utf-8") as f:
                self.vocab = json.load(f)
                self.id_to_token = {v: k for k, v in self.vocab.items()}

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
    
    def get_mask_for_current(self, current_token_ids):
        
