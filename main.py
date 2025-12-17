import asyncio
import os
from crypto import encode_npub, init_identity, encode_note_id
from nostr import stream_nostr_messages, reply_to_message
from ai import generate_ai_response
from dotenv import load_dotenv
from database import create_db_and_tables
from agent_task import process_task

load_dotenv()

relays = [
    "wss://relay.damus.io",
    "wss://relay.primal.net",
    "wss://pyramid.fiatjaf.com/",
    "wss://relay.nostr.band/",
    "wss://nos.lol",
]

nsec = os.getenv("NSEC")
privkey, pubkey = init_identity(nsec)
activation_cmd = os.getenv("ACTIVATION_CMD", "!robot")

print(f"Bot started with identity: {encode_npub(pubkey)}")


def activation_condition(message: dict) -> bool:
    return (
        message["content"].startswith(activation_cmd)
        or encode_npub(pubkey) in message["content"]
    )


async def main():
    create_db_and_tables()
    async for message in stream_nostr_messages(
        relays=relays, filters=[{"kinds": [1]}], since_seconds=1
    ):
        if activation_condition(message):
            print(f"{message} triggered activation")

            content = message["content"].replace(activation_cmd, "").strip()
            # Basic cleanup of the mention if present (not perfect but helpful)
            npub = encode_npub(pubkey)
            if npub in content:
                content = content.replace(npub, "").strip()
            if not content:
                content = "Hello"  # Default if empty

            try:
                note_id = encode_note_id(message["id"])
                sender_npub = encode_npub(message["pubkey"])
                
                agent_result = await process_task(note_id, sender_npub, content)

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant. Summarize what the agent did based on the result below. "
                            "Give a short answer for the user derived from the agent's output. "
                            "Include relevant links and formulate it as an answer to the user's request."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Agent Execution Result:\n{agent_result}",
                    },
                ]

                response = await generate_ai_response(messages)

                await reply_to_message(
                    relays,
                    (privkey, pubkey),
                    message,
                    response,
                )
            except Exception as e:
                print(f"Error processing message: {e}")


if __name__ == "__main__":
    asyncio.run(main())
