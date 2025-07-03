window.addEventListener("load", () => {
  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      for (const node of mutation.addedNodes) {
        const turns = document.querySelectorAll('[data-testid^="conversation-turn"]');
        if (turns.length === 0) return;

        let userTurn;
        let lastSentPrompt = null;
        // user prompt
        if (turns.length === 1) {
          userTurn = turns[0];
        } else {
          // user is second to last
          userTurn = turns[turns.length - 2];
        }

        if (!userTurn) return;

        userInput = userTurn.innerText.trim();
        if (!userInput) return;
        let promptText = userInput.replace(/^You said:\s*/, "");
        console.log("Captured prompt:", promptText);
        if (chrome.runtime && chrome.runtime.id) {
          if (promptText === lastSentPrompt) return; // skip duplicate
          lastSentPrompt = promptText;
          chrome.runtime.sendMessage(
            {
              action: "analyze",
              prompt: promptText
            },
            () => {
              if (chrome.runtime.lastError) {
                console.error("Message send error:", chrome.runtime.lastError.message);
              } else {
                console.log("Sent prompt to background.js");
              }
            }
          );
        } else {
          console.warn("Extension context is invalidated – cannot send message");
        }

      }
    }
  });

  const intervalID = setInterval(() => {
    const firstArticle = document.querySelector("main article");
    if (firstArticle) {
      observer.observe(firstArticle.parentElement, { childList: true });
      clearInterval(intervalID);
      console.log("MutationObserver watching");
    }
  }, 500);
});
