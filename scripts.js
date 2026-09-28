async function sendMessage(text, mode) {
  const res = await fetch("http://localhost:5000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, mode: mode })
  });
  const data = await res.json();
  if (data.error) return "Error: " + data.error;
  return data.reply; // data.prompt_used has the exact prompt, for a "show prompt" panel
}