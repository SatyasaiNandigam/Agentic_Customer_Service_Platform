import sys, json
sys.path.insert(0, ".")
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
path = "eval/datasets/memory.jsonl"
for line in open(path, encoding="utf-8"):
    obj = json.loads(line.strip())
    cat = obj["category"]
    if cat == "below_threshold":
        continue
    es = obj.get("existing_summary") or ""
    es_toks = len(enc.encode(es))
    smc = obj["summarized_message_count"]
    msgs = obj["messages"]
    # safe_horizon walk-back
    sh = len(msgs) - 1
    while sh > smc and msgs[sh]["role"] == "tool":
        sh -= 1
    new_msgs = msgs[smc:sh]
    msg_toks = sum(len(enc.encode(m["content"])) for m in new_msgs)
    true_input = es_toks + msg_toks
    print(f"{obj['id']} [{cat}]: existing_summary={es_toks}tok  new_msgs={msg_toks}tok  true_input={true_input}tok  n_new_msgs={len(new_msgs)}")
