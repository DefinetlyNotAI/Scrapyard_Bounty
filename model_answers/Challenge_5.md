### Challenge 5: Steganography

#### Objective:

Extract hidden data (Format `KEY{xxxx}`) from an image file using an automated script. First, you must find the correct
JPEG file, then the correct line number.

#### Steps to Solve the Challenge:

1. **Understand the Problem:**
    - You are given 100 JPEG files.
    - One of these files contains a hidden message in the format `KEY{xxxx}`.
    - You need to find the correct file and extract the hidden message.

2. **Requirements:**
    - Python programming language.
    - `pillow` library for image processing.
    - `stepic` or `lsb` library for steganography (depending on the method used).

3. **Setup:**
    - Install the required libraries:
      ```sh
      pip install pillow stepic
      ```

4. **Automated Script:**
    - Create a Python script to automate the process of finding the hidden message.

5. **Script Explanation:**
    - The script will iterate through all the JPEG files.
    - For each file, it will attempt to extract the hidden message.
    - If the message matches the expected format, it will print the message and the file name.

6. **Sample Script:**

```python
import os

def find_hidden_message(directory):
   flag_start = b"KEY{"
   flag_end = b"}"

   for filename in os.listdir(directory):
      if filename.endswith(".jpeg"):
         file_path = os.path.join(directory, filename)
         try:
            with open(file_path, "rb") as image_file:
               image_data = image_file.read()
               start_index = image_data.find(flag_start)
               end_index = image_data.find(flag_end, start_index)
               if start_index != -1 and end_index != -1:
                  hidden_message = image_data[start_index:end_index + len(flag_end)].decode()
                  print(f"Hidden message found in {filename}: {hidden_message}")
                  return
         except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
   director = "assets/images"
   find_hidden_message(director)
```

7. **Run the Script:**
    - Place the script in the same directory as your JPEG files or adjust the `directory` variable to point to the
      correct path.
    - Run the script:
      ```sh
      python find_hidden_message.py
      ```

8. **Verify the Result:**
    - The script will output the file name and the hidden message if found.
    - Ensure the hidden message matches the expected format `KEY{xxxx}`.
    - Then get the line number where the flag is, use `Ctrl+F` to find the flag of format `KEY{xxxx}`.

By following these steps,
you will be able to automate the process of finding the hidden message
in the JPEG files and successfully complete Challenge 5.
