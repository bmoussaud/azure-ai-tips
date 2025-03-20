#https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistant
from openai import AzureOpenAI
import os

#load environment variables from the .env file
from dotenv import load_dotenv
import time
from openai import AzureOpenAI
import logging
import time

logging.basicConfig(level=logging.INFO)
load_dotenv()


class AssistantClient:
    
    def chat(self, prompt:str) -> str:
      # Create a new client
      # This will create a new client with the endpoint and API key from the environment variables
      # Make sure to set the AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables
      client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key= os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-05-01-preview",
      )

      # Create a new assistant
      # This will create a new assistant with the name "Financial Analyst Assistant"
      assistant = client.beta.assistants.create(
        name="Financial Analyst Assistant",
        instructions="You are an expert in pets. Use your knowledge base to answer questions about cats and dogs.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
      )
      logging.info(assistant.model_dump_json(indent=2))

      # Create a vector store called "Financial Statements"
      vector_store = client.vector_stores.create(name="pets")
      logging.info(vector_store.id)
      logging.info(vector_store.name)
      
      # Ready the files for upload to OpenAI
      file_paths = ["mydirectory/cats.txt", "mydirectory/dogs.txt"]
      file_streams = [open(path, "rb") for path in file_paths]
      logging.info(file_streams.__len__())
      
      # Use the upload and poll SDK helper to upload the files, add them to the vector store,
      # and poll the status of the file batch for completion.
      file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
      )
      
      # You can logging.info the status and the file counts of the batch to see the result of this operation.
      logging.info(file_batch.status)
      logging.info(file_batch.file_counts)

      # update the assistant to use the vector store
      # This will add the vector store to the assistant's tool resources.
      assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
      )

      logging.info(assistant.model_dump_json(indent=2))

      # Upload the user provided file to OpenAI
      message_file = client.files.create(
        file=open("mydirectory/pets.pdf", "rb"), purpose="assistants"
      )
      
      # Create a thread and attach the file to the message
      thread = client.beta.threads.create(
        messages=[
          {
            "role": "user",
            "content": prompt,
            # Attach the new file to the message.
            "attachments": [
              { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
            ],
          }
        ]
      )
      
      # The thread now has a vector store with that file in its tool resources.
      logging.info(thread.tool_resources.file_search)
      logging.info(thread.model_dump_json(indent=2))
      logging.info("Thread ID %s",thread.id)

      run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        #instructions="New instructions" #You can optionally provide new instructions but these will override the default instructions
      )

      # Retrieve the status of the run
      run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
      )

      start_time = time.time()

      status = run.status
      logging.info(status)

      while status not in ["completed", "cancelled", "expired", "failed"]:
          time.sleep(5)
          run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
          logging.info("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
          status = run.status
          logging.info(f'Status: {status}')
          #clear_output(wait=True)

      # logging.info the final status
      messages = client.beta.threads.messages.list(
        thread_id=thread.id
      ) 

      logging.info(f'Status: {status}')
      logging.info("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
      logging.info(messages.model_dump_json(indent=2))
      # Extract the answer from the messages
      for message in messages:
          if message.role == "assistant":
            logging.info(f"Assistant's response: {message.content}")
            for content in message.content:
              logging.info(content)
            return "X"

if __name__ == "__main__":
    promt = "Give me information about cats and dogs"
    assistant = AssistantClient()
    assistant.chat(prompt=promt)