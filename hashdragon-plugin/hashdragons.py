#!/usr/bin/env python3

from binascii import unhexlify

class Hashdragon:

    def __init__(self):
        self.hash = ''

    def hashdragon(self):
        return self.hash

    def strength(self):
        count = 0
        for bb in self.b:
            count += bin(bb).count('1')
        return count

    def colour_as_rgb(self):
        r,g,b = self.b[4:7]
        return [r, g, b]

    def colour(self):
        colour_bytes = self.b[4:7]
        return '#' + ''.join( '%02x' % b for b in colour_bytes)

    @classmethod
    def from_hex_string(self, string):
        self.b = unhexlify(string)

        if self.b[0] != 0xd4:
            raise AssertionError('Not a valid hashdragon')

        hd = Hashdragon()
        hd.hash = string
        return hd



# hd = Hashdragon.from_hex_string('d41a8517be90657bd88502def8b6c9ffca37f6c8a2d631d02b535d47965c479c')
# print("Strength: %d", hd.strength())
# print("Colour: ", hd.colour_as_rgb())
