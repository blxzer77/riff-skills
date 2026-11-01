import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

export async function suggestBooks(prompt: string): Promise<string> {
  const msg = await client.messages.create({
    model: process.env.LLM_MODEL ?? "claude-sonnet-5-5",
    max_tokens: 400,
    messages: [{ role: "user", content: prompt }],
  });
  return msg.content[0].type === "text" ? msg.content[0].text : "";
}
