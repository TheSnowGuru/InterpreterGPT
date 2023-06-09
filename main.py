import subprocess
import openai
from dotenv import load_dotenv
import ast
import sys
import re
import os

# Load the OpenAI API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate code using GPT-3.5-turbo
def generate_code(prompt):
    # Create a chat completion with the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional full stack developer."},
            {"role": "user", "content": prompt},
        ]
    )
    # Return the content of the response
    return response['choices'][0]['message']['content']

# Function to validate generated code
def validate_code(code):
    try:
        # Parse the code using ast.parse to validate its syntax
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        if not fix_code(code, e):
            return False
        return validate_code(code)

"""
Given a piece of code and an error message, this function extracts the line number from the error message,
constructs a prompt for ChatGPT with the code and the error message, sends the prompt to ChatGPT, and extracts
the fixed code from the response. It then checks if the fixed code is valid by compiling it, and returns the
fixed code if it is valid, or False otherwise.
:param code: A string representing the code to be fixed.
:param error: An error message indicating the error in the code.
:return: Either a string representing the fixed code, or False.
"""
def fix_code(code, error):
    # Extract line number from error message
    line_num = int(re.search(r"line (\d+)", str(error)).group(1))

    # Construct prompt for ChatGPT
    prompt = f"Fix the error in line {line_num}: {error}\nCode:\n{code}"

    # Send prompt to ChatGPT
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.8,
    )

    # Extract fixed code from response
    fixed_code = response.choices[0].text.strip()

    # Check if the fixed code is valid
    try:
        compile(fixed_code, "<string>", "exec")
    except SyntaxError:
        return False

    # Return fixed code
    return fixed_code



# Function to execute the generated code
def execute_code(file_name):
    try:
        # Execute the code with subprocess.check_output
        output = subprocess.check_output([sys.executable, file_name], stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode()
        print(f"An error occurred while executing the code: {error_message}")
        sys.exit(1)

# Function to create a Python file and write the generated code to it
def create_and_run_file(code):
    file_name = input("Enter the name of the Python file you'd like to create (e.g., script.py): ")
    with open(file_name, 'w') as f:
        f.write(code)
    print(f"Created file '{file_name}'")
    return file_name

# Main function
def main():
    # Print the contents of the current directory
    print("Current directory contents:")
    for file_name in os.listdir():
        print(f"  {file_name}")
    
    # Ask the user for their initial prompt
    initial_prompt = input("Please enter your initial request for the script to create and run: ")
    
    # Generate the code
    code = generate_code(initial_prompt)

    # Print the generated code
    print("Generated Code:")
    print("----------------")
    print(code)
    print("----------------")

    # Validate the generated code
    if not validate_code(code):
        print("Code validation failed.")
        sys.exit(1)

    # Ask the user for approval to execute the code
    approval = input("Do you approve execution of this code? (yes/no): ")

    if approval.lower() == "yes":
        # Create a file with the generated code
        file_name = create_and_run_file(code)
        # Execute the generated code
        result = execute_code(file_name)
        # Print the output of the code execution
        print('Output:', result.decode())
    else:
        print("Execution cancelled.")

# Run the main function
if __name__ == "__main__":
    main()
