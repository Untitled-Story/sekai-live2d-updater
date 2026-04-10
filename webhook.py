import logging

import aiohttp

logger = logging.getLogger("live2d")


async def on_updated(added_models: list[str]) -> None:
    import config

    webhook_url = getattr(config, "WEBHOOK_URL", None)
    if not webhook_url or not added_models:
        return

    timeout = getattr(config, "WEBHOOK_TIMEOUT", 10)
    webhook_secret = getattr(config, "WEBHOOK_SECRET", None)

    display_limit = 10
    names_display = "\n".join(f"- {name}" for name in added_models[:display_limit])
    if len(added_models) > display_limit:
        names_display += f"\n- ...及其他 {len(added_models) - display_limit} 个模型"

    payload = {"data": f"收到 {len(added_models)} 个 Live2D 模型更新。\n{names_display}"}
    if webhook_secret:
        payload["secret"] = webhook_secret

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                if response.status < 400:
                    logger.info("Webhook delivered to %s (status %d)", webhook_url, response.status)
                else:
                    logger.warning(
                        "Webhook delivery to %s returned status %d",
                        webhook_url,
                        response.status,
                    )
    except Exception:
        logger.warning("Webhook delivery to %s failed", webhook_url, exc_info=True)
