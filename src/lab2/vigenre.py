def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.
    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    Key = ""
    upper_alphabet = [chr(i) for i in range(ord("A"), ord("Z") + 1)] + [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    lower_alphabet = [chr(i) for i in range(ord("a"), ord("z") + 1)] + [chr(i) for i in range(ord("a"), ord("z") + 1)]
    i = 0
    while i != len(plaintext):
        Key += keyword[i % len(keyword)]
        i += 1

    Key = Key.upper()

    for i in range(len(plaintext)):
        if plaintext[i] in upper_alphabet:
            ch1_index = upper_alphabet.index(plaintext[i])
            ch2_index = upper_alphabet.index(Key[i])
            ciphertext += upper_alphabet[ch1_index + ch2_index]
        else:
            ch1_index = lower_alphabet.index(plaintext[i])
            ch2_index = upper_alphabet.index(Key[i])
            ciphertext += lower_alphabet[ch1_index + ch2_index]

    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.
    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    # PUT YOUR CODE HERE
    return plaintext