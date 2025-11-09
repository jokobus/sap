from pydantic import BaseModel, Field, AnyUrl

def to_serializable(obj):
        if isinstance(obj, BaseModel):
            return {k: to_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [to_serializable(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, AnyUrl):
            return str(obj)
        else:
            return obj