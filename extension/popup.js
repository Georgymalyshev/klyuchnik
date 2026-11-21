const NAMES = ["alarms", "masked", "cancelled", "sentAnyway", "disabledTimes"];

function show(data) {
  document.getElementById("enabled").checked = data.enabled;
  for (const name of NAMES) {
    document.getElementById(name).textContent = data.stats[name] || 0;
  }
}

chrome.storage.local.get({ enabled: true, stats: {} }, show);

document.getElementById("enabled").addEventListener("change", (e) => {
  const on = e.target.checked;
  chrome.storage.local.get({ stats: {} }, (data) => {
    const stats = data.stats;
    if (!on) {
      stats.disabledTimes = (stats.disabledTimes || 0) + 1;
      stats.lastDisabled = new Date().toISOString();
    }
    chrome.storage.local.set({ enabled: on, stats: stats }, () => {
      chrome.storage.local.get({ enabled: true, stats: {} }, show);
    });
  });
});

document.getElementById("test").addEventListener("click", () => {
  chrome.tabs.create({ url: chrome.runtime.getURL("test.html") });
});

document.getElementById("copy").addEventListener("click", () => {
  chrome.storage.local.get({ enabled: true, stats: {} }, (data) => {
    const report = { version: chrome.runtime.getManifest().version, enabled: data.enabled, stats: data.stats };
    navigator.clipboard.writeText(JSON.stringify(report, null, 2)).then(() => {
      document.getElementById("copied").textContent = "Скопировано. В статистике нет самих секретов, только счётчики.";
    });
  });
});
