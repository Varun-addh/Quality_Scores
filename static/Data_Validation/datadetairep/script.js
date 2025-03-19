let isDragging = false;
let currentX;
let currentY;
let initialX;
let initialY;
let xOffset = 0;
let yOffset = 0;
 
const assistant = document.createElement("div");
assistant.id = "ai-assistant";
assistant.innerHTML = `
  <div class="ai-icon">🤖</div>
  <div class="ai-chat-container">
    <div class="ai-chat-header">
      <h3>Data Quality Assistant</h3>
      <button class="close-chat">&times;</button>
    </div>
    <div class="ai-messages"></div>
    <div class="ai-input-container">
      <input type="text" placeholder="Ask about data quality..." class="ai-input">
      <button class="ai-send">Send</button>
    </div>
  </div>
`;
 
// Add to body
document.body.appendChild(assistant);
 
// Drag functionality
assistant.addEventListener("mousedown", dragStart);
document.addEventListener("mousemove", drag);
document.addEventListener("mouseup", dragEnd);
 
// Event listeners
document.querySelector(".ai-icon").addEventListener("click", toggleChat);
document.querySelector(".close-chat").addEventListener("click", toggleChat);
document.querySelector(".ai-send").addEventListener("click", handleQuery);
document.querySelector(".ai-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") handleQuery();
});
 
function dragStart(e) {
  initialX = e.clientX - xOffset;
  initialY = e.clientY - yOffset;
 
  if (e.target === assistant) {
    isDragging = true;
  }
}
 
function drag(e) {
  if (isDragging) {
    e.preventDefault();
    currentX = e.clientX - initialX;
    currentY = e.clientY - initialY;
   
    xOffset = currentX;
    yOffset = currentY;
   
    setTranslate(currentX, currentY, assistant);
  }
}
 
function setTranslate(xPos, yPos, el) {
  el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
}
 
function dragEnd() {
  initialX = currentX;
  initialY = currentY;
  isDragging = false;
}
 
function toggleChat() {
  assistant.classList.toggle("chat-open");
}
 
async function handleQuery() {
  const input = document.querySelector(".ai-input");
  const message = input.value.trim();
  if (!message) return;
 
  addMessage(message, "user");
  input.value = "";
 
  // Add your AI API integration here
  const response = await mockAIResponse(message);
  addMessage(response, "ai");
}
 
function addMessage(content, sender) {
  const messages = document.querySelector(".ai-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}`;
  messageDiv.textContent = content;
  messages.appendChild(messageDiv);
  messages.scrollTop = messages.scrollHeight;
}

import { GoogleGenerativeAI } from "https://cdn.skypack.dev/@google/generative-ai";

async function mockAIResponse(query) {
    const apiKey = "AIzaSyDy1YrIYfclhWv0NV2Xc48xNOdC1gEbh9s";
    const genAI = new GoogleGenerativeAI(apiKey);
   
    const model = genAI.getGenerativeModel({
      model: "gemini-2.0-flash-exp",
    });

    const generationConfig = {
      temperature: 0.7,
      topP: 0.95,
      topK: 64,
      maxOutputTokens: 65536,
      responseMimeType: "text/plain",
    };
   
    const chatSession = model.startChat({
      generationConfig,
      history: [],
    });
   
    const result = await chatSession.sendMessage(query);
    console.log(result.response.text());
    return result.response.text(); // Ensure this returns the AI response properly
  }