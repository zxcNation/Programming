def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    upper_alphabet = [chr(i) for i in range(ord("A"), ord("Z") + 1)] + [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    lower_alphabet = [chr(i) for i in range(ord("a"), ord("z") + 1)] + [chr(i) for i in range(ord("a"), ord("z") + 1)]
    for ch in plaintext:
        if ch in upper_alphabet:
            ch_index = upper_alphabet.index(ch)
            ciphertext += upper_alphabet[ch_index + shift]

        elif ch in lower_alphabet:
            ch_index = lower_alphabet.index(ch)
            ciphertext += lower_alphabet[ch_index + shift]
        else:
            ciphertext += ch
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    upper_alphabet = [chr(i) for i in range(ord("A"), ord("Z") + 1)] + [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    lower_alphabet = [chr(i) for i in range(ord("a"), ord("z") + 1)] + [chr(i) for i in range(ord("a"), ord("z") + 1)]
    for ch in ciphertext:
        if ch in upper_alphabet:
            ch_index = upper_alphabet.index(ch)
            plaintext += upper_alphabet[ch_index + 26 - shift]

        elif ch in lower_alphabet:
            ch_index = lower_alphabet.index(ch)
            plaintext += lower_alphabet[ch_index + 26 - shift]
        else:
            plaintext += ch

    return plaintext
