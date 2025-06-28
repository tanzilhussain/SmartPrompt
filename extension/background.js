chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyze") {
    console.log("Received prompt in background.js:", request.prompt);

    chrome.storage.local.set({
      lastPrompt: {
        prompt: request.prompt,
        timestamp: new Date().toLocaleString("en-GB")
      }
    }, () => {
      console.log("Prompt stored in chrome.storage");
    });
  }
});
