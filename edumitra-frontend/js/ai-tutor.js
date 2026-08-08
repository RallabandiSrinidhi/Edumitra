document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  // Live Backend Address
  const API_URL = "https://edumitra-backend-cado.onrender.com";

  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      // Display User Message
      appendMessage("You", message, "rgba(255, 255, 255, 0.3)");
      chatInput.value = "";

      try {
        // Fetch AI response from your live backend
        // Fetch AI response from your live backend
        const response = await fetch(`${API_URL}/api/v1/tutor/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_query: message,
            current_topic: "Python Fundamentals",
            chat_history: []
          }),
        });

        const data = await response.json();

        // Display AI Tutor Response from API
        appendMessage(
          "AI Tutor",
          data.response || data.reply || "I received your message!",
          "var(--accent-color)"
        );
      } catch (error) {
        console.error("Error communicating with backend:", error);
        appendMessage(
          "System",
          "Error reaching backend server. Please try again later.",
          "rgba(255, 0, 0, 0.3)"
        );
      }
    });
  }

  function appendMessage(sender, text, bgColor) {
    const msgDiv = document.createElement("div");
    msgDiv.style.background = bgColor;
    msgDiv.style.padding = "8px 12px";
    msgDiv.style.borderRadius = "8px";
    msgDiv.style.marginBottom = "8px";
    msgDiv.style.fontSize = "0.9rem";
    
    // Parse Markdown text into clean HTML
    const formattedContent = typeof marked !== "undefined" ? marked.parse(text) : text;
    
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${formattedContent}`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});