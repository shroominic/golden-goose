import asyncio
from asyncio import subprocess
import shlex
import os
from database import create_task, get_or_create_user, update_task_result

AGENT_CLI = os.getenv("AGENT_CLI", "echo 'No agent configured.'")

async def run_agent(task: str, custom_instructions: str = "") -> str:
    full_task = task
    if custom_instructions:
        full_task = f"{custom_instructions}\n\nTask: {task}"

    cmd = (
        f"{AGENT_CLI} {shlex.quote(full_task)}"
        # "Do not do any changes to the underlying system."
        # "You can interact with github using the gh cli."
        # "Make sure to publish what i want on github and give me the link if applicable."
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

async def process_task(note_id: str, npub: str, content: str) -> str:
    # 1. Get/Create User and fetch preferences
    user = get_or_create_user(npub)
    
    # 2. Create Task in DB
    task = create_task(note_id, npub, content)
    if not task:
        # Task already exists, might want to return existing result or just empty if processing
        # For now assuming if it exists we skip or re-run. Let's run but maybe log?
        print(f"Task {note_id} already exists.")
    
    # 3. Run Agent
    # Update status to processing? (Optional, skipping for now to keep it simple as requested fields were status/result)
    result = await run_agent(content, user.custom_instructions)
    
    # 4. Update Task with result
    update_task_result(note_id, result, status="completed")
    
    return result
