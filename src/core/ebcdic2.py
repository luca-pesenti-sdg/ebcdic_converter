# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


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
            return self._bytes.decode('cp037').replace('\x00', '').rstrip() if self._rem_lv == True else self._bytes.decode('cp037')

        # Packed Decimal
        elif self._type == "pd" or self._type == "pd+":
            return _add_dec_places(("" if self._bytes.hex()[-1:] != "d" and self._bytes.hex()[-1:] != "b" else "-") + self._bytes.hex()[:-1], self._dec_places)

        # Binary
        elif self._type == "bi" or (self._type == "bi+" and self._bytes.hex() <= self._HighestPositive[:len(self._bytes)*2]):
            return _add_dec_places(str(int("0x" + self._bytes.hex(), 0)),self._dec_places)
        
        # Signed Binary
        elif self._type == "bi+":
            return _add_dec_places(str(int("0x" + self._bytes.hex(), 0) - int("0x" + len(self._bytes) * 2 * "f", 0) -1), self._dec_places)

        # Zoned
        if self._type == "zd":
            return _add_dec_places(self._bytes.decode('cp037').replace('\x00', '').rstrip(), self._dec_places)

        # Signed Zoned
        elif self._type == "zd+":
            return _add_dec_places(("" if self._bytes.hex()[-2:-1] != "d" else "-") + self._bytes[:-1].decode('cp037') + self._bytes.hex()[-1:], self._dec_places)

        elif self._type == "hex":
            return self._bytes.hex() 

        elif self._type == "bit":
            return ';'.join( bin(bytes[0]).replace("0b", "").zfill(len(self._bytes)*8))
        
        else:
            print("---------------------------\nLength & Type not supported\nLength: ",len(self._bytes),"\nType..: " ,type)
            exit()

def _add_dec_places(value,  decimal_places) -> int:
    if decimal_places == 0:
        return value
    else:
        return (
            value[: len(value) - decimal_places]
            + "."
            + value[len(value) - decimal_places :]
        )