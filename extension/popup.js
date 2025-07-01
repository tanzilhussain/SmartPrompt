class SmartPromptPopup {
  constructor() {
   this.currentView = "stats";
    this.promptData = {};       // will be computed from history
    this.promptHistory = [];    // full array from server
    this.charts = {};
  }

  async init() {
    await this.loadPromptHistoryFromServer();
    this.bindEvents();
    this.toggleViews(); 
    this.loadStoredData()
    // this.bindEvents()
    this.renderCharts()
    this.updateStats()
  }
    // 1️⃣ Fetch the full prompt_log.jsonl from your backend
  async loadPromptHistoryFromServer() {
    try {
      const res = await fetch("http://127.0.0.1:8000/log");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.promptHistory = await res.json();

      // 2️⃣ Recompute your aggregated promptData
      this.computePromptData();

    } catch (err) {
      console.error("Failed to fetch prompt history:", err);
      // Fallback to empty history
      this.promptHistory = [];
      this.promptData = this.getEmptyPromptData();
    }
  }

  // 3️⃣ Build promptData summary from this.promptHistory
  computePromptData() {
    const logs = this.promptHistory;

    // helper functions (you can move these outside the class)
    const average = arr => arr.reduce((a,b)=>a+b,0)/ (arr.length||1);
    const countBy = (arr, key) => arr.reduce((acc,i)=>{
      const v = i[key]; acc[v]=(acc[v]||0)+1; return acc;
    }, {});
    const extractTopics = (logs) => {
      const freq = {};
      logs.forEach(l => {
        (l.prompt||"").toLowerCase().split(/\W+/)
         .filter(w=>w.length>3)
         .forEach(w=>freq[w]=(freq[w]||0)+1);
      });
      return Object.entries(freq)
        .sort((a,b)=>b[1]-a[1])
        .slice(0,5)
        .map(e=>e[0]);
    };

    this.promptData = {
      totalPrompts:       logs.length,
      avgLength:          Math.round(average(logs.map(l=>l.word_count))),
      commonTopics:       extractTopics(logs),
      promptTypes:        countBy(logs, "type"),
      repetitionData:     logs.map(l=>l.repetition_ratio),
      fillerData:         logs.map(l=>l.filler_word_density),
      verbosityData:      countBy(logs, "verbosity"),
    };
  }

  // 4️⃣ Populate the History tab
  loadPromptHistoryView() {
    const ul = document.getElementById("historyList");
    if (!this.promptHistory.length) {
      ul.innerHTML = "<li>No history found.</li>";
      return;
    }
    ul.innerHTML = this.promptHistory
      .map(l => `<li>[${l.timestamp.slice(0,19)}] ${l.prompt}</li>`)
      .join("");
  }

  bindEvents() {
    document.getElementById("simplifyBtn").addEventListener("click", () => {
      this.showSimplifyView()
    })
    document.getElementById("statsBtn").addEventListener("click", () => {
      this.showStatsView()
    })
    document.getElementById("historyBtn").addEventListener("click", () => {
      this.showHistoryView()
    })
    // Simplify action
    const simplifyActionBtn = document.getElementById("simplifyActionBtn")
    if (simplifyActionBtn) {
      simplifyActionBtn.addEventListener("click", () => {
        this.handleSimplifyAction()
      })
    }
    // Listen for messages from content script - idk if i need this
    window.chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.type === "PROMPT_ANALYZED") {
        this.updatePromptData(message.data)
      }
    })
  }

  async showStatsView() {
    console.log("showStatsView() called");
    this.currentView = "stats";
    await this.loadPromptHistoryFromServer(); 
    this.setActiveButton("statsBtn")
    this.toggleViews();
    this.updateStats();     // updates DOM text (#avgLength, #topicList)
    this.renderCharts();    // draws all Chart.js charts
  }

  async showHistoryView() {
    console.log("showHistoryView() called");
    this.currentView = "history";
    await this.loadPromptHistoryFromServer();
    this.setActiveButton("historyBtn");
    this.toggleViews();
    this.loadPromptHistoryView();
  }

  showSimplifyView() {
    console.log("showSimplifyView() called");
    this.currentView = "simplify";
    this.setActiveButton("simplifyBtn");
    this.toggleViews();
    const input  = document.getElementById("promptInput");
    const output = document.getElementById("simplifiedOutput");
    input.value  = "";                  
    output.textContent = "";            
    input.focus();    
  }


  setActiveButton(activeId) {
    document.querySelectorAll(".action-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    const activeBtn = document.getElementById(activeId);
    if (activeBtn) activeBtn.classList.add("active");

  }

  async loadStoredData() {
    try {
      const result = await window.chrome.storage.local.get(["promptData", "promptHistory"])
      if (result.promptData) {
        this.promptData = { ...this.promptData, ...result.promptData }
      }
      if (result.promptHistory) {
        this.promptHistory = result.promptHistory
      }
      this.updateStats()
      this.renderCharts();
    } catch (error) {
      console.error("Error loading stored data:", error)
    }
  }

  async loadPromptHistory() {
    try {
      const result = await window.chrome.storage.local.get(["promptHistory"])
      const history = result.promptHistory || []
      const historyList = document.getElementById("historyList")
      if (history.length === 0) {
        historyList.innerHTML = '<li>No prompt history found.</li>'
        return
      }
      historyList.innerHTML = history.map(item => `<li>${item.prompt || item.Prompt || JSON.stringify(item)}</li>`).join("")
    } catch (error) {
      document.getElementById("historyList").innerHTML = '<li>Error loading history.</li>'
    }
  }

  async handleSimplifyAction() {
    const prompt = document.getElementById("promptInput").value.trim();
    const out    = document.getElementById("simplifiedOutput");

    if (!prompt) {
      out.textContent = "Please enter a prompt.";
      return;
    }

    out.textContent = "Simplifying…";

    chrome.runtime.sendMessage(
      { action: "simplify", prompt },
      (resp) => {
        if (chrome.runtime.lastError) {
          out.textContent = "Extension error: " + chrome.runtime.lastError.message;
          return;
        }

        if (resp && resp.success) {
          out.textContent = resp.simplified || "No suggestion returned.";
        } else {
          out.textContent = "Failed to simplify prompt.";
        }
      }
    );
  }


  toggleViews() {
    ["stats", "history", "simplify"].forEach((view) => {
      const el = document.getElementById(`${view}-view`);
      if (el) {
        if (this.currentView === view) {
          el.classList.add("active");
        } else {
          el.classList.remove("active");
        }
      }
    });
  }


  updateStats() {
    document.getElementById("avgLength").textContent = this.promptData.avgLength || "—";
    document.getElementById("topicList").innerHTML =
      (this.promptData.commonTopics || []).map(t=>`<li>• ${t}</li>`).join("");
  }

  renderCharts() {
    // your existing Chart.js code, but now reading from this.promptData
    this.renderPromptTypesChart();
    this.renderRepetitionChart();
    this.renderFillerChart();
    this.renderVerbosityChart();
  }

  renderPromptTypesChart() {
    const ctx = document.getElementById("promptTypesChart")?.getContext("2d");
    if (!ctx) return;
    if (this.charts.promptTypes) this.charts.promptTypes.destroy()
    this.charts.promptTypes = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Casual", "Neutral", "Formal"],
        datasets: [{
          data: [
            this.promptData.promptTypes.casual,
            this.promptData.promptTypes.neutral,
            this.promptData.promptTypes.formal,
          ],
          backgroundColor: ["#22c55e", "#6366f1", "#ec4899"],
          borderWidth: 0,
        }],
      },
      options: {
        cutout: "60%",
        plugins: { legend: { display: false } },
        responsive: false,
        maintainAspectRatio: false,
      },
    })
  }

  renderRepetitionChart() {
    const ctx = document.getElementById("repetitionChart").getContext("2d")
    if (this.charts.repetition) this.charts.repetition.destroy()
    this.charts.repetition = new Chart(ctx, {
      type: "line",
      data: {
        labels: this.promptData.repetitionData.map((_, i) => i + 1),
        datasets: [{
          data: this.promptData.repetitionData,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245,158,11,0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
        responsive: false,
        maintainAspectRatio: false,
      },
    })
  }

  renderVerbosityChart() {
    const ctx = document.getElementById("verbosityChart").getContext("2d")
    if (this.charts.verbosity) this.charts.verbosity.destroy()
    this.charts.verbosity = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["High", "Medium", "Low"],
        datasets: [{
          data: [
            this.promptData.verbosityData.high || 0,
            this.promptData.verbosityData.medium || 0,
            this.promptData.verbosityData.low || 0
          ],

          backgroundColor: ["#22c55e", "#a3e635", "#fde047"],
          borderRadius: 6,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
        responsive: false,
        maintainAspectRatio: false,
      },
    })
  }

  renderFillerChart() {
    const ctx = document.getElementById("fillerChart").getContext("2d")
    if (this.charts.filler) this.charts.filler.destroy()
    this.charts.filler = new Chart(ctx, {
      type: "line",
      data: {
        labels: this.promptData.fillerData.map((_, i) => i + 1),
        datasets: [{
          data: this.promptData.fillerData,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
        responsive: false,
        maintainAspectRatio: false,
      },
    })
  }

  updatePromptData(newData) {
    this.promptData = { ...this.promptData, ...newData }
    this.saveData()
    this.updateStats()
    this.renderCharts()
  }

  showLoading() {
    document.getElementById("loading").style.display = "flex"
  }

  hideLoading() {
    document.getElementById("loading").style.display = "none"
  }

  showNotification(message) {
    // Simple notification - could be enhanced with a proper notification system
    const notification = document.createElement("div")
    notification.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 1000;
        `
    notification.textContent = message
    document.body.appendChild(notification)

    setTimeout(() => {
      document.body.removeChild(notification)
    }, 3000)
  }

  async saveData() {
    try {
      await window.chrome.storage.local.set({ promptData: this.promptData })
    } catch (error) {
      console.error("Error saving data:", error)
    }
  }
  
  copyToClipboard() {
    var copyText = document.getElementById("simplifiedOutput");
    copyText.select();
    copyText.setSelectionRange(0, 99999); 
    navigator.clipboard.writeText(copyText.value);
    alert("Copied the text: " + copyText.value);
  }
}

document.addEventListener("DOMContentLoaded", async() => {
  const popup = new SmartPromptPopup()
  await popup.init()
})

