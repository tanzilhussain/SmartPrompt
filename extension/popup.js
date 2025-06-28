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
    document.getElementById("token-count").textContent = data.tokens;
    document.getElementById("prompt-type").textContent = data.type;
    document.getElementById("tone").textContent = data.tone;
    document.getElementById("verbosity").textContent = data["verbosity level"];
}





// grab DOM elements
// fill DOM elements with prompt data