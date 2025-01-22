import os
import random
from os import mkdir

flag = b"KEY{i_tES_TYU564678IUY^&*(I_E%$rf}"

if not os.path.exists("assets/bin"):
    mkdir("assets/bin")

when = random.randint(0, 100)

for _ in range(100):
    # Generate random data
    random_data_before = os.urandom(10000)
    random_data_after = os.urandom(6000)

    # Combine random data and flag
    if when == _:
        print(f"Flag is in C3_{_}.bin")
        binary_content = random_data_before + flag + random_data_after
    else:
        binary_content = random_data_before + random_data_after
    with open(f"assets/bin/C3_{_}.bin", "wb") as f:
        f.write(binary_content)
