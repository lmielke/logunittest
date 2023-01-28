"""
    Entry poiont for logunittest shell calls 
    ###################################################################################
    
    __main__.py imports the action module from logunittest.actions >> actionModule.py
                and runs it
                action is provided as first positional argument

    ###################################################################################
    
    for user info runs: 
        python -m logunittest info
    above cmd is identical to
        python -m logunittest.actions.info


"""

import colorama as color

color.init()
import importlib

import logunittest.settings as sts
import logunittest.arguments as arguments
import logunittest.contracts as contracts


def runable(*args, action, **kwargs):
    """
    imports action as a package and executes it
    returns the runable result
    """
    return importlib.import_module(f"logunittest.actions.{action}")


def main(*args, **kwargs):
    """
    to runable from shell these arguments are passed in
    runs action if legidemit and prints outputs
    """
    kwargs = arguments.mk_args().__dict__

    # kwargs are vakidated against enforced contract
    kwargs = contracts.checks(*args, **kwargs)
    if kwargs.get("action") != "help":
        return runable(*args, **kwargs).main(*args, **kwargs)


if __name__ == "__main__":
    main()
