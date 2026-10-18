"""Generate saved explanations on this machine (CPU).

Run from the repo root:
  python scripts/make_saved_model.py --limit 12       # test run, writes *_test.json files
  python scripts/make_saved_model.py                  # full run (all products)
  python scripts/make_saved_model.py --template-only  # no model, fixed factual templates
"""
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
CPU_NAME = os.environ.get("CPU_NAME", "AMD Ryzen 7 7735HS with Radeon Graphics")
FORBIDDEN = ["customer", "sale", "revenue", "prevent", "avoid", "lost", "christmas",
             "holiday", "trend", "season", "supplier", "delay", "expected", "likely",
             "because", "ensure", "help", "risk", "shortage", "stockout", "sufficient",
             "enough", "should", "will", "would", "could", "may", "might", "so that",
             "in order", "recommend"]


def load_actions():
    data = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))
    return data["actions"] if isinstance(data, dict) and "actions" in data else data


def numbers_in(text):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))]


def facts(a):
    buffer = float(a.get("buffer", 1.2))
    forecast = float(a["forecast"])
    stock = float(a["stock"])
    target = round(buffer * forecast, 2)
    return {
        "description": str(a["description"]),
        "forecast": round(forecast, 2),
        "buffer": buffer,
        "target": target,
        "stock": round(stock, 2),
        "shortfall": round(max(0.0, target - stock), 2),
        "quantity": int(a["quantity"]),
        "action": a["action"],
    }


def template(f):
    base = (f"Forecast demand for {f['description']} next week is {f['forecast']} units. "
            f"The target stock with a {f['buffer']} buffer is {f['target']} units; "
            f"simulated stock is {f['stock']}.")
    if f["action"] == "reorder":
        return base + f" Suggested order: {f['quantity']} units."
    return base + " Simulated stock already meets the target, so hold."


def build_prompt(f):
    return (
        "Write exactly 3 short plain sentences for a shop buyer using only these numbers. "
        "State the forecast, the target stock, the simulated stock and the suggested order. "
        "Do not mention customers, sales, revenue, lost sales, trends, seasons, suppliers, "
        "or any outcome. Do not give reasons beyond the numbers.\n"
        f"Product: {f['description']}\n"
        f"Forecast demand next week: {f['forecast']} units\n"
        f"Target stock ({f['buffer']} x forecast): {f['target']} units\n"
        f"Simulated stock: {f['stock']} units\n"
        f"Shortfall: {f['shortfall']} units\n"
        f"Suggested order: {f['quantity']} units"
    )


SYSTEM = ("You write short factual notes for a shop buyer. Use only the numbers given. "
          "Write exactly 3 sentences in the same style as the examples. Add nothing else.")

EX_REORDER = {"description": "EXAMPLE MUG", "forecast": 100.0, "buffer": 1.2, "target": 120.0,
              "stock": 40.0, "shortfall": 80.0, "quantity": 80, "action": "reorder"}
EX_HOLD = {"description": "EXAMPLE MUG", "forecast": 50.0, "buffer": 1.2, "target": 60.0,
           "stock": 75.0, "shortfall": 0.0, "quantity": 0, "action": "hold"}
FEWSHOT = [
    {"role": "user", "content": build_prompt(EX_REORDER)},
    {"role": "assistant", "content": "The forecast for EXAMPLE MUG next week is 100.0 units. The target stock with a 1.2 buffer is 120.0 units, and simulated stock is 40.0 units. The suggested order is 80 units."},
    {"role": "user", "content": build_prompt(EX_HOLD)},
    {"role": "assistant", "content": "The forecast for EXAMPLE MUG next week is 50.0 units. The target stock with a 1.2 buffer is 60.0 units, and simulated stock is 75.0 units. The suggested order is 0 units."},
]


def sentences(text):
    t = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if p.strip()]


def passes(text, f):
    t = " ".join(text.split())
    if not t.endswith("."):
        return False, "truncated"
    sents = sentences(t)
    if len(sents) != 3:
        return False, "sentence_count"
    if len(t.split()) > 70:
        return False, "too_long"
    if f["description"].lower() not in t.lower():
        return False, "description"
    desc = re.escape(f["description"])
    scrubbed = re.sub(desc, "", t, flags=re.I)
    low = scrubbed.lower()
    if any(re.search(r"\b" + re.escape(w), low) for w in FORBIDDEN):
        return False, "forbidden"
    allowed = [f["forecast"], f["target"], f["stock"], f["shortfall"],
               f["quantity"], f["buffer"]]
    found = numbers_in(scrubbed)
    for n in found:
        if not any(abs(n - a) <= 0.5 for a in allowed):
            return False, "number"
    if not any(abs(n - f["forecast"]) <= 0.5 for n in found):
        return False, "missing_forecast"
    if f["action"] == "reorder" and not any(abs(n - f["quantity"]) <= 0.5 for n in found):
        return False, "missing_quantity"
    for s in sents:
        s_clean = re.sub(desc, "", s, flags=re.I)
        if not any(abs(n - a) <= 0.5 for n in numbers_in(s_clean) for a in allowed):
            return False, "sentence_without_number"
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--template-only", action="store_true")
    args = ap.parse_args()

    actions = load_actions()
    if args.limit:
        actions = actions[: args.limit]

    torch = tok = model = None
    if not args.template_only:
        import torch as _torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch = _torch
        tok = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, torch_dtype=torch.float32).to("cpu").eval()

    out, secs, toks, rejects, samples = {}, [], [], {}, []
    saved = tmpl = 0
    for a in actions:
        f = facts(a)
        why = ""
        if model is None:
            txt, src = template(f), "template"
            tmpl += 1
        else:
            messages = [{"role": "system", "content": SYSTEM}] + FEWSHOT + \
                       [{"role": "user", "content": build_prompt(f)}]
            text_in = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tok(text_in, return_tensors="pt")
            t0 = time.perf_counter()
            with torch.no_grad():
                gen = model.generate(**inputs, do_sample=False, max_new_tokens=90)
            dt = time.perf_counter() - t0
            new = gen[0][inputs["input_ids"].shape[1]:]
            reply = tok.decode(new, skip_special_tokens=True).strip()
            secs.append(dt)
            toks.append(int(new.shape[0]))
            ok, why = passes(reply, f)
            if ok:
                txt, src = reply, "saved"
                saved += 1
            else:
                txt, src = template(f), "template"
                tmpl += 1
                rejects[why] = rejects.get(why, 0) + 1
                if len(samples) < 5:
                    samples.append({"sku": str(a["sku"]), "reason": why, "model_reply": reply[:300]})
        out[str(a["sku"])] = {"text": txt, "source": src}
        print(f"{a['sku']}: {src} {why}\n    {txt}")

    suffix = "_test" if args.limit else ""
    (ROOT / f"data/saved_explanations{suffix}.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    meta = {
        "generation_method": "rule-based template, no language model" if model is None
                             else "open language model run locally on the CPU",
        "model_id": None if model is None else MODEL_ID,
        "model_source": None if model is None else "Hugging Face Hub (downloaded once, then cached)",
        "torch_version": None if model is None else torch.__version__,
        "cuda_available": None if model is None else bool(torch.cuda.is_available()),
        "device": "cpu",
        "cpu_name": CPU_NAME,
        "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE", "unset"),
        "count": len(out),
        "saved_count": saved,
        "template_count": tmpl,
        "rejection_reasons": rejects,
        "rejected_examples": samples,
        "avg_seconds_per_explanation": round(sum(secs) / len(secs), 2) if secs else 0,
        "avg_new_tokens": round(sum(toks) / len(toks), 1) if toks else 0,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ROOT / f"eval/amd_generation{suffix}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()