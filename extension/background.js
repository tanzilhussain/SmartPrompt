console.log("bg script loaded")
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyze") {
    // send to fastAPI backend
    fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }, 
      body: JSON.stringify({prompt: request.prompt})
    })
    .then(response => response.json())
    .then (data => {
      console.log("Backend response: ", data);
      chrome.storage.local.set({
      lastPrompt: {
      originalPrompt: data["original prompt"],
      tokenCount: data["token count"],
      wordCount: data["word count"],
      average_word_length: data["average word length"],
      type: data.type,
      tone: data.tone,
      repetition_ratio: data["repetition ratio"],
      filler_word_density: data["filler word density"],
      verbosity: data.verbosity,
      simplified_prompt: data.simplified_prompt           
      }
    }, () => {
      console.log("Prompt stored in chrome.storage");
      sendResponse({success: true});
    });
    })
    .catch(error => {
      console.error("Error calling backend: ", error);
      sendResponse({ success: false, error});
    });
    return true;
  }
});
