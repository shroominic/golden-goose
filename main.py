import asyncio
from asyncio import subprocess
import os
import shlex
from crypto import encode_npub, init_identity
from nostr import stream_nostr_messages, reply_to_message
from ai import generate_ai_response, PROMPT
from dotenv import load_dotenv

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
AGENT_CLI = os.getenv("AGENT_CLI", "echo 'No agent configured.'")

print(f"Bot started with identity: {encode_npub(pubkey)}")


def activation_condition(message: dict) -> bool:
    return (
        message["content"].startswith(activation_cmd)
        or encode_npub(pubkey) in message["content"]
    )


async def run_agent(task: str) -> str:
    cmd = (
        f"{AGENT_CLI} {shlex.quote(task)}"
        "Do not do any changes to the underlying system."
        "You can interact with github using the gh cli."
        "Make sure to publish what i want on github and give me the link if applicable."
    )
    print(f"Running agent command: {cmd}")

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    output = ""
    if stdout:
        output += f"Output:\n{stdout.decode()}\n"
    if stderr:
        output += f"Errors:\n{stderr.decode()}\n"

    print(f"Agent result: {output}")

    return output.strip()


async def main():
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

            agent_result = await run_agent(content)

            messages = [
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": f"User Request: {content}\n\nAgent Execution Result:\n{agent_result}\n\nPlease formulate a response to the user based on this result.",
                },
            ]

            response = await generate_ai_response(messages)

            await reply_to_message(
                relays,
                (privkey, pubkey),
                message,
                response,
            )


if __name__ == "__main__":
    asyncio.run(main())
