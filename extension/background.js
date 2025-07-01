console.log("bg script loaded")
function saveLastPrompt(result) {
  const record = {
    originalPrompt      : result.prompt,
    tokenCount          : result["token count"],
    wordCount           : result["word count"],
    averageWordLength   : result["average word length"],
    type                : result.type,
    tone                : result.tone,
    repetitionRatio     : result["repetition ratio"],
    fillerWordDensity   : result["filler word density"],
    verbosity           : result.verbosity,
  };
  return new Promise(res =>
    chrome.storage.local.set({ lastPrompt: record }, () => res(record))
  );
}
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
    .then(r => r.json())
    .then(saveLastPrompt)                   
    .then(stored => {
      /* broadcast so popup can refresh immediately */
      chrome.runtime.sendMessage({ action:"prompt_analyzed", data: stored });
      sendResponse({ success:true, data: stored });
    })
    .catch(err => {
      console.error("Analyze error:", err);
      sendResponse({ success:false, error:String(err) });
    });
    return true;       
  }
  if (request.action === "simplify") {
    fetch("http://127.0.0.1:8000/simplify", {
      method  : "POST",
      headers : { "Content-Type":"application/json" },
      body    : JSON.stringify({ prompt: request.prompt })
    })
    .then(r => r.json())
    .then(({ simplified_prompt }) => {
      sendResponse({ success:true, simplified:simplified_prompt });
    })
    .catch(err => {
      sendResponse({ success:false, error:String(err) });
    });
    return true;
  }
});
