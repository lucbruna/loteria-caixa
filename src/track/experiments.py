import json
from pathlib import Path
from datetime import datetime
import uuid


def log_exp(metrics: dict, cfg: dict, out_dir: Path = Path('reports')):
    out_dir.mkdir(exist_ok=True)
    rec = {
        'id': str(uuid.uuid4()),
        'ts': datetime.now().isoformat(),
        'metrics': metrics,
        'cfg': cfg,
    }
    with open(out_dir/'experiments.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False)+'\n')
    return rec


if __name__=='__main__':
    log_exp({'p':0.00017}, {'model':'freq_top10'})
    print('ok')
