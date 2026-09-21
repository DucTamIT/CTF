import codecs

bits = open("files/chirp.txt").read().split()

# Bước 1: mỗi nhóm 8 bit là một ký tự ASCII
text = "".join(chr(int(b, 2)) for b in bits)
print("binary -> ascii:", text)

# Bước 2: "bay 13 vòng" -> ROT13
print("rot13:          ", codecs.decode(text, "rot13"))
