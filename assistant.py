import os
from openai import OpenAI
from database import retriever

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

assistant = client.beta.assistants.create(
   name='Chat with a custom retriever',
   instructions='You will search for relevant information via retriever and answer questions based on retrieved information.',
   tools=[
     {
       'type': 'function',
       'function': {
         'name': 'CustomRetriever',
         'description': 'Retrieve relevant information from provided documents.',
         'parameters': {
             'type': 'object',
             'properties': {'query': {'type': 'string', 'description': 'The user query'}},
             'required': ['query']
         },
       }
     }
   ],
   model=os.environ.get("ASSISTANT_MODEL", "gpt-4o"),
)

def process_query(query):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    print(f"run.status: {run.status}")
    print(f"run.last_error: {run.last_error}")

    if run.status == 'requires_action':
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == 'CustomRetriever':
                search_res = retriever.get_relevant_documents(query)
                # pages = [res.page_content for res in search_res]
                # print(pages)
                tool_outputs.append({
                    'tool_call_id': tool_call.id,
                    'output': ('\n\n').join([res.page_content for res in search_res])
                })

        client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    result = None
    for m in messages:
        text = m.content[0].text.value
        if m.role == "assistant":
            result = text

    return result
