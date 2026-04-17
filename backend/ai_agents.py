import subprocess

def run_agent(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return result.stdout.strip()

    except Exception as e:
        return f"Exception occurred: {str(e)}"


def evaluate_assignment(content):

    if not content or content.strip() == "":
        return 0, "No content provided"

    analysis = run_agent(f"Analyze this assignment:\n{content}")
    grading = run_agent(f"Give a score out of 100 for this assignment:\n{content}")
    feedback = run_agent(f"Write detailed feedback:\n{content}")
    grammar = run_agent(f"Check grammar mistakes:\n{content}")

    final_output = f"""
ANALYSIS:
{analysis}

GRADING:
{grading}

FEEDBACK:
{feedback}

GRAMMAR:
{grammar}
"""

    # TEMP score (we will improve later)
    score = 85

    return score, final_output