
<div align="center">


<center><a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Bitcount+Prop+Single&size=40&duration=4000&pause=200&width=435&lines=C1ZX+Cipher+Tool;C1ZX+Cipher+Tool" alt="Typing SVG" /></a></center>

### A Professional Dual-Table Unicode Substitution Cipher

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/Version-2.0.1-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange?style=for-the-badge)

Developed by **Axxo | The NULL**

A deterministic two-table Unicode substitution cipher built with extensive validation, integrity verification, automated testing, and reversible encryption.

</div>
<div></div>
---

# Overview

- C1ZX is a Unicode-based substitution cipher that encrypts printable ASCII characters using two independent substitution tables.

- Unlike a traditional monoalphabetic substitution cipher, C1ZX alternates between two completely separate lookup tables depending on the character index.

- Even indexed characters use one table.

- Odd indexed characters use another.

- This significantly reduces simple repetition patterns while maintaining deterministic and fully reversible encryption.

---

# Features

- 🔒 Dual-table substitution cipher
- 🌍 Unicode symbol encryption
- 🔄 Fully reversible encryption
- 🧪 Built-in automated self-testing
- ✅ Extensive validation before startup
- ⚡ O(n) encryption and decryption
- 📦 Single-file implementation
- 🖥 Terminal Unicode compatibility detection
- 🧩 Immutable cipher configuration
- 📚 Well documented source code

---

# Architecture

```

Program
│
├── Constants
├── Unicode Symbol Pool
├── Validation System
├── Table Generator
├── Reverse Table Builder
├── Cipher Engine
├── Self Tests
├── Terminal Compatibility
├── User Interface
└── Main Entry Point

```

---

# Cryptographic Design

- C1ZX uses two completely independent substitution tables.

```

Index 0 → TABLE_01
Index 1 → TABLE_02
Index 2 → TABLE_01
Index 3 → TABLE_02
...

```

Example

```

Plaintext

HELLO

↓

H → TABLE_01
E → TABLE_02
L → TABLE_01
L → TABLE_02
O → TABLE_01

↓

Unicode Ciphertext

```

- Each table owns its own exclusive Unicode symbol pool.

- No encrypted symbol exists in both tables.

---

# Initialization Sequence

- Before encryption is possible the application performs:

```

Validate Unicode Symbols
        │
        ▼
Generate TABLE_01
        │
        ▼
Generate TABLE_02
        │
        ▼
Validate Tables
        │
        ▼
Build Reverse Tables
        │
        ▼
Validate Reverse Tables
        │
        ▼
Run Self Tests
        │
        ▼
Ready

```

- If any validation fails, the application exits immediately.

---

# Self Tests

- Every launch automatically performs comprehensive testing.

- Included tests:

	- Supported character round-trip
	- Entire character set verification
	- Empty string handling
	- Random string encryption
	- Long text encryption
	- Unicode passthrough
	- Whitespace preservation
	- Control character passthrough
	- Reverse table integrity
	- Alternating parity verification
	- Symbol overlap detection

Only after every test passes does the program become available.

---

# 📂 Project Structure

```

.
├── main.py
├── LICENSE
└── README.md

```

---

# Installation

Clone the repository

```bash
git clone https://github.com/axxodeveloper/C1ZX.git
```

Enter the project

```bash
cd C1ZX
```

Run the application

```bash
python main.py
```

---

# Requirements

- Python 3.9+
- UTF-8 compatible terminal

- No external dependencies are required.

- Only Python's standard library is used.

---

#  Main Menu

```

[1] Encrypt Text

[2] Decrypt Text

[3] About

[0] Exit

```

---

# Encryption Workflow

```

Plaintext

↓

Character Position

↓

Even?
│
├── Yes → TABLE_01
│
└── No → TABLE_02

↓

Unicode Ciphertext

```

---

# Decryption Workflow

```

Ciphertext

↓

Character Position

↓

Even?
│
├── Yes → REV_TABLE_01
│
└── No → REV_TABLE_02

↓

Recovered Plaintext

```

---

# Performance

| Operation | Complexity |
|------------|-----------|
| Encryption | O(n) |
| Decryption | O(n) |
| Table Lookup | O(1) |
| Initialization | O(k) |

- Where **n** is the text length.

---

# Validation System

Before startup C1ZX verifies:

- Unique Unicode symbols
- No duplicate mappings
- Complete character coverage
- Exclusive symbol pools
- Reverse lookup correctness
- Table integrity
- Mapping consistency

This prevents corrupted cipher tables.

---

# Unicode Support

- C1ZX automatically checks terminal compatibility.

- If Unicode support is unavailable, a warning is displayed before continuing.

- The encryption still functions correctly even if the terminal cannot display the encrypted symbols properly.

---

# Supported Characters

- The cipher currently supports:

	- Uppercase letters
	- Lowercase letters
	- Numbers
	- ASCII punctuation
	- Space character

Unsupported Unicode characters pass through unchanged.

---

# ⚠ Security Notice

- C1ZX is intended as an educational cryptographic project demonstrating deterministic dual-table substitution.

 - It is a replacement for modern cryptographic standards such as:

	- AES
	- ChaCha20
	- RSA
	- ECC

- Sensitive or production data should always be protected using cryptographic libraries and industry-standard algorithms.
- For that purposes you can use this tool.

---

#  License

Distributed under the MIT License.

See **LICENSE** for more information.

---

#  Author

**Axxo | The NULL**

Version **2.0.1**

---

<div align="center">

Made with ❤️ using Python

**C1ZX Cipher Tool**

</div>
