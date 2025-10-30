import logging
import yaml
import os

def setup_logging(log_file, log_level):
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def load_config(path="config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing config file at {path}")
    with open(path, 'r') as fh:
        cfg = yaml.safe_load(fh)
    return cfg
