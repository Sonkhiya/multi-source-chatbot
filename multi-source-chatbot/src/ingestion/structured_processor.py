import json
from typing import Any, Dict


class StructuredDataProcessor:
    @staticmethod
    def validate_and_flatten(data: Dict[str, Any], context: str = "") -> str:
        try:
            flattened = StructuredDataProcessor._flatten_dict(data)
            formatted = json.dumps(flattened, indent=2, default=str)
            
            if context:
                formatted = f"Context: {context}\n\n{formatted}"
            
            return formatted
        except Exception as e:
            raise ValueError(f"Error processing structured data: {e}")
    
    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(StructuredDataProcessor._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, default=str)))
            else:
                items.append((new_key, v))
        return dict(items)
