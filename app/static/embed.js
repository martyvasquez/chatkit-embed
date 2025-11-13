(function () {
  const scriptEl = document.currentScript;
  if (!scriptEl) {
    console.error("ChatKit embed: unable to determine current script element.");
    return;
  }

  const appId = scriptEl.getAttribute("data-app-id");
  if (!appId) {
    console.error("ChatKit embed: data-app-id is required.");
    return;
  }

  let scriptOrigin;
  try {
    const srcUrl = new URL(scriptEl.src);
    scriptOrigin = srcUrl.origin;
  } catch (err) {
    console.warn("ChatKit embed: falling back to window origin.", err);
    scriptOrigin = window.location.origin;
  }

  const requestOrigin = window.location.origin;
  const CONFIG_URL = `${scriptOrigin}/embed/config/${encodeURIComponent(appId)}?origin=${encodeURIComponent(requestOrigin)}`;
  const SESSION_URL = `${scriptOrigin}/api/chatkit/session/${encodeURIComponent(appId)}`;

  const chatkitScript = document.createElement("script");
  chatkitScript.src = "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js";
  chatkitScript.async = true;
  chatkitScript.onload = initChatWidget;
  chatkitScript.onerror = function () {
    console.error("ChatKit embed: failed to load ChatKit script.");
  };
  document.head.appendChild(chatkitScript);

  async function initChatWidget() {
    let configResponse;
    try {
      configResponse = await fetch(CONFIG_URL, {
        credentials: "omit",
        mode: "cors",
      });
    } catch (err) {
      console.error("ChatKit embed: failed to fetch config.", err);
      return;
    }

    if (!configResponse.ok) {
      console.warn("ChatKit embed: widget unavailable on this domain.");
      return;
    }

    const payload = await configResponse.json();
    const options = payload.options || {};

    const container = document.createElement("div");
    container.style.position = "fixed";
    container.style.bottom = "20px";
    container.style.right = "20px";
    container.style.width = "360px";
    container.style.height = "600px";
    container.style.zIndex = "999999";
    container.style.boxShadow = "0 15px 30px rgba(0,0,0,0.2)";
    container.style.borderRadius = "18px";
    container.style.overflow = "hidden";
    document.body.appendChild(container);

    const element = document.createElement("openai-chatkit");
    container.appendChild(element);

    element.setOptions({
      api: {
        async getClientSecret(existing) {
          let response;
          try {
            response = await fetch(SESSION_URL, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                origin: requestOrigin,
                existing_client_secret: existing ? existing.client_secret : null,
              }),
            });
          } catch (err) {
            console.error("ChatKit embed: failed to obtain client secret.", err);
            throw err;
          }

          if (!response.ok) {
            throw new Error("ChatKit embed: backend rejected client secret request.");
          }
          const secretPayload = await response.json();
          return secretPayload.client_secret;
        },
      },
      ...options,
    });
  }
})();
