window.addEventListener("load", () => {
  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      for (const node of mutation.addedNodes) {
        const turns = document.querySelectorAll('[data-testid^="conversation-turn"]');
        if (turns.length === 0) return;

        let userTurn;
        // user prompt
        if (turns.length === 1) {
          userTurn = turns[0];
        } else {
          // user is second to last
          userTurn = turns[turns.length - 2];
        }

        if (!userTurn) return;

        const promptText = userTurn.innerText.trim();
        if (!promptText) return;

        console.log("Captured prompt:", promptText);

        chrome.runtime.sendMessage(
          {
            action: "analyze",
            prompt: promptText
          },
          () => {
            console.log("Sent prompt to background.js");
          }
        );
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
