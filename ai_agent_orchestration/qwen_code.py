import subprocess

# --------------------------
# High-level concept you want to turn into an SD prompt
concept = "make a fun waveform animation of a mp3 file using python 3.11"
# --------------------------

# Construct a prompt for the LLM to generate a Stable Diffusion description
prompt = f"""
You are a expert coder. 
do good code for the following project'{concept}'
"""

def run_ollama(prompt_text):
    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2.5:7b-instruct", prompt_text],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

# Generate the SD prompt
sd_prompt = run_ollama(prompt)
print("=== Generated Stable Diffusion Prompt ===")
print(sd_prompt)
