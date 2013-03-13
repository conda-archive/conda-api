=================================================
conda-api: a light weight conda interface library
=================================================


Purpose of this package:
------------------------
  * Document a well-defined small and useful interface to conda, which is
    stable across many conda versions.
  * Allow users to easily interact conda from *any* environment (in fact
    from any Python process on the same machine).
    As conda always only resides in the so-called root environment, it
    is not possible to import conda from any additional environments.
    For this purpose, the conda-api supports (at least) Python 2.6, 2.7
    and 3.3, whereas conda itself will always (at least for the foreseeable
    future will only support Python 2.7).


Implementation details:
-----------------------
  * Most functionality will be implemented by calling the conda command
    in a sub-process.  To process the output from the conda sub-process,
    conda may, e.g. write json to stdout.
  * Very trivial functionality (such as returning the list of named
    environments, i.e. basically a listing of the envs directory), are
    implemented in this library directory.
