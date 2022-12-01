# contracts.py
import logunittest.src.settings as sts
import os, sys
import colorama as color

color.init()


def checks(*args, **kwargs):
    warn_deletion(*args, **kwargs)
    return kwargs


def warn_deletion(*args, action, **kwargs):
    print(f"srs.contracts.action: {action}")
