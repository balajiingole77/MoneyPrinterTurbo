#!/usr/bin/env python3
"""
Railway entrypoint for MoneyPrinterTurbo.

config.toml is gitignored and MPT does NOT expand ${ENV} placeholders,
so we generate a valid config.toml at container start from environment
variables (set in Railway -> Variables). Secrets never live in git.

Cost-optimized defaults (see MINIMUM-COST-VIDEO-PLAN.md):
  - LLM:      Gemini Flash (free tier), DeepSeek fallback
  - Stock:    Pexels
  - Subtitle: faster-whisper (base model, CPU)
"""
import os
import toml

BASE = os.path.join(os.path.dirname(__file__), "config.example.toml")
OUT = os.path.join(os.path.dirname(__file__), "config.toml")


def split_keys(value: str) -> list[str]:
    """Comma-separated env value -> list of trimmed keys."""
    return [k.strip() for k in value.split(",") if k.strip()]


def main() -> None:
    cfg = toml.load(BASE)
    app = cfg.setdefault("app", {})

    # --- Stock video (Pexels primary, Pixabay backup) ---
    app["video_source"] = os.getenv("VIDEO_SOURCE", "pexels")
    if os.getenv("PEXELS_API_KEY"):
        app["pexels_api_keys"] = split_keys(os.environ["PEXELS_API_KEY"])
    if os.getenv("PIXABAY_API_KEY"):
        app["pixabay_api_keys"] = split_keys(os.environ["PIXABAY_API_KEY"])

    # --- LLM: Gemini Flash primary, DeepSeek fallback ---
    app["llm_provider"] = os.getenv("LLM_PROVIDER", "gemini")
    if os.getenv("GEMINI_API_KEY"):
        app["gemini_api_key"] = os.environ["GEMINI_API_KEY"]
    app["gemini_model_name"] = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
    if os.getenv("DEEPSEEK_API_KEY"):
        app["deepseek_api_key"] = os.environ["DEEPSEEK_API_KEY"]
    app["deepseek_base_url"] = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    app["deepseek_model_name"] = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

    # --- API server bind ---
    # config.py reads listen_host/listen_port from the ROOT of the config
    # (_cfg.get("listen_port")), NOT from [app]. Set them at top level so
    # uvicorn binds the port Railway routes to (default 8080).
    cfg["listen_host"] = "0.0.0.0"
    cfg["listen_port"] = int(os.getenv("PORT", "8080"))

    # --- Subtitles: faster-whisper on CPU ---
    app["subtitle_provider"] = os.getenv("SUBTITLE_PROVIDER", "whisper")
    whisper = cfg.setdefault("whisper", {})
    whisper["model_size"] = os.getenv("WHISPER_MODEL_SIZE", "base")
    whisper["device"] = os.getenv("WHISPER_DEVICE", "CPU")
    whisper["compute_type"] = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    with open(OUT, "w", encoding="utf-8") as f:
        toml.dump(cfg, f)

    print(f"[railway_entrypoint] wrote {OUT} "
          f"(llm={app['llm_provider']}, source={app['video_source']}, "
          f"subtitle={app['subtitle_provider']})")


if __name__ == "__main__":
    main()
