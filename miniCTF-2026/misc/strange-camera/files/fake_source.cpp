
#include <openssl/sha.h>

#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Bytes = std::vector<std::uint8_t>;
using Hash256 = std::array<std::uint8_t, SHA256_DIGEST_LENGTH>;

struct DecryptedImage {
    Bytes bytes;
    std::string extension;
};

// Implemented inside the distributed challenge binary.
// Its definition is deliberately omitted from this public source file.
DecryptedImage decrypt_image(const Bytes& encrypted_data,
                             const std::string& decoded_key);

namespace {

constexpr Hash256 EXPECTED_KEY_HASH = {
    0x17,0xd4,0x55,0xf9,0xc7,0xe1,0x90,0x15,
    0x86,0x1d,0x99,0x6f,0x0b,0x88,0x48,0x9f,
    0x3e,0xd8,0xbe,0x71,0x27,0x92,0x39,0xf4,
    0xa9,0x46,0xf6,0x86,0xac,0x31,0x7f,0xd1
};

std::uint8_t rotate_right(std::uint8_t value, unsigned amount) {
    amount &= 7U;
    return static_cast<std::uint8_t>(
        (value >> amount) | (value << ((8U - amount) & 7U))
    );
}

bool decode_key(const std::string& input, std::string& decoded) {
    constexpr std::uint8_t XOR_MASK[5] = {
        0xdb, 0xef, 0x3d, 0x41, 0xa1
    };

    Bytes bytes(input.begin(), input.end());
    if (bytes.size() != 16) return false;

    for (std::size_t i = 0; i < bytes.size(); ++i) {
        bytes[i] = rotate_right(bytes[i], static_cast<unsigned>((i % 7) + 1));
        bytes[i] ^= XOR_MASK[i % 5];
        bytes[i] = static_cast<std::uint8_t>(
            bytes[i] - static_cast<std::uint8_t>(i * 3 + 7)
        );
    }

    std::reverse(bytes.begin(), bytes.end());
    decoded.assign(bytes.begin(), bytes.end());
    return true;
}

Hash256 sha256(const std::string& text) {
    Hash256 digest{};
    SHA256(
        reinterpret_cast<const unsigned char*>(text.data()),
        text.size(),
        digest.data()
    );
    return digest;
}

bool hashes_equal(const Hash256& left, const Hash256& right) {
    std::uint8_t difference = 0;
    for (std::size_t i = 0; i < left.size(); ++i) {
        difference |= left[i] ^ right[i];
    }
    return difference == 0;
}

Bytes read_binary_file(const std::string& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("cannot open input file");

    const std::streampos end = input.tellg();
    if (end <= 0) throw std::runtime_error("input file is empty");

    Bytes data(static_cast<std::size_t>(end));
    input.seekg(0);
    if (!input.read(reinterpret_cast<char*>(data.data()),
                    static_cast<std::streamsize>(data.size()))) {
        throw std::runtime_error("cannot read input file");
    }
    return data;
}

void write_binary_file(const std::string& path, const Bytes& data) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot open output file");

    output.write(
        reinterpret_cast<const char*>(data.data()),
        static_cast<std::streamsize>(data.size())
    );
    if (!output) throw std::runtime_error("cannot write output file");
}

void print_as_binary(const Bytes& data) {
    constexpr std::size_t BYTES_PER_LINE = 8;
    std::cout << "Binary image data (" << data.size() << " bytes):\n";

    for (std::size_t i = 0; i < data.size(); ++i) {
        std::cout << std::bitset<8>(data[i]);
        if ((i + 1) % BYTES_PER_LINE == 0 || i + 1 == data.size()) {
            std::cout << '\n';
        } else {
            std::cout << ' ';
        }
    }
}

void print_usage(const char* program_name) {
    std::cerr << "Usage:\n"
              << "  " << program_name << " <data.bin> <data.out>\n";
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2 || argc > 4) {
        print_usage(argv[0]);
        return 2;
    }

    std::string input_key;
    std::string data_path;
    std::string output_path;

    if (argc == 2 || argc == 3) {
        data_path = argv[1];
        if (argc == 3) output_path = argv[2];

        std::cout << "Enter key: ";
        if (!std::getline(std::cin, input_key)) {
            std::cout << "Wrong\n";
            return 1;
        }
    } else {
        input_key = argv[1];
        data_path = argv[2];
        output_path = argv[3];
    }

    std::string decoded_key;
    if (!decode_key(input_key, decoded_key) ||
        !hashes_equal(sha256(decoded_key), EXPECTED_KEY_HASH)) {
        std::cout << "Wrong\n";
        return 1;
    }

    try {
        const Bytes encrypted_data = read_binary_file(data_path);
        const DecryptedImage image = decrypt_image(encrypted_data, decoded_key);

        if (output_path.empty()) {
            output_path = "recovered" +
                (image.extension.empty() ? ".img" : image.extension);
        }

        write_binary_file(output_path, image.bytes);
        std::cout << "Correct key!\n"
                  << "Image restored: " << output_path << '\n';
        print_as_binary(image.bytes);
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
