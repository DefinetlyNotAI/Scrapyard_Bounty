### Model Answer Guide for Challenge 3: Reverse Engineering

#### Challenge Description

In this challenge, participants are required to locate the binary file containing the hidden flag.
Which is one of 100 binary files to find a hidden flag. The flag format is `KEY{xxxx}`.

#### Steps to Solve the Challenge

1. **Download the Binary Files:**
    - The binary files are provided for this challenge. Download all 100 files from the challenge page.

2. **Automate the Analysis:**
    - Create a script to automate the analysis of each binary file to find the correct one containing the flag.

3. **Analyze Each Binary File:**
    - Load each binary file into notepad and start examining the code.
        - Use a custom script you can develop to automate the analysis of each binary file.

4. **Extract the Flag:**
    - The flag is hardcoded in the binary. Look for string literals or constants that match the flag format `KEY{xxxx}`.

5. **Verify the Flag:**
    - After extracting the flag, verify it by submitting the file, and KEY line number to challenge page.
    - Ensure that the flag matches the required format and is correctly extracted from the binary.

#### Example Solution

1. **Create a Script to Automate the Analysis:**
    - Write a Python script to automate the analysis of each binary file.

```python
import os
import subprocess


def analyze_binary(file_path):
    # Use strings command to extract strings from the binary
    result = subprocess.run(['strings', file_path], capture_output=True, text=True)
    strings_output = result.stdout

    # Check for the flag format in the strings output
    for line in strings_output.split('\n'):
        if 'KEY{' in line:
            return line.strip()
    return None


def main():
    binary_dir = 'path/to/binary/files'
    for file_name in os.listdir(binary_dir):
        file_path = os.path.join(binary_dir, file_name)
        flag = analyze_binary(file_path)
        if flag:
            print(f'Flag found in {file_name}: {flag}')
            break
    else:
        print('Flag not found in any binary file.')


if __name__ == '__main__':
    main()
```

2. **Run the Script:**
    - Execute the script to analyze each binary file and find the one containing the flag.

3. **Extract the Flag:**
    - Get the line where the flag is, use `Ctrl+F` to find the flag of format `KEY{xxxx}`.

By following these steps,
participants can successfully locate the correct binary file
and extract the hidden flag for Challenge 3.
