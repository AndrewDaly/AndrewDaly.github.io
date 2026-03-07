import subprocess

# --------------------------
# High-level concept you want to turn into an SD prompt
concept = "A fantasy world, but realistic, with mountains, rivers, and a medieval village at sunrise."
# --------------------------

# Construct a prompt for the LLM to generate a Stable Diffusion description
prompt = f"""
You are a creative prompt writer for a text-to-image AI. 
Turn the following concept into a vivid, highly detailed, photorealistic Stable Diffusion prompt:
'{concept}'
Include details about lighting, environment, composition, and style. 
Make it something that will produce a visually stunning image.
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
