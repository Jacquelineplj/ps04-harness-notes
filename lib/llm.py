#!/usr/bin/env python3
"""Model-provider wrapper used by the editorial and content components.

One entry point, three providers:
  claude-cli  (default) Claude Code CLI in headless mode. No API key needed; it
              uses the operator's Claude login. Cost comes from the CLI's own
              `total_cost_usd` and is recorded as an estimate (list-price basis).
  anthropic   Official `anthropic` SDK; needs ANTHROPIC_API_KEY. Cost is computed
              from the price table in config/models.json.
  openai      Official `openai` SDK; needs OPENAI_API_KEY. Cost is computed from
              the price table when the model is listed, otherwise unknown (null).

Credentials are read from environment variables only and never logged.
Every call appends one usage line (no prompt text) to RUN_DIR/logs/llm_calls.jsonl.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROVIDERS = ("claude-cli", "anthropic", "openai")


class LLMError(RuntimeError):
    pass


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_model_config(run_dir: str | None = None) -> dict:
    """Prefer the run snapshot (RUN_DIR/config/models.json), else config/models.json."""
    candidates = []
    if run_dir:
        candidates.append(os.path.join(run_dir, "config", "models.json"))
    candidates.append(os.path.join(ROOT, "config", "models.json"))
    for p in candidates:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
    return {"default_provider": "claude-cli", "stages": {}, "prices_per_mtok": {}}


def stage_settings(stage: str, run_dir: str | None = None) -> dict:
    cfg = load_model_config(run_dir)
    st = dict(cfg.get("stages", {}).get(stage, {}))
    provider = os.environ.get("LLM_PROVIDER") or st.get("provider") or cfg.get("default_provider", "claude-cli")
    if provider not in PROVIDERS:
        raise LLMError(f"unknown LLM provider {provider!r}; expected one of {PROVIDERS}")
    model = os.environ.get("LLM_MODEL") or st.get("model") or "claude-opus-5"
    if provider == "openai" and not os.environ.get("LLM_MODEL"):
        model = st.get("openai_model") or cfg.get("openai_default_model") or "gpt-5"
    return {
        "provider": provider,
        "model": model,
        "max_tokens": int(st.get("max_tokens", 16000)),
        "prices": cfg.get("prices_per_mtok", {}),
        "max_budget_usd": float(cfg.get("max_budget_usd_per_call", 20.0)),
    }


def _price(prices: dict, model: str, input_tokens: int, output_tokens: int):
    p = prices.get(model)
    if not p:
        return None
    return round(input_tokens / 1e6 * float(p["input"]) + output_tokens / 1e6 * float(p["output"]), 6)


def _log_call(run_dir, record: dict):
    if not run_dir:
        return
    os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
    with open(os.path.join(run_dir, "logs", "llm_calls.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _extract_json(text: str):
    text = (text or "").strip()
    if not text:
        raise LLMError("empty model response")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if text.startswith("```"):
        inner = text.split("```", 2)
        if len(inner) >= 2:
            body = inner[1]
            if body.startswith("json"):
                body = body[4:]
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])
    raise LLMError("model response is not JSON")


# ----------------------------------------------------------------------------- providers

def _call_claude_cli(system, user, schema, model, max_tokens, settings, timeout):
    exe = shutil.which("claude")
    if not exe:
        raise LLMError("claude CLI not found on PATH (install Claude Code or set LLM_PROVIDER)")
    cmd = [exe, "-p", "--no-session-persistence", "--output-format", "json",
           "--model", model, "--tools", "", "--max-turns", "6",
           "--max-budget-usd", str(settings.get("max_budget_usd", 20.0))]
    if system:
        cmd += ["--system-prompt", system]
    if schema is not None:
        cmd += ["--json-schema", json.dumps(schema)]
    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_CHILD_SESSION"):
        env.pop(k, None)
    proc = subprocess.run(cmd, input=user, capture_output=True, text=True, timeout=timeout, env=env, cwd=ROOT)
    if proc.returncode != 0 and not proc.stdout.strip():
        raise LLMError(f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:500]}")
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise LLMError(f"claude CLI returned non-JSON output: {proc.stdout[:300]!r} stderr={proc.stderr[:300]!r}")
    if out.get("is_error") or out.get("subtype") not in (None, "success"):
        raise LLMError(f"claude CLI error: subtype={out.get('subtype')} result={str(out.get('result'))[:300]}")
    text = out.get("result") or ""
    data = out.get("structured_output") if schema is not None else None
    if schema is not None and data is None:
        data = _extract_json(text)
    usage_in = usage_out = 0
    models_used = []
    for name, mu in (out.get("modelUsage") or {}).items():
        models_used.append(mu.get("canonicalModel") or name)
        usage_in += int(mu.get("inputTokens") or 0) + int(mu.get("cacheReadInputTokens") or 0) + int(mu.get("cacheCreationInputTokens") or 0)
        usage_out += int(mu.get("outputTokens") or 0)
    usage = {
        "provider": "claude-cli",
        "model": ",".join(sorted(set(models_used))) or model,
        "input_tokens": usage_in,
        "output_tokens": usage_out,
        "cost_usd": out.get("total_cost_usd"),
        "cost_is_estimate": True,
        "cost_basis": "claude CLI total_cost_usd (list price)",
    }
    return data, text, usage


def _call_anthropic(system, user, schema, model, max_tokens, settings, timeout):
    try:
        import anthropic
    except ImportError as exc:
        raise LLMError("anthropic SDK not installed") from exc
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise LLMError("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(timeout=timeout, max_retries=2)
    kwargs = dict(model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": user}])
    if system:
        kwargs["system"] = system
    if schema is not None:
        kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
    with client.messages.stream(**kwargs) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise LLMError("model refused the request (stop_reason=refusal)")
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    data = _extract_json(text) if schema is not None else None
    u = msg.usage
    input_tokens = int(getattr(u, "input_tokens", 0) or 0) + int(getattr(u, "cache_read_input_tokens", 0) or 0) \
        + int(getattr(u, "cache_creation_input_tokens", 0) or 0)
    output_tokens = int(getattr(u, "output_tokens", 0) or 0)
    cost = _price(settings.get("prices", {}), model, input_tokens, output_tokens)
    usage = {"provider": "anthropic", "model": model, "input_tokens": input_tokens, "output_tokens": output_tokens,
             "cost_usd": cost, "cost_is_estimate": cost is not None, "cost_basis": "list price table in config/models.json"}
    return data, text, usage


def _call_openai(system, user, schema, model, max_tokens, settings, timeout):
    try:
        import openai
    except ImportError as exc:
        raise LLMError("openai SDK not installed") from exc
    if not os.environ.get("OPENAI_API_KEY"):
        raise LLMError("OPENAI_API_KEY is not set")
    client = openai.OpenAI(timeout=timeout, max_retries=2)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    kwargs = dict(model=model, messages=messages)
    if schema is not None:
        kwargs["response_format"] = {"type": "json_schema", "json_schema": {"name": "result", "schema": schema, "strict": False}}
    resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    data = _extract_json(text) if schema is not None else None
    u = resp.usage
    input_tokens = int(getattr(u, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(u, "completion_tokens", 0) or 0)
    cost = _price(settings.get("prices", {}), model, input_tokens, output_tokens)
    usage = {"provider": "openai", "model": model, "input_tokens": input_tokens, "output_tokens": output_tokens,
             "cost_usd": cost, "cost_is_estimate": cost is not None, "cost_basis": "list price table in config/models.json"}
    return data, text, usage


_CALLERS = {"claude-cli": _call_claude_cli, "anthropic": _call_anthropic, "openai": _call_openai}


def complete(*, system: str, user: str, schema: dict | None = None, stage: str, run_dir: str | None = None,
             label: str = "", settings: dict | None = None, timeout: int = 1800, retries: int = 2) -> dict:
    """Run one completion. Returns {"data", "text", "usage"}; raises LLMError after retries."""
    settings = settings or stage_settings(stage, run_dir)
    provider, model, max_tokens = settings["provider"], settings["model"], settings["max_tokens"]
    caller = _CALLERS[provider]
    last_exc = None
    for attempt in range(retries + 1):
        started = time.time()
        try:
            data, text, usage = caller(system, user, schema, model, max_tokens, settings, timeout)
            usage["duration_seconds"] = round(time.time() - started, 3)
            _log_call(run_dir, {"at": _now(), "stage": stage, "label": label, "attempt": attempt + 1, "ok": True,
                                "provider": provider, "model": usage.get("model"),
                                "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                                "cost_usd": usage.get("cost_usd"), "cost_is_estimate": usage.get("cost_is_estimate"),
                                "duration_seconds": usage["duration_seconds"],
                                "prompt_chars": len(system or "") + len(user or "")})
            return {"data": data, "text": text, "usage": usage}
        except (LLMError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
            last_exc = exc
            _log_call(run_dir, {"at": _now(), "stage": stage, "label": label, "attempt": attempt + 1, "ok": False,
                                "provider": provider, "model": model, "error": str(exc)[:500],
                                "duration_seconds": round(time.time() - started, 3)})
            print(f"[llm] {stage}/{label} attempt {attempt + 1} failed: {str(exc)[:300]}", file=sys.stderr)
            if attempt < retries:
                time.sleep(5 * (attempt + 1))
    raise LLMError(f"{stage}/{label}: model call failed after {retries + 1} attempts: {last_exc}")


if __name__ == "__main__":  # smoke test: python lib/llm.py "question"
    q = sys.argv[1] if len(sys.argv) > 1 else "Reply with the JSON {\"ok\": true}."
    res = complete(system="You answer with JSON only.", user=q, stage="smoke",
                   schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False},
                   settings={"provider": os.environ.get("LLM_PROVIDER", "claude-cli"), "model": os.environ.get("LLM_MODEL", "claude-haiku-4-5"),
                             "max_tokens": 256, "prices": {}, "max_budget_usd": 1.0})
    print(json.dumps(res, indent=2))
