# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


class EBCDICDecoder:
    HighestPositive = "7fffffffffffffffffff"

    def __init__(self, bytes: bytearray, type: str, rem_lv: bool, dec_places: int = 0):
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
        self._unpack_map = {
            "ch": self._unpack_text,
            "zd": self._unpack_zoned,
            "zd+": self._unpack_zoned,
            "bi": self._unpack_binary,
            "bi+": self._unpack_binary,
            "pd": self._packed_decimal,
            "pd+": self._packed_decimal,
            "hex": self._bytes.hex,
            "bit": self._packed_decimal,
        }

    def _add_dec_places(value, decimal_places) -> int:
        if decimal_places == 0:
            return value
        else:
            return (
                value[: len(value) - decimal_places]
                + "."
                + value[len(value) - decimal_places :]
            )

    def unpack(self):
        """
        Unpacks the EBCDIC data based on the type.

        Returns:
        - str: The unpacked ASCII data
        """
        if self._bytes in list(self._unpack_map.keys()):
            return self._unpack_map[self._bytes]()
        else:
            raise ValueError("Invalid type")

    def _unpack_text(self):
        """
        Unpacks EBCDIC text data.

        Returns:
        - str: The unpacked ASCII text
        """
        if self.rem_lv == True:
            return bytes.decode("cp037").replace("\x00", "").rstrip()
        else:
            return bytes.decode("cp037")

    def _unpack_zoned(self, signed: bool = False):
        """
        Unpacks EBCDIC zoned data.

        Returns:
        - str: The unpacked ASCII zoned data
        """
        if not signed:
            return self._add_dec_places(
                bytes.decode("cp037").replace("\x00", "").rstrip(), self._dec_places
            )
        else:
            self._add_dec_places(
                ("" if bytes.hex()[-2:-1] != "d" else "-")
                + bytes[:-1].decode("cp037")
                + bytes.hex()[-1:],
                self._dec_places,
            )

    def _unpack_binary(self, signed: bool = False):
        """
        Unpacks EBCDIC binary data.

        Returns:
        - str: The unpacked ASCII binary data
        """
        # TO DO: implement binary unpacking logic
        if not signed:
            return self._add_dec_places(
                str(int("0x" + bytes.hex(), 0)), self._dec_places
            )
        else:
            return self._add_dec_places(
                str(
                    int("0x" + bytes.hex(), 0) - int("0x" + len(bytes) * 2 * "f", 0) - 1
                ),
                self._dec_places,
            )

    def _packed_decimal(self):
        """
        Unpacks EBCDIC packed-decimal data.

        Returns:
        - str: The unpacked ASCII packed-decimal data
        """
        return self._add_dec_places(("" if bytes.hex()[-1:] != "d" and bytes.hex()[-1:] != "b" else "-") + bytes.hex()[:-1], self._dec_places)

    def _unpack_bit(self):
        """
        Unpacks EBCDIC bit data.

        Returns:
        - str: The unpacked ASCII bit data
        """
        return ';'.join( bin(self._bytes[0]).replace("0b", "").zfill(len(self._bytes)*8))