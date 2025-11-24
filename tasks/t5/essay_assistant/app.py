import uvicorn
from aidial_client import AsyncDial

from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

SYSTEM_PROMPT = """You are an essay-focused assistant. Respond to every request by writing a **short essay** of up to 300 tokens.

**Structure:**
- Clear introduction with thesis
- Body paragraphs with supporting points
- Concise conclusion

**Rules:**
- Always write in essay format regardless of topic
- Keep responses analytical and structured
- Use formal, academic tone
- Include specific examples when relevant
- Maintain logical flow between paragraphs
"""


class EssayAssistantApplication(ChatCompletion):


    async def chat_completion(
            self, request: Request, response: Response
    ) -> None:

        client: AsyncDial = AsyncDial(base_url="http://localhost:8080", api_key="dial_api_key", api_version="2025-01-01-preview")

        with response.create_single_choice() as choice:
            chunks = await client.chat.completions.create(deployment_name="gpt-4o", stream=True,
                                                          messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.messages[-1].content }])
            async for chunk in chunks:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta  and delta.content:
                        choice.append_content(delta.content)

        #TODO:
        # 1. Create self-closable choice where we return response (you can find this code in echo app)
        #    (you need to call `response.create_single_choice()`
        # 2. Assign to `chunks` the call to client chat completions (await client.chat.completions.create) with such parameters:
        #   - deployment_name="gpt-4o"
        #   - stream=True
        #   - messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.messages[-1].content }]
        # 3. Make async loop through `chunks` (async for chunk in chunks) and:
        #   -> if `chunk` has `choices` (chunk.choices):
        #   -> Get its `delta` (chunk.choices[0].delta) and assign to `delta`
        #   -> if delta is not None and has `content` (delta.content):
        #   -> Append delta content to choice (choice.append_content(delta.content))


app: DIALApp = DIALApp()
app.add_chat_completion(deployment_name="essay-assistant", impl=EssayAssistantApplication())

if __name__ == "__main__":
    uvicorn.run(app, port=5025, host="0.0.0.0")