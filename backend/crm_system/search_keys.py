import os
for k, v in os.environ.items():
    if "KEY" in k or "OPENAI" in k:
        print(f"{k}: {v[:5]}...")
