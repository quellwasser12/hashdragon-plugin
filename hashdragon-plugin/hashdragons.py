#!/usr/bin/env python3

from binascii import unhexlify


class HashdragonDescriber:

    def describe_inner_light(self, hashdragon):
        inner_light = hashdragon.inner_light()
        if 0 <= inner_light < 20:
            return 'Ignorant'
        elif 201 <= inner_light < 240:
            return 'Intelligent'
        elif 240 <= inner_light < 255:
            return 'Enlightened'
        elif inner_light == 255:
            return 'Genius'
        else:
            return ''

    def describe_presence(self, hashdragon):
        presence = hashdragon.presence()
        if presence == 0:
            return 'Invisible'
        elif 1 <= presence < 10:
            return 'Ghost'
        elif 10 <= presence < 40:
            return 'Shadow'
        elif 40 <= presence < 60:
            return 'Shimmering'
        elif 230 < presence < 255:
            return 'Rock'
        elif presence == 255:
            return 'Marble'
        else:
            return ''


    def describe_charm(self, hashdragon):
        charm = hashdragon.charm()
        if charm < 5:
            return 'Brutal'
        elif 5 <= charm < 15:
            return 'Unfriendly'
        elif 190 < charm <= 230:
            return 'Friendly'
        elif 230 < charm <= 250:
            return 'Charming'
        elif charm > 250:
            return 'Charismatic'
        else:
            return ''

    def describe_strangeness(self, hashdragon):
        strangeness = hashdragon.strangeness()
        if strangeness < 10:
            return 'Practical'
        elif 200 < strangeness <= 240:
            return 'Strange'
        elif strangeness > 240:
            return 'Weird'
        else:
            return ''


    def describe_beauty(self, hashdragon):
        beauty = hashdragon.beauty()
        if beauty < 10:
            return 'Ugly'
        elif 10 <= beauty < 20:
            return 'Unattractive'
        elif 200 < beauty <= 230:
            return 'Attractive'
        elif 230 < beauty <= 250:
            return 'Beautiful'
        elif beauty > 250:
            return 'Exquisite'
        else:
            return ''

    def describe_truth(self, hashdragon):
        truth = hashdragon.truth()
        if truth < 5:
            return 'Lying'
        elif 5 <= truth < 20:
            return 'Dishonest'
        elif 220 < truth <= 250:
            return 'Honest'
        elif truth > 250:
            return 'Oracular'
        else:
            return ''

    def describe_magic(self, hashdragon):
        magic = hashdragon.magic()
        if magic < 20:
            return 'Clumsy'
        elif 210 < magic <= 250:
            return 'Magical'
        elif 250 < magic < 255:
            return 'Legendary'
        elif magic == 255:
            return 'Mythical'
        else:
            return ''


    def describe(self, hashdragon):
        virtues = ', '.join(filter(lambda x: x != '',
                         [self.describe_inner_light(hashdragon),
                          self.describe_presence(hashdragon),
                          self.describe_charm(hashdragon),
                          self.describe_strangeness(hashdragon),
                          self.describe_beauty(hashdragon),
                          self.describe_truth(hashdragon),
                          self.describe_magic(hashdragon)]))
        if virtues == '':
            return 'Unremarkable'
        return virtues


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

    def inner_light(self):
        return self.b[3]

    def presence(self):
        return self.b[7]

    def charm(self):
        return self.b[8]

    def strangeness(self):
        return self.b[9]

    def beauty(self):
        return self.b[10]

    def truth(self):
        return self.b[11]

    def magic(self):
        return self.b[12]

    def special_powers(self):
        return bin(int.from_bytes(self.b[13:16], 'big')).lstrip('0b')

    def manifestation(self):
        return int.from_bytes(self.b[16:20], 'big')

    def arcana(self):
        return int.from_bytes(self.b[20:24], 'big')

    def cabala(self):
        return int.from_bytes(self.b[24:28], 'big')

    def maturity(self):
        return int.from_bytes(self.b[28:30], 'big')

    def sigil(self):
        return int.from_bytes(self.b[30:32], 'big')

    def sigil_unicode(self):
        return chr(self.b[30] + 4608) + chr(self.b[31] + 4608)

    def description(self):
        pass

    @classmethod
    def from_hex_string(self, string):
        self.b = unhexlify(string)

        if self.b[0] != 0xd4:
            raise AssertionError('Not a valid hashdragon')

        hd = Hashdragon()
        hd.hash = string
        return hd



# hd = Hashdragon.from_hex_string('d41a8517be90657bd88502def8b6c9ffca37f6c8a2d631d02b535d47965c479c')
# print("Strength: ", hd.strength())
# print("Colour: ", hd.colour_as_rgb())
# print("Beauty: ", hd.beauty())
# print("Special Powers: ", hd.special_powers())
# print("manifestation: ", hd.manifestation())
# print("Sigil ", hd.sigil_unicode())
