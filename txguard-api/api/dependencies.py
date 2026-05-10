from functools import lru_cache
from .config import settings
from ml.scorer import HybridScorer
from ml.explainer import SHAPExplainer

@lru_cache()
def get_scorer():
    return HybridScorer(model_dir=settings.MODEL_DIR)

@lru_cache()
def get_explainer():
    scorer = get_scorer()
    return SHAPExplainer(model=scorer.iso_forest)

def get_db():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
