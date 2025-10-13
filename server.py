# main.py
from fastapi import FastAPI, BackgroundTasks
import subprocess
import os, sys
import subprocess, os, datetime, psutil
from fastapi.middleware.cors import CORSMiddleware

TARGET_SCRIPTS = ["visit_meet_with_audio.py", "gemini_audio_only_cable.py"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <— Allow every domain
    allow_credentials=True,
    allow_methods=["*"],        # <— Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],        # <— Allow all headers
)

@app.get("/health")
def health():
    return {"status": "ok"}

def kill_existing_processes(script_name: str):
    """Find and kill any running PowerShell or Python processes executing the target script."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""
            if any(script_name.lower() in cmdline for script_name in TARGET_SCRIPTS):
                print(f"Terminating PID {proc.pid}: {cmdline}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def run_powershell_script(script_name: str, meet_url: str = None):
    """Run a Python script via PowerShell so Chrome can open in GUI session."""
    if meet_url:
        command = f'powershell -ExecutionPolicy Bypass -NoExit -Command "python {script_name} --link {meet_url}"'
    else:
        command = f'powershell -ExecutionPolicy Bypass -NoExit -Command "python {script_name}"'

    subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print(f"Started PowerShell for {script_name}")

@app.post("/join-meeting")
def join_meeting(payload: dict, background_tasks: BackgroundTasks):
    meet_url = payload.get("meetUrl")
    print("Received:", payload)

    background_tasks.add_task(kill_existing_processes, "visit_meet_with_audio.py")
    background_tasks.add_task(kill_existing_processes, "gemini_audio_only_cable.py")

    background_tasks.add_task(run_powershell_script, "visit_meet_with_audio.py", meet_url)
    background_tasks.add_task(run_powershell_script, "gemini_audio_only_cable.py")

    return {"status": "joining", "meeting_url": meet_url}
