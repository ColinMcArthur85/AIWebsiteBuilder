document.getElementById("generate-btn").addEventListener("click", () => {
  const prompt = document.getElementById("user-input").value;
  const loadingElement = document.getElementById("loading");
  const codeElement = document.getElementById("generated-code");

  // Show loading message
  loadingElement.style.display = "block";
  codeElement.textContent = ""; // Clear the previous generated code

  fetch("http://127.0.0.1:5000/generate_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt: prompt }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Hide loading message
      loadingElement.style.display = "none";

      if (data.code) {
        codeElement.textContent = data.code;
        // Re-run Prism syntax highlighting
        Prism.highlightElement(codeElement);
      } else {
        alert("Error: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while generating the code.");
      // Hide loading message in case of error
      loadingElement.style.display = "none";
    });
});

document.getElementById("clear-prompt").addEventListener("click", () => {
  document.getElementById("user-input").value = "";
});

document.getElementById("copy-code").addEventListener("click", () => {
  const codeElement = document.getElementById("generated-code");
  const code = codeElement.textContent;

  navigator.clipboard.writeText(code).then(
    () => {
      alert("Code copied to clipboard!");
    },
    (err) => {
      console.error("Error copying code to clipboard: ", err);
      alert("Failed to copy code to clipboard.");
    }
  );
});

document.getElementById("upload-btn").addEventListener("click", () => {
  const fileInput = document.getElementById("image-upload");
  const file = fileInput.files[0];
  const loadingElement = document.getElementById("loading");
  const codeElement = document.getElementById("generated-code");

  if (file) {
    const formData = new FormData();
    formData.append("image", file);

    // Show loading message
    loadingElement.style.display = "block";
    codeElement.textContent = ""; // Clear the previous generated code

    fetch("http://127.0.0.1:5000/upload_image", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loading message
        loadingElement.style.display = "none";

        if (data.code) {
          codeElement.textContent = data.code;
          // Re-run Prism syntax highlighting
          Prism.highlightElement(codeElement);
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while uploading the image.");
        // Hide loading message in case of error
        loadingElement.style.display = "none";
      });
  } else {
    alert("Please select an image to upload.");
  }
});
