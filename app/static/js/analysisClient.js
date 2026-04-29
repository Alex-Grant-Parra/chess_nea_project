import { postJson } from "./api.js";

const fenInput = document.getElementById("analysisFen");
const depthInput = document.getElementById("analysisDepth");
const timeInput = document.getElementById("analysisTime");
const output = document.getElementById("analysisOutput");

document.getElementById("analyseButton").addEventListener("click", async () => {
    output.textContent = "Searching...";
    try {
        const result = await postJson("/api/analysis/evaluate", {
            fen: fenInput.value,
            maxDepth: Number(depthInput.value),
            timeLimitSeconds: Number(timeInput.value),
        });
        output.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        output.textContent = error.message;
    }
});
