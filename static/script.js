document.getElementById("analyzeBtn").addEventListener("click", analyzeNews);

async function analyzeNews() {
  const text = document.getElementById("input").value.trim();
  const progressDiv = document.getElementById("progress");
  const resultDiv = document.getElementById("result");

  resultDiv.classList.add("hidden");
  progressDiv.textContent = "";

  if (!text) {
    progressDiv.textContent = "⚠️ Please enter text to analyze.";
    return;
  }

  try {
    progressDiv.textContent = "Connecting to TruthSleuth AI...";
    console.log("Connecting to backend...");

    setTimeout(() => (progressDiv.textContent = "Analyzing sources..."), 800);
    setTimeout(() => (progressDiv.textContent = "Cross-checking facts..."), 1800);
    setTimeout(() => (progressDiv.textContent = "Generating final report..."), 2800);

    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();
    console.log("✅ Received data:", data);

    progressDiv.textContent = "✅ Analysis complete!";
    resultDiv.classList.remove("hidden");

    if (data.error) {
      resultDiv.innerHTML = `<b>Error:</b> ${data.error}`;
      return;
    }

    resultDiv.innerHTML = `
      <b>Score:</b> ${data.score}/100<br>
      <b>Classification:</b> ${data.classification}<br>
      <b>Sources:</b> ${data.sources.join(", ") || "No verified sources found"}<br><br>
      <b>Reasoning:</b><br>${data.reasoning}
    `;
  } catch (err) {
    console.error("❌ Fetch error:", err);
    progressDiv.textContent = "❌ Could not connect to backend.";
  }
}
