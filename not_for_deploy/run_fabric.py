"""
Very thin wrapper around Fabric. We basically re-implement
the ``fab`` executable.

We use this when we need to create PyCharm run configurations that run Fabric tasks.
"""

if __name__ == '__main__':
    from fabric.main import main
    main()
