"""Generators

This module exposes generators for the generator utility to use to write to stdout.
"""

from generators.apache import Apache
from generators.cloudflare import Cloudflare
from generators.cloudfront import Cloudfront

__all__ = [Apache, Cloudfront, Cloudflare]
