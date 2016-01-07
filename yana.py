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

if __name__ == '__main__':
    main()
