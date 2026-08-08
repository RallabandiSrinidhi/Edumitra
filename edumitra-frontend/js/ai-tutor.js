document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      // Display User Message
      appendMessage("You", message, "rgba(255, 255, 255, 0.3)");
      chatInput.value = "";

      // Simulate AI Tutor Response
      setTimeout(() => {
        appendMessage(
          "AI Tutor",
          "Great question! I'm here to help you master this concept step by step.",
          "var(--accent-color)"
        );
      }, 600);
    });
  }

  function appendMessage(sender, text, bgColor) {
    const msgDiv = document.createElement("div");
    msgDiv.style.background = bgColor;
    msgDiv.style.padding = "8px 12px";
    msgDiv.style.borderRadius = "8px";
    msgDiv.style.marginBottom = "8px";
    msgDiv.style.fontSize = "0.9rem";
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});