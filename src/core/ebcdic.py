#
# Formats ebcdic text, zoned, big endian binary or decinal data into unpacked/string ascii data.

# Parameters:
#  - bytes (bytearray): The content to be extracted
#  - type  (str)......:
#   - ch : text                     | pic  x
#   - zd : zoned                    | pic  9
#   - zd+: signed zoned             | pic s9
#   - bi : binary                   | pic  9 comp
#   - bi+: signed binary            | pic s9 comp
#   - dp : double-precision         | pic  9 comp-2
#   - dp+: signed double-precision  | pic s9 comp-2
#   - pd : packed-decimal           | pic  9 comp-3
#   - pd+: signed packed-decimal    | pic s9 comp-3

# Returns:
#  - ascii string

# Test sample:
#  import struct
#  ori = 9223372036854775807
#  print(ori, unpack(struct.pack(">q",ori),"bi+"))
#  ori = ori * -1
#  print(ori, unpack(struct.pack(">q",ori),"bi+"))
#  print(unpack(bytearray.fromhex("f0f0f1c1"), "zd+"))

# Input examples:
# - 8 bytes comp-signed   struct q: -9,223,372,036,854,775,808 through +9,223,372,036,854,775,807
# - 8 bytes comp-unsigned struct Q: 0 through 18,446,744,073,709,551,615
# - 4 bytes comp-signed   struct i: -2147483648 through +2147483647
# - 4 bytes comp-unsigned struct I: 0 through +4294967295
# - 2 bytes comp-signed   struct h: -32768 through +32767
# - 2 bytes comp-unsigned struct H: 0 through +65535


class EBCDICDecoder:

    def __init__(
        self,
        bytes: bytearray,
        type: str,
        rem_lv: bool,
        dec_places: int = 0,
        rem_spaces: bool = False,
    ):
        """
        Initializes the EBCDICDecoder class.

        Parameters:
        - bytes (bytearray): The content to be extracted
        - type (str): The type of data (ch, zd, zd+, bi)
        - rem_lv (bool): Remove leading zeros
        """
        self._bytes = bytes
        self._type = type.lower()
        self._rem_lv = rem_lv
        self._dec_places = dec_places
        self._rem_spaces = rem_spaces  # seems useless
        self._HighestPositive = "7fffffffffffffffffff"

    def unpack(self):
        """
        Unpacks the EBCDIC data based on the type.

        Returns:
        - str: The unpacked ASCII data
        """
        # Text
        if self._type == "ch":
            return self._bytes.decode("cp037").replace("\x00", "")
            # return (
            #     self._bytes.decode("cp037").replace("\x00", "").rstrip()
            #     if self._rem_lv == True
            #     else self._bytes.decode("cp037")
            # )

        # Packed Decimal
        elif self._type == "pd" or self._type == "pd+":
            return _add_dec_places(
                (
                    ""
                    if self._bytes.hex()[-1:] != "d" and self._bytes.hex()[-1:] != "b"
                    else "-"
                )
                + self._bytes.hex()[:-1],
                self._dec_places,
            )

        # Double Precision
        elif self._type == "dp" or self._type == "dp+":
            # for the reference see here:
            # https://www.tek-tips.com/threads/the-truth-about-the-comp-1-and-comp-2-floating-point-fields.845671/
            
            # print('bytes\t\t\t:', self._bytes)
            # print('full_binary\t\t:', bin(int(self._bytes.hex(), 16)))
            # print('bytes\t\t\t:', ''.join(format(byte, '08b') for byte in self._bytes))
            # print('hex\t\t\t:', self._bytes.hex())
            
            binary_data = bin(int(self._bytes.hex(), 16))[2:].zfill(64)  # 64 bits for double precision
            sign = -1 if binary_data[0] == "1" else 1  # 1 bit
            exponent = binary_data[1:8]  # 7 bits

            mantissa = binary_data[8:]  # 56 bits
            mantissa_hex = hex(int(mantissa, 2))  # convert to hex
            real_exponent_decimal = int(exponent, 2) - 64  # 64 is the exponent bias
            mantissa_cleaned = mantissa_hex[2:]  # remove the "0x" prefix
            number = int(mantissa_cleaned, 16) * (16 ** (real_exponent_decimal - 14))
            
            # print('binary\t\t\t:', binary_data)
            # print('mantissa\t\t\t:', mantissa)
            # print('real_exponent_decimal\t:', real_exponent_decimal)
            # print('mantissa_hex\t:', mantissa_hex)
            # print('mantissa_cleaned\t:', mantissa_cleaned)
            # print('number\t\t\t:', str(number*sign))
            # print('-----------')
            # exit()

            return str(number*sign)

        # Binary
        elif self._type == "bi" or (
            self._type == "bi+"
            and self._bytes.hex() <= self._HighestPositive[: len(self._bytes) * 2]
        ):
            return _add_dec_places(
                str(int("0x" + self._bytes.hex(), 0)), self._dec_places
            )

        # Signed Binary
        elif self._type == "bi+":
            return _add_dec_places(
                str(
                    int("0x" + self._bytes.hex(), 0)
                    - int("0x" + len(self._bytes) * 2 * "f", 0)
                    - 1
                ),
                self._dec_places,
            )

        # Zoned
        if self._type == "zd":
            return _add_dec_places(
                self._bytes.decode("cp037").replace("\x00", "").rstrip(),
                self._dec_places,
            )

        # Signed Zoned
        elif self._type == "zd+":
            return _add_dec_places(
                ("" if self._bytes.hex()[-2:-1] != "d" else "-")
                + self._bytes[:-1].decode("cp037")
                + self._bytes.hex()[-1:],
                self._dec_places,
            )

        elif self._type == "hex":
            return self._bytes.hex()

        elif self._type == "bit":
            return ";".join(bin(bytes[0]).replace("0b", "").zfill(len(self._bytes) * 8))

        else:
            print(
                "---------------------------\nLength & Type not supported\nLength: ",
                len(self._bytes),
                "\nType..: ",
                type,
            )
            exit()


def _add_dec_places(value, decimal_places) -> int:
    if decimal_places == 0:
        return value
    else:
        return (
            value[: len(value) - decimal_places]
            + "."
            + value[len(value) - decimal_places :]
        )
