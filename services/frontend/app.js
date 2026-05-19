const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";
const POLL_INTERVAL_MS = 3000;

const stateUpload = document.getElementById("state-upload");
const stateLoading = document.getElementById("state-loading");
const stateResult = document.getElementById("state-result");
const feedback = document.getElementById("feedback");

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const selectedFileName = document.getElementById("selected-file-name");
const selectFileButton = document.getElementById("select-file-button");
const submitButton = document.getElementById("submit-button");

const loadingAnalysisId = document.getElementById("loading-analysis-id");

const componentList = document.getElementById("component-list");
const riskList = document.getElementById("risk-list");
const recommendationList = document.getElementById("recommendation-list");
const diagramPreview = document.getElementById("diagram-preview");
const diagramPreviewEmpty = document.getElementById("diagram-preview-empty");
const diagramPreviewFileName = document.getElementById("diagram-preview-file-name");
const diagramModal = document.getElementById("diagram-modal");
const diagramModalImage = document.getElementById("diagram-modal-image");
const closeDiagramModalButton = document.getElementById("close-diagram-modal");
const newAnalysisButton = document.getElementById("new-analysis-button");

let selectedFile = null;
let activePollTimeout = null;
let diagramPreviewUrl = null;

function showFeedback(message, type = "error") {
    const palette = {
        error: "border-red-400/50 bg-red-500/10 text-red-200",
        info: "border-info/40 bg-info/10 text-info",
        success: "border-success/40 bg-success/10 text-success"
    };

    feedback.className = `mb-4 rounded-xl border px-4 py-3 text-sm ${palette[type] || palette.error}`;
    feedback.textContent = message;
    feedback.classList.remove("hidden");
}

function clearFeedback() {
    feedback.classList.add("hidden");
    feedback.textContent = "";
}

function setState(state) {
    const states = [stateUpload, stateLoading, stateResult];
    states.forEach((section) => {
        section.classList.add("hidden", "opacity-0");
    });

    const selectedState = {
        upload: stateUpload,
        loading: stateLoading,
        result: stateResult
    }[state];

    if (!selectedState) {
        return;
    }

    selectedState.classList.remove("hidden");
    requestAnimationFrame(() => {
        selectedState.classList.remove("opacity-0");
    });
}

function resetAnalysis() {
    if (diagramModal?.open) {
        diagramModal.close();
    }

    if (diagramPreviewUrl) {
        URL.revokeObjectURL(diagramPreviewUrl);
        diagramPreviewUrl = null;
    }

    selectedFile = null;
    fileInput.value = "";
    selectedFileName.textContent = "Nenhum arquivo selecionado";
    submitButton.disabled = true;

    loadingAnalysisId.textContent = "-";
    componentList.innerHTML = "";
    riskList.innerHTML = "";
    recommendationList.innerHTML = "";
    diagramPreview.src = "";
    diagramPreview.classList.add("hidden");
    diagramPreviewEmpty.classList.remove("hidden");
    diagramPreviewFileName.textContent = "";
    if (diagramModalImage) {
        diagramModalImage.src = "";
    }

    if (activePollTimeout) {
        clearTimeout(activePollTimeout);
        activePollTimeout = null;
    }

    clearFeedback();
    setState("upload");
}

function updateFileSelection(file) {
    if (diagramPreviewUrl) {
        URL.revokeObjectURL(diagramPreviewUrl);
        diagramPreviewUrl = null;
    }

    selectedFile = file;
    diagramPreviewUrl = file ? URL.createObjectURL(file) : null;
    selectedFileName.textContent = file ? file.name : "Nenhum arquivo selecionado";
    submitButton.disabled = !file;
}

function renderList(items, targetElement, emptyMessage, badgeClass) {
    targetElement.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const li = document.createElement("li");
        li.className = "rounded-lg border border-lineGlow bg-slate-900/45 px-3 py-2 text-slate-400";
        li.textContent = emptyMessage;
        targetElement.appendChild(li);
        return;
    }

    items.forEach((item, index) => {
        const li = document.createElement("li");
        li.className = "rounded-lg border border-lineGlow bg-slate-900/45 px-3 py-2 text-sm text-slate-100";

        const badge = document.createElement("span");
        badge.className = `mr-2 inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 font-mono text-xs ${badgeClass}`;
        badge.textContent = String(index + 1);

        const text = document.createElement("span");
        text.textContent = typeof item === "string" ? item : JSON.stringify(item);

        li.appendChild(badge);
        li.appendChild(text);
        targetElement.appendChild(li);
    });
}

function renderResult(report) {
    if (diagramPreviewUrl) {
        diagramPreview.src = diagramPreviewUrl;
        diagramPreview.classList.remove("hidden");
        diagramPreviewEmpty.classList.add("hidden");
        diagramPreviewFileName.textContent = selectedFile?.name || "diagrama";
    } else {
        diagramPreview.src = "";
        diagramPreview.classList.add("hidden");
        diagramPreviewEmpty.classList.remove("hidden");
        diagramPreviewFileName.textContent = "";
    }

    renderList(report.componentes, componentList, "Nenhum componente identificado.", "bg-info/20 text-info");
    renderList(report.riscos, riskList, "Nenhum risco identificado.", "bg-warning/20 text-warning");
    renderList(report.recomendacoes, recommendationList, "Nenhuma recomendação gerada.", "bg-accent/20 text-accent");
    setState("result");
}

function openDiagramModal() {
    if (!diagramPreviewUrl || !diagramModal || !diagramModalImage) {
        return;
    }

    diagramModalImage.src = diagramPreviewUrl;
    diagramModal.showModal();
}

function closeDiagramModal() {
    if (!diagramModal?.open) {
        return;
    }

    diagramModal.close();
}

async function pollReport(analysisId) {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/analyses/${analysisId}/report`, {
            method: "GET"
        });

        if (response.status === 404) {
            activePollTimeout = setTimeout(() => {
                pollReport(analysisId);
            }, POLL_INTERVAL_MS);
            return;
        }

        if (!response.ok) {
            const body = await response.text();
            throw new Error(`Falha ao consultar relatório (${response.status}). ${body}`);
        }

        const report = await response.json();
        clearFeedback();
        renderResult(report);
    } catch (error) {
        showFeedback(error.message || "Erro inesperado durante o polling do relatório.");
        setState("upload");
    }
}

async function submitAnalysis() {
    if (!selectedFile) {
        showFeedback("Selecione um arquivo antes de enviar.");
        return;
    }

    clearFeedback();
    setState("loading");

    try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(`${API_BASE_URL}/v1/analyses`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const body = await response.text();
            throw new Error(`Falha no upload (${response.status}). ${body}`);
        }

        const data = await response.json();
        const analysisId = data.analysis_id;

        if (!analysisId) {
            throw new Error("A API não retornou o analysis_id.");
        }

        loadingAnalysisId.textContent = analysisId;
        pollReport(analysisId);
    } catch (error) {
        showFeedback(error.message || "Erro inesperado ao iniciar a análise.");
        setState("upload");
    }
}

function preventDefaults(event) {
    event.preventDefault();
    event.stopPropagation();
}

["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.add("border-accent/70", "bg-accent/5");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove("border-accent/70", "bg-accent/5");
    });
});

dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (file) {
        updateFileSelection(file);
    }
});

selectFileButton.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0] || null;
    updateFileSelection(file);
});

submitButton.addEventListener("click", submitAnalysis);
newAnalysisButton.addEventListener("click", resetAnalysis);
diagramPreview.addEventListener("click", openDiagramModal);
closeDiagramModalButton?.addEventListener("click", closeDiagramModal);
diagramModal?.addEventListener("click", (event) => {
    if (event.target === diagramModal) {
        closeDiagramModal();
    }
});

resetAnalysis();
