
# gen_prime, multinv, and keygen functions copy/pasted from
# http://stackoverflow.com/questions/8539441/private-public-encryption-in-python-with-standard-library

import random

def gen_prime(N=10**8, bases=range(2,20000)):
    # FIXME replace with a more sophisticated algorithm
    p = 1
    while any(pow(base, p-1, p) != 1 for base in bases):
        p = random.SystemRandom().randrange(N)
    return p

def multinv(modulus, value):
    '''Multiplicative inverse in a given modulus

        >>> multinv(191, 138)
        18
        >>> 18 * 138 % 191
        1

    '''
    # http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    x, lastx = 0, 1
    a, b = modulus, value
    while b:
        a, q, b = b, a // b, a % b
        x, lastx = lastx - q * x, x
    result = (1 - lastx * modulus) // value
    return result + modulus if result < 0 else result


def keygen(N):
    '''Generate public and private keys from primes up to N.

        >>> pubkey, privkey = keygen(2**64)
        >>> msg = 123456789012345
        >>> coded = pow(msg, 65537, pubkey)
        >>> plain = pow(coded, privkey, pubkey)
        >>> assert msg == plain

    '''
    # http://en.wikipedia.org/wiki/RSA
    prime1 = gen_prime(N)
    prime2 = gen_prime(N)
    print "prime1 %d prime2 %d" % (prime1, prime2)
    totient = (prime1 - 1) * (prime2 - 1)
    return prime1 * prime2, multinv(totient, 65537)


class PEcrypt:
    """ PEcrypt class is copy-pasted from
        http://code.activestate.com/recipes/266586/ 

    """
    def __init__(self, aKey):
        self.key = aKey

    def Crypt(self, aString):
        kIdx = 0
        cryptStr = ""   
        for x in range(len(aString)):
            cryptStr = cryptStr + \
                       chr( ord(aString[x]) ^ ord(self.key[kIdx]))
            kIdx = (kIdx + 1) % len(self.key)

        return cryptStr

def SimpleObfuscator(aString, aKey, obfuscate=True):
    ''' naive string obfuscation by shifting char values '''
    i = 0
    k = len(aKey)-1
    shiftString = ''
    while i < len(aString):
        sumVal = -1 * (ord(aKey[k]) % 2) * pow(ord(aKey[k]), 2)
        numChar = ord(aString[i]) 
        if obfuscate:
            numChar += sumVal
        else:
            numChar -= sumVal
        while numChar > 255:
            numChar -= 256
        while numChar < 0:
            numChar += 256
        shiftString += chr(numChar)
        i += 1
        k -= 1
        if k < 0:
            k = len(aKey)-1
    return shiftString

class SimpleCrypt:
    def __init__(self, useObfuscator = True):
        self.obfuscate = useObfuscator
        self.twoWayKey = False
        self.publicKey = False
        self.privateKey = False

    def SetTwoWayKey(self, aKey):
        self.twoWayKey = aKey
        if self.twoWayKey:
            self.crypter = PEcrypt(self.twoWayKey)

    def SetPublicKey(self, aKey):
        self.publicKey = aKey

    def SetPrivateKey(self, aKey):
        self.privateKey = aKey

    def PPKeyGen(self, exp=32):
        if type(exp) != type(1):
            exp = 32
        return keygen(2**exp)

    def Crypt(self, aString):
        if not self.twoWayKey:
            return False
        if self.obfuscate:
            return self.crypter.Crypt(SimpleObfuscator(aString, self.crypter.key))
        else:
            return self.crypter.Crypt(aString)

    def DeCrypt(self, aString):
        if not self.twoWayKey:
            return False
        if self.obfuscate:
            return SimpleObfuscator(self.crypter.Crypt(aString), self.crypter.key, False)
        else:
            return self.crypter.Crypt(aString)

    def PPCrypt(self, msg):
        if not self.publicKey:
            return False
        nList = []
        i = 0
        while i < len(msg):
            n = (ord(msg[i]) << 24) + (ord(msg[i+1]) << 16) + (ord(msg[i+2]) << 8) + ord(msg[i+3])
            nList.append(pow(n, 65537, self.publicKey))
            i += 4
        return nList

    def PPDecrypt(self, msg):
        if not self.publicKey or not self.privateKey:
            return False
        out = ''
        for m in msg:
            n = pow(m, self.privateKey, self.publicKey)
            out += chr((n >> 24) & 0xff)
            out += chr((n >> 16) & 0xff)
            out += chr((n >> 8) & 0xff)
            out += chr(n & 0xff)
        return out


if __name__ == "__main__":
    import sys

    def strToHex(aString):
        hexStr = ""
        for x in aString:
            hexStr = hexStr + "%02X " % ord(x)

        return hexStr
    
    # self test routine

    print "\nTesting SimpleCrypt!"
    print "----------------\n"

    print "\n *** Two way encryption\n"

    keyStr = "This is a key"
    if len(sys.argv) == 1:
        testStr = "The quick brown fox jumps over the lazy dog!"
    else:
        testStr = sys.argv[1]

    print "\nString : ", testStr
    print "in hex : ", strToHex(testStr)
    print "key    : ", keyStr

    pe = SimpleCrypt()  # generate the SimpleCrypt instance
    pe.SetTwoWayKey(keyStr)

    testStr = pe.Crypt(testStr)
    print "\nEncrypted string"
    print "Hex    : ", strToHex(testStr)

    testStr = pe.DeCrypt(testStr)
    print "\nDecrypted string"
    print "Ascii  : ", testStr
    print "Hex    : ", strToHex(testStr)

    for i in range(256):
        c = pe.Crypt(chr(i))
        d = pe.DeCrypt(c)
        if chr(i) != d:
            print "ERROR %d %s %s" % (i, chr(i), d)

    print "\n *** Public/private key encryption\n"

    pub, priv = pe.PPKeyGen()
    print "\nPublic key: ", pub
    print "Private key: ", priv

    pe.SetPublicKey(pub)

    print "\nMsg :", testStr

    encoded = pe.PPCrypt(testStr)
    print "\n Public key encoding: ", str(encoded)

    pe.SetPrivateKey(priv)
    print "Private key decoding: ", pe.PPDecrypt(encoded)


            
    

