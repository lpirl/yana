"""
Main script to be called from the command line.
"""

from lib.cli import Cli

def main():
    """
    Creates and hands over to CLI handler.
    """
    cli = Cli()
    cli.handle_args()

    # TODO: what is the proper way to wire something to program exit
    #   (willing and unwillingly)
    cli.tear_down()

if __name__ == '__main__':
    main()
