### Model Answer Guide for Challenge 3: Reverse Engineering with Wireshark

#### Challenge Description

In this challenge, participants are required to locate the
PCAP file containing the hidden flag. The flag format is `KEY{xxxx}`.

#### Steps to Solve the Challenge

1. **Download the PCAP Files:**
    - The PCAP files are provided for this challenge. Download all 100 files from the challenge page.

2. **Automate the Analysis:**
    - Create a script to automate the analysis of each PCAP file to find the correct one containing the flag.

3. **Analyze Each PCAP File:**
    - Use Wireshark or a Python script to analyze each PCAP file.
    - Look for packets containing the flag format `KEY{xxxx}`.

4. **Extract the Flag:**
    - The flag is embedded in one of the packets. Use Wireshark or a script to extract the flag.

5. **Verify the Flag:**
    - After extracting the flag, verify it by submitting the file and the packet number to the challenge page.
    - Ensure that the flag matches the required format and is correctly extracted from the packet.

#### Example Solution

1. **Create a Script to Automate the Analysis:**
    - Write a Python script to automate the analysis of each PCAP file using the `pyshark` library.

```python
import pyshark
import os

def analyze_pcap(file_path):
    cap = pyshark.FileCapture(file_path)
    for packet in cap:
        if 'KEY{' in str(packet):
            return packet
    return None

def main():
    pcap_dir = 'path/to/pcap/files'
    for file_name in os.listdir(pcap_dir):
        file_path = os.path.join(pcap_dir, file_name)
        flag_packet = analyze_pcap(file_path)
        if flag_packet:
            print(f'Flag found in {file_name}: {flag_packet}')
            break
    else:
        print('Flag not found in any PCAP file.')

if __name__ == '__main__':
    main()
```

2. **Run the Script:**
    - Execute the script to analyze each PCAP file and find the one containing the flag.

3. **Extract the Flag:**
    - Use Wireshark or the script to locate the packet containing the flag and extract it.
    - Then get the packet number/line where the flag is, use `Ctrl+F` to find the flag of format `KEY{xxxx}`.

By following these steps, participants can successfully locate the
correct PCAP file and extract the hidden flag for Challenge 3.
