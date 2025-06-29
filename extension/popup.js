// load prompt data (token-count, prompt-type, tone, verbosity)
document.addEventListener("DOMContentLoaded", function () {
    chrome.storage.local.get("lastPrompt", function(result){
        const data = result.lastPrompt
        if (!data) {
            console.log("no prompt data found");
            return;
        }
        console.log("loaded prompt: ", data);
        updatePopup(data)
    });
});
chrome.storage.onChanged.addListener(function (changes, area) {
    if (area === "local" && changes.lastPrompt) {
        const data = changes.lastPrompt.newValue;
        updatePopup(data)
    }
});

function updatePopup(data) {
    document.getElementById("original_prompt").textContent = data.originalPrompt;
    document.getElementById("token_count").textContent = data.tokenCount;
    document.getElementById("prompt_type").textContent = data.type;
    document.getElementById("tone").textContent = data.tone;
    document.getElementById("verbosity").textContent = data.verbosity;
}





// grab DOM elements
// fill DOM elements with prompt data