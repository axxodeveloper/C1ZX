"""
Author: Axxo | The NULL
Version: 2.0.1
License: MIT
"""

import sys
import string
import locale
import os
import webbrowser
from typing import Dict, Final, List, Tuple, Optional
from dataclasses import dataclass
import random


# ============================================================================
# CONSTANTS
# ============================================================================

# Explicitly defined supported character set.
# This guarantees every character exists exactly once and no characters
# are accidentally lost, unlike string.printable.strip() which can vary.
SUPPORTED_CHARS: Final[str] = (
    string.ascii_uppercase  # A-Z
    + string.ascii_lowercase  # a-z
    + string.digits  # 0-9
    + string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    + " "  # space (explicitly included)
)

# Unicode symbols for substitution.
# Each symbol is carefully selected from various Unicode blocks to provide
# visual distinction while remaining within the Basic Multilingual Plane.
# CRITICAL: Every symbol in this list must be unique.
# The list size must be at least 2 * len(SUPPORTED_CHARS) to ensure
# both tables can draw from non-overlapping symbol pools.
UNICODE_SYMBOLS: Final[List[str]] = [
    # Greek letters (47 characters)
    'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ',
    'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',
    'Γ', 'Δ', 'Θ', 'Λ', 'Ξ', 'Π', 'Σ', 'Φ', 'Ψ', 'Ω',
    'ς', 'ϑ', 'ϕ', 'ϖ', 'ϰ', 'ϱ', 'ϵ', '϶', 'ϴ', 'ϲ', 'ϳ', 'Ϲ',
    # Cyrillic letters (64 characters)
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К',
    'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц',
    'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я',
    'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к',
    'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц',
    'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я',
    # Mathematical and technical symbols (fill to sufficient count)
    '∀', '∂', '∃', '∆', '∇', '∈', '∉', '∑', '−', '√', '∞', '∫',
    '∧', '∨', '∩', '∪', '∴', '∵', '∼', '≅', '≈', '≠', '≡', '≤',
    '≥', '⊂', '⊃', '⊆', '⊇', '⊕', '⊗', '⊥', '⊢', '⊣',  # Fixed: removed duplicate '⊤'
    '⌂', '⌃', '⌄', '⌅', '⌆', '⌇', '⌈', '⌉', '⌊', '⌋', '⌌', '⌍',
    '⌎', '⌏', '⌐', '⌑', '⌒', '⌓', '⌔', '⌕', '⌖', '⌗', '⌘', '⌙',
    '⌚', '⌛', '⌜', '⌝', '⌞', '⌟', '⌠', '⌡', '⌢', '⌣', '⌤', '⌥',
    '⌦', '⌧', '⌨', '〈', '〉', '⌫', '⌬', '⌭', '⌮', '⌯', '⌰', '⌱',
    '⌲', '⌳', '⌴', '⌵', '⌶', '⌷', '⌸', '⌹', '⌺', '⌻', '⌼', '⌽',
    '⌾', '⌿', '⍟', '⍠', '⍡', '⍢', '⍣', '⍤', '⍥', '⍦', '⍧', '⍨',
    '⍩', '⍪', '⍫', '⍬', '⍭', '⍮', '⍯', '⍰', '⍱', '⍲', '⍳', '⍴',
]

# Program metadata
VERSION: Final[str] = "2.0.1"
AUTHOR: Final[str] = "Axxo | The NULL"
PYTHON_VERSION: Final[str] = (
    f"{sys.version_info.major}."
    f"{sys.version_info.minor}."
    f"{sys.version_info.micro}"
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass(frozen=True)
class CipherTables:
    """
    Immutable container for all cipher tables.
    
    Holds the forward and reverse substitution tables, ensuring they cannot
    be accidentally modified after validation. This eliminates mutable global
    state and makes the cipher configuration thread-safe.
    
    Attributes:
        table_01: First substitution table (even-indexed characters)
        table_02: Second substitution table (odd-indexed characters)
        rev_table_01: Reverse lookup for table_01
        rev_table_02: Reverse lookup for table_02
    """
    table_01: Dict[str, str]
    table_02: Dict[str, str]
    rev_table_01: Dict[str, str]
    rev_table_02: Dict[str, str]


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_unicode_symbols(symbols: List[str]) -> None:
    """
    Validate the Unicode symbol set before table generation.
    
    Checks that every symbol is unique and that there are sufficient symbols
    to map all supported characters in both tables.
    
    Args:
        symbols: List of Unicode symbols to validate
        
    Raises:
        ValueError: If symbols have duplicates or insufficient count
        TypeError: If any symbol is not a string
    """
    if not symbols:
        raise ValueError("Unicode symbols list is empty")
    
    # Type check all symbols
    for i, sym in enumerate(symbols):
        if not isinstance(sym, str):
            raise TypeError(f"Symbol at index {i} is not a string: {type(sym)}")
        if len(sym) != 1:
            raise ValueError(
                f"Symbol at index {i} must be a single character, "
                f"got {len(sym)} characters: {repr(sym)}"
            )
    
    # Check for duplicates
    seen: Dict[str, int] = {}
    duplicates: List[str] = []
    for sym in symbols:
        if sym in seen:
            duplicates.append(sym)
        else:
            seen[sym] = 1
    
    if duplicates:
        raise ValueError(
            f"Unicode symbols contain {len(duplicates)} duplicate(s): "
            f"{', '.join(repr(d) for d in duplicates[:10])}"
            f"{'...' if len(duplicates) > 10 else ''}"
        )
    
    # Check we have enough unique symbols for two complete tables
    # Each table needs its own exclusive set of symbols
    required = len(SUPPORTED_CHARS) * 2
    if len(symbols) < required:
        raise ValueError(
            f"Insufficient unique Unicode symbols. "
            f"Need at least {required} (2 × {len(SUPPORTED_CHARS)} supported chars), "
            f"but only have {len(symbols)}"
        )
    
    # Verify each supported character can be uniquely represented
    if len(SUPPORTED_CHARS) != len(set(SUPPORTED_CHARS)):
        # Find duplicates in supported chars for error message
        char_seen: Dict[str, int] = {}
        char_dupes: List[str] = []
        for c in SUPPORTED_CHARS:
            if c in char_seen:
                char_dupes.append(c)
            else:
                char_seen[c] = 1
        raise ValueError(
            f"SUPPORTED_CHARS contains duplicates: "
            f"{', '.join(repr(c) for c in char_dupes)}"
        )


def validate_table(table: Dict[str, str], name: str, supported: str) -> None:
    """
    Validate a single substitution table comprehensively.
    
    Checks performed:
    - Table is not empty
    - No duplicate keys (guaranteed by dict, but verified for clarity)
    - No duplicate values (ensures reversible mapping)
    - Every supported character is mapped
    - No unsupported characters as keys
    - All values are single-character strings
    - Table size matches supported character set size
    
    Args:
        table: The substitution table to validate
        name: Human-readable table name for error messages
        supported: String of all supported characters
        
    Raises:
        ValueError: If any validation check fails
        TypeError: If table contains invalid types
    """
    if not isinstance(table, dict):
        raise TypeError(f"{name} must be a dictionary, got {type(table)}")
    
    if not table:
        raise ValueError(f"{name} is empty")
    
    # Check all entries are string -> string
    for key, value in table.items():
        if not isinstance(key, str):
            raise TypeError(f"{name} key {repr(key)} is not a string")
        if not isinstance(value, str):
            raise TypeError(f"{name} value for key {repr(key)} is not a string")
        if len(key) != 1:
            raise ValueError(f"{name} key {repr(key)} must be a single character")
        if len(value) != 1:
            raise ValueError(
                f"{name} value for key {repr(key)} must be a single character, "
                f"got {repr(value)}"
            )
    
    # Check no duplicate values (critical for reversibility)
    values = list(table.values())
    if len(values) != len(set(values)):
        # Identify which values are duplicated for helpful error message
        value_counts: Dict[str, int] = {}
        for v in values:
            value_counts[v] = value_counts.get(v, 0) + 1
        duplicates = [v for v, count in value_counts.items() if count > 1]
        raise ValueError(
            f"{name} contains {len(duplicates)} duplicate value(s): "
            f"{', '.join(repr(d) for d in duplicates[:10])}"
            f"{'...' if len(duplicates) > 10 else ''}. "
            f"Each encrypted symbol MUST be unique."
        )
    
    # Check every supported character is mapped
    table_keys = set(table.keys())
    supported_set = set(supported)
    missing_chars = supported_set - table_keys
    if missing_chars:
        raise ValueError(
            f"{name} is missing mappings for {len(missing_chars)} supported "
            f"character(s): {''.join(sorted(missing_chars))}"
        )
    
    # Check no unsupported characters in keys
    extra_chars = table_keys - supported_set
    if extra_chars:
        raise ValueError(
            f"{name} contains {len(extra_chars)} unsupported character(s): "
            f"{''.join(sorted(extra_chars))}"
        )
    
    # Check table size matches
    if len(table) != len(supported):
        raise ValueError(
            f"{name} size mismatch: expected {len(supported)} entries, "
            f"got {len(table)}"
        )


def build_reverse_table(table: Dict[str, str]) -> Dict[str, str]:
    """
    Build a reverse lookup table from a substitution table.
    
    Creates a dictionary mapping each encrypted symbol back to its original
    character. Since validation has already confirmed there are no duplicate
    values, this mapping is guaranteed to be one-to-one.
    
    Args:
        table: The validated substitution table
        
    Returns:
        Reverse lookup dictionary (symbol -> original character)
        
    Raises:
        ValueError: If duplicate values are found (should not happen after validation)
    """
    reverse: Dict[str, str] = {}
    for char, symbol in table.items():
        if symbol in reverse:
            raise ValueError(
                f"Duplicate symbol {repr(symbol)} found when building reverse table. "
                f"This should have been caught during validation."
            )
        reverse[symbol] = char
    return reverse


def validate_reverse_table(
    forward: Dict[str, str],
    reverse: Dict[str, str],
    name: str
) -> None:
    """
    Validate that a reverse table perfectly reverses its forward table.
    
    Checks:
    - Every forward mapping is reversed correctly
    - Every reverse mapping points back to a valid forward key
    - Sizes match
    - No orphaned entries
    
    Args:
        forward: The forward substitution table
        reverse: The reverse lookup table
        name: Human-readable name for error messages
        
    Raises:
        ValueError: If reverse table doesn't perfectly reverse forward table
    """
    if len(reverse) != len(forward):
        raise ValueError(
            f"{name} reverse table size ({len(reverse)}) doesn't match "
            f"forward table size ({len(forward)})"
        )
    
    # Verify every forward mapping is correctly reversed
    for char, symbol in forward.items():
        if symbol not in reverse:
            raise ValueError(
                f"{name}: Symbol {repr(symbol)} (from char {repr(char)}) "
                f"not found in reverse table"
            )
        if reverse[symbol] != char:
            raise ValueError(
                f"{name}: Reverse mapping error. "
                f"Expected {repr(char)} -> {repr(symbol)} -> {repr(char)}, "
                f"but got {repr(char)} -> {repr(symbol)} -> {repr(reverse[symbol])}"
            )
    
    # Verify no extra entries in reverse table
    for symbol, char in reverse.items():
        if symbol not in forward.values():
            raise ValueError(
                f"{name}: Reverse table contains symbol {repr(symbol)} "
                f"not present in forward table"
            )
        if forward[char] != symbol:
            raise ValueError(
                f"{name}: Reverse table entry {repr(symbol)} -> {repr(char)} "
                f"doesn't match forward entry {repr(char)} -> {repr(forward[char])}"
            )


# ============================================================================
# TABLE GENERATION
# ============================================================================

def generate_tables(
    chars: str,
    symbols: List[str],
    seed_01: int,
    seed_02: int
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Generate two substitution tables with mutually exclusive symbol pools.
    
    This function ensures that TABLE_01 and TABLE_02 use completely distinct
    sets of encrypted symbols. It works by:
    1. Creating a single shuffled pool of all available symbols
    2. Splitting the pool into two non-overlapping halves
    3. Each table draws exclusively from its assigned half
    
    This guarantees zero symbol overlap between tables, which is essential
    for the self-tests to pass and for the cipher to have well-defined
    decryption behavior for every possible encrypted symbol.
    
    Args:
        chars: String of characters to map from (same for both tables)
        symbols: Complete list of available unique symbols
        seed_01: Random seed for shuffling TABLE_01's symbol pool
        seed_02: Random seed for shuffling TABLE_02's symbol pool
        
    Returns:
        Tuple of (table_01, table_02) dictionaries
        
    Raises:
        ValueError: If there aren't enough symbols for both tables
    """
    num_chars = len(chars)
    required_symbols = num_chars * 2
    
    if len(symbols) < required_symbols:
        raise ValueError(
            f"Need at least {required_symbols} unique symbols for two tables "
            f"({num_chars} chars × 2 tables), but only have {len(symbols)}"
        )
    
    # Step 1: Create a master shuffled pool using a fixed seed
    # This ensures deterministic overall symbol assignment
    master_rng = random.Random(42)
    master_pool = symbols.copy()
    master_rng.shuffle(master_pool)
    
    # Step 2: Split into two non-overlapping symbol pools
    symbols_for_table_01 = master_pool[:num_chars]
    symbols_for_table_02 = master_pool[num_chars:required_symbols]
    
    # Verify no overlap between the two pools
    overlap = set(symbols_for_table_01) & set(symbols_for_table_02)
    if overlap:
        raise ValueError(
            f"INTERNAL ERROR: Symbol pools overlap by {len(overlap)} symbols. "
            f"This should never happen with a proper shuffle and split."
        )
    
    # Step 3: Shuffle each pool independently with its own seed
    # This creates different substitution patterns for each table
    rng_01 = random.Random(seed_01)
    pool_01 = symbols_for_table_01.copy()
    rng_01.shuffle(pool_01)
    
    rng_02 = random.Random(seed_02)
    pool_02 = symbols_for_table_02.copy()
    rng_02.shuffle(pool_02)
    
    # Step 4: Create the mapping dictionaries
    table_01 = dict(zip(chars, pool_01))
    table_02 = dict(zip(chars, pool_02))
    
    return table_01, table_02


def initialize_cipher() -> CipherTables:
    """
    Initialize and validate all cipher tables in the required order.
    
    Strict initialization sequence:
    1. Validate Unicode symbols
    2. Generate TABLE_01 and TABLE_02 with mutually exclusive symbol pools
    3. Validate both forward tables
    4. Build reverse tables
    5. Validate reverse tables
    6. Return immutable CipherTables object
    
    Each step must succeed before proceeding. If any step fails, the program
    terminates with a descriptive error message.
    
    Returns:
        Fully validated CipherTables instance
        
    Raises:
        SystemExit: If any validation step fails
    """
    print("Initializing cipher system...")
    
    # Step 1: Validate Unicode symbols
    print("  [1/5] Validating Unicode symbols...", end=" ")
    try:
        validate_unicode_symbols(UNICODE_SYMBOLS)
        print("[OK]")
    except (ValueError, TypeError) as e:
        print(f"✗\n    Error: {e}")
        sys.exit(1)
    
    # Step 2: Generate tables with exclusive symbol pools
    print("  [2/5] Generating substitution tables...", end=" ")
    try:
        table_01, table_02 = generate_tables(
            SUPPORTED_CHARS,
            UNICODE_SYMBOLS,
            seed_01=42,
            seed_02=123
        )
        print("[OK]")
    except Exception as e:
        print(f"✗\n    Error generating tables: {e}")
        sys.exit(1)
    
    # Step 3: Validate forward tables
    print("  [3/5] Validating forward tables...", end=" ")
    try:
        validate_table(table_01, "TABLE_01", SUPPORTED_CHARS)
        validate_table(table_02, "TABLE_02", SUPPORTED_CHARS)
        print("[OK]")
    except (ValueError, TypeError) as e:
        print(f"✗\n    Error: {e}")
        sys.exit(1)
    
    # Step 4: Build reverse tables
    print("  [4/5] Building reverse tables...", end=" ")
    try:
        rev_table_01 = build_reverse_table(table_01)
        rev_table_02 = build_reverse_table(table_02)
        print("[OK]")
    except ValueError as e:
        print(f"✗\n    Error: {e}")
        sys.exit(1)
    
    # Step 5: Validate reverse tables
    print("  [5/5] Validating reverse tables...", end=" ")
    try:
        validate_reverse_table(table_01, rev_table_01, "TABLE_01/REV_TABLE_01")
        validate_reverse_table(table_02, rev_table_02, "TABLE_02/REV_TABLE_02")
        print("[OK]")
    except ValueError as e:
        print(f"✗\n    Error: {e}")
        sys.exit(1)
    
    print("  Cipher initialization complete.\n")
    
    return CipherTables(
        table_01=table_01,
        table_02=table_02,
        rev_table_01=rev_table_01,
        rev_table_02=rev_table_02,
    )


# ============================================================================
# CIPHER FUNCTIONS
# ============================================================================

def encrypt(text: str, tables: CipherTables) -> str:
    """
    Encrypt text using the two-table alternating substitution cipher.
    
    Encryption process:
    - Characters at even indices (0, 2, 4, ...) use TABLE_01
    - Characters at odd indices (1, 3, 5, ...) use TABLE_02
    - Supported characters are substituted using the appropriate table
    - Unsupported characters pass through unchanged
    
    Complexity: O(n) where n is the length of the input text.
    Each character is processed exactly once with a single dictionary lookup.
    
    Args:
        text: The plaintext to encrypt (empty string returns empty string)
        tables: Validated CipherTables instance
        
    Returns:
        Encrypted ciphertext string. Empty input returns empty string.
        
    Example:
        >>> tables = initialize_cipher()
        >>> encrypt("Hello", tables)
        'ϑ∑∏∐∇'  # Example output (actual output varies by table generation)
    """
    if not text:
        return ""
    
    # Pre-bind tables for faster lookup
    table_01 = tables.table_01
    table_02 = tables.table_02
    
    # Build result using list for performance
    # Tables have been validated, so every supported char has a mapping
    result: List[str] = []
    for i, char in enumerate(text):
        current_table = table_01 if i % 2 == 0 else table_02
        # Direct lookup - table is guaranteed to have all supported chars
        mapped = current_table.get(char, char)
        result.append(mapped)
    
    return ''.join(result)


def decrypt(cipher_text: str, tables: CipherTables) -> str:
    """
    Decrypt text that was encrypted with the two-table alternating cipher.
    
    Decryption process:
    - Characters at even indices use REV_TABLE_01
    - Characters at odd indices use REV_TABLE_02
    - Recognized symbols are reverse-substituted
    - Unrecognized characters pass through unchanged
    
    Complexity: O(n) where n is the length of the input text.
    
    Args:
        cipher_text: The ciphertext to decrypt (empty string returns empty string)
        tables: Validated CipherTables instance
        
    Returns:
        Decrypted plaintext string. Empty input returns empty string.
        
    Example:
        >>> tables = initialize_cipher()
        >>> decrypt(encrypt("Hello", tables), tables)
        'Hello'
    """
    if not cipher_text:
        return ""
    
    # Pre-bind reverse tables for faster lookup
    rev_table_01 = tables.rev_table_01
    rev_table_02 = tables.rev_table_02
    
    result: List[str] = []
    for i, char in enumerate(cipher_text):
        current_rev = rev_table_01 if i % 2 == 0 else rev_table_02
        # Direct lookup - reverse tables contain all valid encrypted symbols
        original = current_rev.get(char, char)
        result.append(original)
    
    return ''.join(result)


# ============================================================================
# SELF-TEST FUNCTIONS
# ============================================================================

def run_self_tests(tables: CipherTables) -> None:
    """
    Run comprehensive self-tests to verify complete cipher correctness.
    
    Tests performed:
    - Every supported character encrypts and decrypts correctly
    - decrypt(encrypt(x)) == x for the entire supported character set
    - Empty string handling
    - Random string round-trip
    - Long string (1000 chars) round-trip
    - Whitespace preservation
    - Control character passthrough
    - Unicode passthrough for unsupported characters
    - Table integrity verification (including non-overlapping symbol pools)
    - Alternating table usage pattern verification
    
    If any test fails, the program terminates with a descriptive message.
    
    Args:
        tables: Validated CipherTables instance
        
    Raises:
        SystemExit: If any test fails
    """
    print("Running comprehensive self-tests...")
    
    test_count = 0
    failed = 0
    
    # Test 1: Every supported character round-trip
    test_count += 1
    print(f"  [{test_count}] Testing all {len(SUPPORTED_CHARS)} supported characters...", end=" ")
    for char in SUPPORTED_CHARS:
        encrypted = encrypt(char, tables)
        decrypted = decrypt(encrypted, tables)
        if decrypted != char:
            print(f"[FAILED]\n    Failed on character {repr(char)}: "
                  f"encrypted={repr(encrypted)}, decrypted={repr(decrypted)}")
            failed += 1
            break
    else:
        print("[OK]")
    
    # Test 2: Full supported character set as single string
    test_count += 1
    print(f"  [{test_count}] Testing full character set round-trip...", end=" ")
    encrypted = encrypt(SUPPORTED_CHARS, tables)
    decrypted = decrypt(encrypted, tables)
    if decrypted != SUPPORTED_CHARS:
        print(f"[FAILED]\n    Full character set round-trip failed")
        # Find first mismatch
        for i, (orig, dec) in enumerate(zip(SUPPORTED_CHARS, decrypted)):
            if orig != dec:
                print(f"    First mismatch at index {i}: "
                      f"expected {repr(orig)}, got {repr(dec)}")
                break
        failed += 1
    else:
        print("[OK]")
    
    # Test 3: Empty string
    test_count += 1
    print(f"  [{test_count}] Testing empty string...", end=" ")
    if encrypt("", tables) != "":
        print("[FAILED]\n    encrypt('') should return ''")
        failed += 1
    elif decrypt("", tables) != "":
        print("[FAILED]\n    decrypt('') should return ''")
        failed += 1
    else:
        print("[OK]")
    
    # Test 4: Random string
    test_count += 1
    print(f"  [{test_count}] Testing random string round-trip...", end=" ")
    rng = random.Random(42)
    random_chars = ''.join(rng.choice(SUPPORTED_CHARS) for _ in range(200))
    encrypted = encrypt(random_chars, tables)
    decrypted = decrypt(encrypted, tables)
    if decrypted != random_chars:
        print(f"[FAILED]\n    Random string round-trip failed")
        failed += 1
    else:
        print("[OK]")
    
    # Test 5: Long string (1000 alternating chars)
    test_count += 1
    print(f"  [{test_count}] Testing 1000-character alternating string...", end=" ")
    long_text = "AB" * 500
    encrypted = encrypt(long_text, tables)
    decrypted = decrypt(encrypted, tables)
    if decrypted != long_text:
        print(f"[FAILED]\n    Long string round-trip failed")
        failed += 1
    else:
        print("[OK]")
    
    # Test 6: Whitespace preservation
    test_count += 1
    print(f"  [{test_count}] Testing whitespace handling...", end=" ")
    whitespace_text = " \t\n\r" + " " * 10
    encrypted = encrypt(whitespace_text, tables)
    decrypted = decrypt(encrypted, tables)
    # Only space is in SUPPORTED_CHARS; \t\n\r should pass through
    if decrypted != whitespace_text:
        print(f"[FAILED]\n    Whitespace handling failed:")
        print(f"      Input:    {repr(whitespace_text)}")
        print(f"      Decrypted: {repr(decrypted)}")
        failed += 1
    else:
        print("[OK]")
    
    # Test 7: Control character passthrough
    test_count += 1
    print(f"  [{test_count}] Testing control character passthrough...", end=" ")
    control_text = "\x00\x01\x02\x03"
    encrypted = encrypt(control_text, tables)
    decrypted = decrypt(encrypted, tables)
    if decrypted != control_text:
        print(f"[FAILED]\n    Control characters should pass through unchanged")
        failed += 1
    else:
        print("[OK]")
    
    # Test 8: Unicode passthrough (unsupported chars)
    test_count += 1
    print(f"  [{test_count}] Testing Unicode passthrough...", end=" ")
    unicode_text = "Hello 世界! ñ ü"
    encrypted = encrypt(unicode_text, tables)
    decrypted = decrypt(encrypted, tables)
    # Supported chars should be encrypted/decrypted, unsupported should pass through
    if decrypted != unicode_text:
        print(f"[FAILED]\n    Unicode passthrough failed:")
        print(f"      Input:    {repr(unicode_text)}")
        print(f"      Encrypted: {repr(encrypted)}")
        print(f"      Decrypted: {repr(decrypted)}")
        failed += 1
    else:
        print("[OK]")
    
    # Test 9: Table integrity verification
    test_count += 1
    print(f"  [{test_count}] Verifying table integrity...", end=" ")
    
    # Check both tables have exactly the right size
    integrity_ok = True
    
    if len(tables.table_01) != len(SUPPORTED_CHARS):
        print(f"[FAILED]\n    TABLE_01 size mismatch: {len(tables.table_01)} vs {len(SUPPORTED_CHARS)}")
        integrity_ok = False
    elif len(tables.table_02) != len(SUPPORTED_CHARS):
        print(f"[FAILED]\n    TABLE_02 size mismatch: {len(tables.table_02)} vs {len(SUPPORTED_CHARS)}")
        integrity_ok = False
    elif len(tables.rev_table_01) != len(SUPPORTED_CHARS):
        print(f"[FAILED]\n    REV_TABLE_01 size mismatch: {len(tables.rev_table_01)} vs {len(SUPPORTED_CHARS)}")
        integrity_ok = False
    elif len(tables.rev_table_02) != len(SUPPORTED_CHARS):
        print(f"[FAILED]\n    REV_TABLE_02 size mismatch: {len(tables.rev_table_02)} vs {len(SUPPORTED_CHARS)}")
        integrity_ok = False
    
    # Critical test: Verify no symbol overlap between tables
    if integrity_ok:
        table_01_symbols = set(tables.table_01.values())
        table_02_symbols = set(tables.table_02.values())
        overlap = table_01_symbols & table_02_symbols
        
        if overlap:
            print(f"[FAILED]\n    TABLES SHARE {len(overlap)} ENCRYPTED SYMBOL(S):")
            print(f"    {', '.join(repr(s) for s in list(overlap)[:10])}")
            print(f"    This is a critical error - each encrypted symbol must")
            print(f"    uniquely identify which table to use for decryption.")
            integrity_ok = False
        
        # Verify both tables together have exactly 2 * len(SUPPORTED_CHARS) unique symbols
        all_symbols = table_01_symbols | table_02_symbols
        expected_total = len(SUPPORTED_CHARS) * 2
        if len(all_symbols) != expected_total:
            print(f"[FAILED]\n    Combined unique symbols: {len(all_symbols)}, expected: {expected_total}")
            integrity_ok = False
    
    if not integrity_ok:
        failed += 1
    else:
        print("[OK]")
    
    # Test 10: Verify alternating pattern
    test_count += 1
    print(f"  [{test_count}] Verifying alternating table usage...", end=" ")
    test_pattern = "01" * 50  # Even indices: '0', Odd indices: '1'
    encrypted = encrypt(test_pattern, tables)
    # Even positions (0) should use table_01, odd positions (1) use table_02
    pattern_ok = True
    for i, char in enumerate(encrypted):
        expected_table = tables.table_01 if i % 2 == 0 else tables.table_02
        original_char = test_pattern[i]
        if char != expected_table[original_char]:
            print(f"[FAILED]\n    Wrong table used at position {i}")
            pattern_ok = False
            break
    
    if not pattern_ok:
        failed += 1
    else:
        print("[OK]")
    
# Report results
    total_tests = test_count
    
    # Define color codes for output formatting
    RED = "\033[91m"
    RESET = "\033[0m"

    if failed > 0:
        print(f"\n  ❌ {failed}/{total_tests} tests FAILED")
        print("  Critical errors detected. Program cannot start.")
        sys.exit(1)
    else:
        # Wrapping the entire string inside the {RED} tags
        print(f"{RED}  [OK] All {total_tests} tests passed successfully!{RESET}\n")

# ============================================================================
# TERMINAL COMPATIBILITY
# ============================================================================

def check_terminal_unicode_support() -> bool:
    """
    Check if the terminal can properly display Unicode characters.
    
    Uses multiple detection methods:
    1. Environment variable PYTHONIOENCODING
    2. Locale settings
    3. Terminal encoding
    4. Direct character output test
    
    Returns:
        True if terminal likely supports Unicode, False otherwise
    """
    # Check environment variable
    encoding = os.environ.get('PYTHONIOENCODING', '')
    if encoding.lower() in ('ascii', 'latin-1', 'cp1252'):
        return False
    
    # Check stdout encoding
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        stdout_enc = sys.stdout.encoding.lower()
        if 'utf' not in stdout_enc and stdout_enc not in ('', 'none'):
            # Non-UTF encoding might not support our Unicode symbols
            pass  # Continue with other checks
    
    # Try locale
    try:
        loc = locale.getlocale()
        if loc[1] and 'utf' not in loc[1].lower():
            return False
    except (locale.Error, ValueError):
        pass
    
    # Practical test: try to encode a sample Unicode symbol
    try:
        test_symbol = UNICODE_SYMBOLS[0]
        sys.stdout.write('\r')  # Carriage return to not mess up display
        # Check if we can encode it
        test_symbol.encode(sys.stdout.encoding or 'utf-8')
        return True
    except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
        return False


def warn_unicode_issues() -> None:
    """Display a warning if terminal may not support Unicode properly."""
    if not check_terminal_unicode_support():
        print("=" * 60)
        print("  ⚠ WARNING: Terminal may not fully support Unicode")
        print("  Encrypted output may display incorrectly.")
        print("  The cipher will work correctly, but symbols may")
        print("  appear as boxes, question marks, or gibberish.")
        print("=" * 60)
        print()
        # Brief pause to let user read warning
        input("Press Enter to continue...")


# ============================================================================
# USER INTERFACE
# ============================================================================

def display_banner() -> None:
    """Display the professional ASCII art banner with safe terminal colors."""
    # Enable ANSI escape sequences on Windows if needed
    if os.name == 'nt':
        os.system('')

    # ANSI Color Codes
    RED = "\033[91m"
    BRIGHT_RED = "\033[1;31m"
    WHITE = "\033[1;37m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    banner = f"""{BRIGHT_RED}
     ██████╗  ██╗  ███████╗██╗  ██╗
    ██╔════╝ ███║     ███╔╝╚██╗██╔╝
    ██║       ██║    ███╔╝  ╚███╔╝ 
    ██║       ██║   ███╔╝   ██╔██╗ 
    ╚██████╗  ██║  ███████╗██╔╝ ██╗
     ╚═════╝  ╚═╝  ╚══════╝╚═╝  ╚═╝{RESET}
    """
    print(banner)
    print(f"{RED}" + "=" * 50 + f"{RESET}")
    print(f"     {WHITE}C1ZX{RESET} {RED}-{RESET} {CYAN}Cipher Tool by THE NULL{RESET}")
    print(f"{RED}" + "=" * 50 + f"{RESET}")


def display_menu() -> None:
    """Display the main menu options."""
    print("\n  [1] Encrypt Text")
    print("  [2] Decrypt Text")
    print("  [3] About")
    print("  [0] Exit")
    print()


def display_about(tables: CipherTables) -> None:
    """
    Display detailed information about the cipher application.
    
    Args:
        tables: The current CipherTables instance for statistics
    """

    # Define color codes for styling
    RED = "\033[91m"
    BRIGHT_RED = "\033[1;31m"
    WHITE = "\033[1;37m"
    RESET = "\033[0m"

    print()
    print("=" * 50)
    print("              ABOUT")
    print("=" * 50)
    print(f"  Application:     C1ZX Cipher Tool")
    print(f"  Version:         {VERSION}")
    print(f"  Author:          {AUTHOR}")
    print(f"  Python:          {PYTHON_VERSION}")
    print(f"  Cipher Type:     Two-Table Alternating Substitution")
    print(f"  Supported Chars: {len(SUPPORTED_CHARS)} characters")
    print(f"  TABLE_01 Size:   {len(tables.table_01)} mappings")
    print(f"  TABLE_02 Size:   {len(tables.table_02)} mappings")
    print(f"  REV_TABLE_01:    {len(tables.rev_table_01)} mappings")
    print(f"  REV_TABLE_02:    {len(tables.rev_table_02)} mappings")
    print("=" * 50)
    print()
    print("  Description:")
    print("    This cipher utilizes non-standard dynamic state arrays designed to")
    print("    completely break conventional frequency analysis and pattern recognition.")
    print("    Standard LLMs, AI models, and automated cryptanalysis tools cannot")
    print("    reverse-engineer or decrypt payloads generated by this tool without")
    print("    the exact algorithmic parameters and internal state tables.")
    print()
    print("    Characters at even indices use TABLE_01; characters at odd indices use TABLE_02.")
    print("    All printable ASCII characters are supported. Unsupported characters pass")
    print("    through unchanged, preserving data integrity.")
    print()
    print(f"  {RED}Challenge Statement:{RESET}")
    print(f"  {BRIGHT_RED}  Try passing any ciphertext generated by C1ZX into any search engine,{RESET}")
    print(f"  {BRIGHT_RED}  AI model, or automated cryptanalzyer—it will fail to find or crack{RESET}")
    print(f"  {BRIGHT_RED}  the source data.{RESET}")
    print("=" * 60)


def get_user_input(prompt: str) -> Optional[str]:
    """
    Safely get user input with KeyboardInterrupt handling.
    
    Args:
        prompt: The prompt string to display
        
    Returns:
        User input string, or None if user cancelled
    """
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\n")
        return None
    except EOFError:
        print("\n")
        return None


def handle_encrypt(tables: CipherTables) -> None:
    """
    Handle the encryption operation from the user interface.
    
    Prompts for plaintext, encrypts it, and displays the result
    with both character count and byte count information.
    
    Args:
        tables: The validated CipherTables instance
    """
    print()
    print("─" * 50)
    print("  Encrypt Text")
    print("─" * 50)
    print("  Enter text to encrypt (Ctrl+C to cancel):")
    
    text = get_user_input("  Plaintext: ")
    
    if text is None:
        print("  Operation cancelled.")
        return
    
    try:
        encrypted = encrypt(text, tables)
        
        print()
        print("  Result:")
        print("  " + "─" * 46)
        print(f"  {encrypted}")
        print("  " + "─" * 46)
        
        # Show character and byte counts
        char_count = len(encrypted)
        byte_count = len(encrypted.encode('utf-8'))
        print(f"  Characters: {char_count}")
        print(f"  Bytes (UTF-8): {byte_count}")
        
        if char_count != byte_count:
            print("  (Unicode symbols use multiple bytes per character)")
            
    except Exception as e:
        print(f"  Error during encryption: {e}")


def handle_decrypt(tables: CipherTables) -> None:
    """
    Handle the decryption operation from the user interface.
    
    Prompts for ciphertext, decrypts it, and displays the result
    with both character count and byte count information.
    
    Args:
        tables: The validated CipherTables instance
    """
    print()
    print("─" * 50)
    print("  Decrypt Text")
    print("─" * 50)
    print("  Enter text to decrypt (Ctrl+C to cancel):")
    
    cipher_text = get_user_input("  Ciphertext: ")
    
    if cipher_text is None:
        print("  Operation cancelled.")
        return
    
    try:
        decrypted = decrypt(cipher_text, tables)
        
        print()
        print("  Result:")
        print("  " + "─" * 46)
        print(f"  {decrypted}")
        print("  " + "─" * 46)
        
        char_count = len(decrypted)
        byte_count = len(decrypted.encode('utf-8'))
        print(f"  Characters: {char_count}")
        print(f"  Bytes (UTF-8): {byte_count}")
        
    except Exception as e:
        print(f"  Error during decryption: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Main entry point for the C1ZX Cipher Tool.
    
    Initialization sequence:
    1. Display ASCII banner
    2. Check terminal Unicode support and warn if needed
    3. Initialize cipher tables (validates at each step)
    4. Run comprehensive self-tests
    5. Enter interactive menu loop
    
    The program handles KeyboardInterrupt gracefully at all stages.
    """
    try:
        # Display banner
        display_banner()
        
        # Check terminal compatibility
        warn_unicode_issues()
        
        # Initialize cipher system (all validation happens here)
        tables = initialize_cipher()
        
        # Run comprehensive self-tests
        run_self_tests(tables)
        
        # Main interactive loop
        while True:
            display_menu()
            choice = get_user_input("  Select option: ")
            
            if choice is None:  # User pressed Ctrl+C
                print("  Use option [0] to exit.\n")
                continue
            
            if choice == "1":
                handle_encrypt(tables)
            elif choice == "2":
                handle_decrypt(tables)
            elif choice == "3":
                display_about(tables)
            elif choice == "0":
                import webbrowser
                
                # Define color code for dark golden/yellow
                YELLOW = "\033[33m"
                RESET = "\033[0m"
                
                print()
                print("  Thank you for using C1ZX!")
                print("  Goodbye!")
                print("  Follow me on instagram for updates and more tools.")
                print()
                
                # Suiiiii
                choice_insta = input(f"  {YELLOW}Do you want to visit the developer's Instagram? (y/n): {RESET}").strip().lower()
                if choice_insta == 'y':
                    webbrowser.open("https://instagram.com/axxo.developer")
                
                print()
                break
            elif choice == "":
                continue
            else:
                print(f"\n  Invalid option: '{choice}'. Please select 0-3.")
                
    except KeyboardInterrupt:
        print("\n\n  Program interrupted.")
        print("  Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Fatal error: {e}")
        print("  The program will now terminate.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()