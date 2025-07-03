class SmartPromptPopup {
  constructor() {
   this.currentView = "stats";
    this.promptData = {};       // will be computed from history
    this.promptHistory = [];    // full array from server
    this.charts = {};
  }

  async init() {
    this.bindEvents()
    this.toggleViews()
    const { rows = [] } = await this.bgRequest({ action: "get_history", limit: 100 });
    this.promptHistory = rows;
    this.computePromptData();
    this.updateStats()
    this.renderCharts()
    document.getElementById("copyBtn").addEventListener("click", () => {
      const text = document.getElementById("simplifiedOutput").textContent;
      navigator.clipboard.writeText(text).catch((err) => {
        alert("Failed to copy");
        console.error(err);
      });
    });
  }

    // build promptData summary from this.promptHistory
    computePromptData() {
    const logs = this.promptHistory;

    const average = arr => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;

    const countBy = (arr, key) => {
      return arr.reduce((acc, item) => {
        const value = item[key];
        acc[value] = (acc[value] || 0) + 1;
        return acc;
      }, {});
    };

    const extractTopics = logs => {
      const freq = {};
      logs.forEach(log => {
        const prompt = log["original prompt"] || log.prompt || "";
        prompt.toLowerCase().split(/\W+/)
          .filter(word => word.length > 3)
          .forEach(word => {
            freq[word] = (freq[word] || 0) + 1;
          });
      });

      return Object.entries(freq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([word, _count]) => word);
    };
    
    const rawVerbosityCounts = countBy(logs, "verbosity");
    this.promptData = {
      totalPrompts: logs.length,
      avgLength: Math.round(average(logs.map(l => l["word count"]))),
      commonTopics: extractTopics(logs),
      promptTones: countBy(logs, "tone") || {},
      repetitionData: logs.map(l => l["repetition ratio"] || 0),
      fillerData: logs.map(l => l["filler word density"] || 0),
      verbosityData: {
        high: rawVerbosityCounts.high || 0,
        medium: rawVerbosityCounts.medium || 0,
        low: rawVerbosityCounts.low || 0,
      }
    };

  }
  
  groupPromptsByDate(logs) {
    return logs.reduce((acc, log) => {
      const date = log.timestamp?.split(" ")[0] || "Unknown";
      if (!acc[date]) acc[date] = [];
      acc[date].push(log);
      return acc;
    }, {});
  }



  // populate the history tab
  loadPromptHistoryView() {
    const container = document.getElementById("historyList");
    if (!this.promptHistory.length) {
      container.innerHTML = "<li>No history found.</li>";
      return;
    }

    const grouped = this.groupPromptsByDate(this.promptHistory);
    container.innerHTML = ""; // Clear old content

    Object.entries(grouped).forEach(([date, logs]) => {
      // Create a collapsible section
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = `${date} — ${logs.length} prompt${logs.length > 1 ? "s" : ""}`;
      details.appendChild(summary);

      const ul = document.createElement("ul");
      logs.forEach(log => {
        const li = document.createElement("li");
        li.textContent = log["original prompt"] || log.prompt || "undefined";
        ul.appendChild(li);
      });

      details.appendChild(ul);
      container.appendChild(details);
    });
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
    // simplify action
    const simplifyActionBtn = document.getElementById("simplifyActionBtn")
    if (simplifyActionBtn) {
      simplifyActionBtn.addEventListener("click", () => {
        this.handleSimplifyAction()
      })
    }
    // listen for messages from content script 
    window.chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.type === "PROMPT_ANALYZED") {
        this.updatePromptData(message.data)
      }
    })
  }
  
  bgRequest(msg) {
    return new Promise(res =>
      chrome.runtime.sendMessage(msg, res)
    );
  }

  async showStatsView() {
    console.log("showStatsView() called");
    this.currentView = "stats";
    this.setActiveButton("statsBtn")
    this.toggleViews();
    const { rows } = await this.bgRequest({ action:"get_history", limit:100 });
    this.promptHistory = rows;         
    this.computePromptData();
    this.updateStats();     
    this.renderCharts();    
  }

  async showHistoryView() {
    console.log("showHistoryView() called");
    this.currentView = "history";
    this.setActiveButton("historyBtn");
    this.toggleViews();
    const { rows } = await this.bgRequest({ action:"get_history", limit:10 });
    this.promptHistory = rows;
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

  async handleSimplifyAction() {
    const prompt = document.getElementById("promptInput").value.trim();
    const out    = document.getElementById("simplifiedOutput");
    const copy = document.getElementById("copyBtn")
    if (!prompt) {
      out.textContent = "Please enter a prompt.";
      return;
    }
    copy.style.display = "none";
    

    out.textContent = "Simplifying…";
    chrome.runtime.sendMessage(
      { action: "simplify", prompt },
      (resp) => {
        
        if (chrome.runtime.lastError) {
          out.textContent = "Extension error: " + chrome.runtime.lastError.message;
          return;
        }

        if (resp && resp.success) {
          console.log("Simplified response: ", resp)
          out.textContent = resp.simplified || "No suggestion returned.";
          copy.style.display = "inline-block";
        } else {
          out.textContent = "Failed to simplify prompt.";
          copy.style.display = "none";
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
      // existing Chart.js code, but now reading from this.promptData
      this.renderPromptTonesChart();
      this.renderRepetitionChart();
      this.renderFillerChart();
      this.renderVerbosityChart();
    }

    renderPromptTonesChart() {
      console.log("Prompt Tones Data:", this.promptData.promptTones);

      const data = this.promptData.promptTones|| {};
      const ctx = document.getElementById("promptTonesChart")?.getContext("2d");
      if (!ctx || Object.keys(data).length === 0) return;
      if (this.charts.promptTones) this.charts.promptTones.destroy();

      this.charts.promptTones = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: Object.keys(this.promptData.promptTones),
          datasets: [
            {
              data: Object.values(this.promptData.promptTones || {}),
              backgroundColor: ["#22c55e", "#6366f1", "#ec4899"],
              borderWidth: 0,
            },
          ],
        },
        options: {
          cutout: "60%",
          plugins: { legend: { display: false } },
          responsive: false,
          maintainAspectRatio: false,
        },
      });
    }


  renderRepetitionChart() {
    const data = this.promptData.repetitionData || [];
    const ctx = document.getElementById("repetitionChart")?.getContext("2d");
    if (!ctx || !data.length === 0) return;

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
    console.log("Verbosity Data:", this.promptData.verbosityData);

    const data = this.promptData.verbosityData || {};
    const ctx = document.getElementById("verbosityChart")?.getContext("2d");
    if (!ctx || Object.keys(data).length === 0) return;
    if (this.charts.verbosity) this.charts.verbosity.destroy();

    this.charts.verbosity = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["High", "Medium", "Low"],
        datasets: [{
          data: [
            this.promptData.verbosityData.high || 0,
            this.promptData.verbosityData.medium || 0,
            this.promptData.verbosityData.low || 0,
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
    });
  }


  renderFillerChart() {
    const data = this.promptData.fillerData || {};
    const ctx = document.getElementById("fillerChart")?.getContext("2d");
    if (!ctx || !data.length === 0) return;
    if (this.charts.filler) this.charts.filler.destroy();

    this.charts.filler = new Chart(ctx, {
      type: "line",
      data: {
        labels: (this.promptData.fillerData || []).map((_, i) => i + 1),
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
    });
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


  
}

document.addEventListener("DOMContentLoaded", async() => {
  const popup = new SmartPromptPopup()
  await popup.init()
})

