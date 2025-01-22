## Step-by-Step Guide for Challenge 3: Cryptography (ROT13 decryption)

---

### Step 1: Understand ROT13

ROT13 is a simple substitution cipher that shifts each letter in the alphabet by 13 places. It works only for alphabetic
characters (ignoring non-alphabetic characters). For example:

- `A ↔ N`
- `B ↔ O`
- `Z ↔ M`

This encryption is symmetric, meaning encrypting or decrypting is the same operation.

---

### Step 2: Examine the Encrypted Message

The encrypted message provided in the challenge is:  
`GUVF_VF_GUR_SYNT`

---

### Step 3: Use a ROT13 Decoder

You can use Python's `codecs` module or a quick online decoder. Here's how to decode it manually:

#### Option 1: Write a Python Script

```python
import codecs

# Encrypted message
encrypted_message = "GUVF_VF_GUR_SYNT"

# Decrypt using ROT13
decrypted_message = codecs.decode(encrypted_message, 'rot_13')
print("Decrypted Message:", decrypted_message)
```

#### Option 2: Decode Online

Many online tools are available. Simply search for "ROT13 decoder" and paste the encrypted text into the tool.

---

### Step 4: Obtain the Decrypted Message

Running the script or using a decoder, you'll get:
`THIS_IS_THE_FLAG`

---

### Step 5: Submit the Decrypted Message

Return to the challenge's web interface, enter `THIS_IS_THE_FLAG` into the input field for the decrypted message, and
submit. If correct, the server will return the flag.

---
