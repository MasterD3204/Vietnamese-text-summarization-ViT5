const summarizeButton = document.getElementById("btn-ph");
const inputText = document.getElementById("input-text");
const summaryOutput = document.getElementById("summary-output");
const lengthSelect = document.getElementById("length-select");

function clearPlaceholder() {
  const placeholderText = document.getElementById("input-text").placeholder;
  if (placeholderText) {
    document.getElementById("input-text").placeholder = "";
  }
}

function addPlaceholder() {
  const inputText = document.getElementById("input-text").value;
  if (!inputText) {
    document.getElementById("input-text").placeholder =
      "Enter your input text here...";
  }
}

function handleFileUpload(files) {
  if (files.length === 0) {
    return;
  }

  const uploadedFile = files[0];
  const formData = new FormData();
  formData.append("file", uploadedFile);

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error(data.error);
      } else {
        inputText.value = data.text;
      }
    })
    .catch((error) => console.error("Error:", error));
}

const panels = document.querySelector(".js-panel");
const modal = document.querySelector(".js-modal");
const modalClose = document.querySelector(".js-modal-close");

function showStatistics() {
  modal.classList.add("open");
}

function hideStatistics() {
  modal.classList.remove("open");
}
panels.addEventListener("click", showStatistics);

modalClose.addEventListener("click", hideStatistics);

summarizeButton.addEventListener("click", async () => {
  const textToSummarize = inputText.value;
  const lengthOption = lengthSelect.value;

  const response = await runPythonScript(textToSummarize, lengthOption);
  summaryOutput.textContent = response.summary;

  if (response.statistics) {
    updateStatistics(response.statistics);
  }
});

async function runPythonScript(textToSummarize, lengthOption) {
  try {
    const response = await fetch("/summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: textToSummarize,
        length: lengthOption, // Gửi giá trị length đã chọn đến server
      }),
    });
    const data = await response.json();
    return data; // Trả về dữ liệu đã nhận từ máy chủ
  } catch (error) {
    console.error(error);
    return { summary: "An error occurred while fetching summary.", statistics: null };
  }
}

// Function to update statistics
function updateStatistics(statistics) {
  const wordCountElement = document.querySelector(".word-count");
  const characterCountElement = document.querySelector(".characters");
  const reductionElement = document.querySelector(".reduction");

  const originalWordCount = statistics.original_word_count;
  const summaryWordCount = statistics.summary_word_count;

  const originalCharCount = statistics.original_char_count;
  const summaryCharCount = statistics.summary_char_count;

  const reduction = statistics.reduction;
  const contentBasedScore = statistics.content_based_score;

  wordCountElement.querySelector(".number li:nth-child(1)").textContent =
    originalWordCount;
  wordCountElement.querySelector(".number li:nth-child(3)").textContent =
    summaryWordCount;
  wordCountElement.dataset.value = originalWordCount;

  characterCountElement.querySelector(".number li:nth-child(1)").textContent =
    originalCharCount;
  characterCountElement.querySelector(".number li:nth-child(3)").textContent =
    summaryCharCount;
  characterCountElement.dataset.value = originalCharCount;

  reductionElement.querySelector(
    "p"
  ).textContent = `Content Score: ${contentBasedScore.toFixed(2)}%`;
  reductionElement.dataset.value = reduction.toFixed(2);
}

//dowload button
const downloadButton = document.getElementById("download-button");
const outputDiv = document.getElementById("summary-output");

downloadButton.addEventListener("click", () => {
  const docContent = outputDiv.outerHTML;
  const blob = new Blob([docContent], {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });

  const url = window.URL.createObjectURL(blob);

  const downloadLink = document.createElement("a");
  downloadLink.href = url;
  downloadLink.download = "summary.docx";

  downloadLink.click();

  window.URL.revokeObjectURL(url);
  downloadLink.remove();
});

//copy button
const copyButton = document.getElementById("copy-button");

copyButton.addEventListener("click", () => {
  const textToCopy = outputDiv.innerText;

  const copyTextArea = document.createElement("textarea");
  copyTextArea.value = textToCopy;

  document.body.appendChild(copyTextArea);

  copyTextArea.select();

  try {
    navigator.clipboard.writeText(textToCopy);
    alert("Text copied successfully!");
  } catch (err) {
    document.execCommand("copy");
    alert("Please select the copied text and press Ctrl+C or Cmd+C to copy.");
  }

  document.body.removeChild(copyTextArea);
});
