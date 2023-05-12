import subprocess
import openai
from getpass import getpass
import ast
import sys
import re

# Initialize the OpenAI API with your secret key
openai.api_key = getpass(prompt="Enter your OpenAI API key: ")

def generate_code(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content']

def validate_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        return False

def execute_code(code):
    try:
        output = subprocess.check_output(['python', '-c', code], stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode()
        print(f"An error occurred while executing the code: {error_message}")
        match = re.search(r"No module named '([^']*)'", error_message)
        if match:
            missing_module_name = match.group(1)
            print(f"Module {missing_module_name} is missing.")
            approval = input(f"Do you approve installation of this module? (yes/no): ")
            if approval.lower() == "yes":
                install_missing_module(missing_module_name)
                return execute_code(code)  # Retry code execution after installing the module
        else:
            sys.exit(1)

def install_missing_module(module_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def main():
    initial_prompt = input("Please enter your initial request: ")
    code = generate_code(initial_prompt)

    print("Generated Code:")
    print("----------------")
    print(code)
    print("----------------")

    if not validate_code(code):
        print("Code validation failed.")
        sys.exit(1)

    approval = input("Do you approve execution of this code? (yes/no): ")

    if approval.lower() == "yes":
        result = execute_code(code)
        print('Output:', result.decode())
    else:
        print("Execution cancelled.")

if __name__ == "__main__":
    main()
