from binascii import b2a_uu
from os import urandom
from sys import argv
from timeit import timeit

from .curve import (
    P192, P224, P256, P384, P521, secp256k1, brainpoolP160r1, brainpoolP192r1, brainpoolP224r1,
    brainpoolP256r1, brainpoolP320r1, brainpoolP384r1, brainpoolP512r1
)
from .ecdsa import sign, verify
from .keys import gen_keypair


def sign_and_verify(d, Q, curve):
    msg = b2a_uu(urandom(32))
    sig = sign(msg, d, curve=curve)
    assert verify(sig, msg, Q, curve=curve)


if __name__ == '__main__':
    iterations = 1000
    curves = (
        P192, P224, P256, P384, P521, secp256k1, brainpoolP160r1, brainpoolP192r1, brainpoolP224r1,
        brainpoolP256r1, brainpoolP320r1, brainpoolP384r1, brainpoolP512r1
    )

    for curve in curves:
        d, Q = gen_keypair(curve)
        time = timeit(stmt=lambda: sign_and_verify(d, Q, curve), number=iterations)
        print('{} signatures and verifications with curve {} took {:.2f} seconds'.format(
            iterations, curve.name, time))
