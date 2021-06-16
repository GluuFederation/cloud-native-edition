from pygluu.kubernetes.create import create_parser, main
import argparse
from argparse import ArgumentParser, _StoreAction
import sys


def test_empty_arg():
    parser = create_parser()
    args = parser.parse_args(['version'])

    assert args is not None
