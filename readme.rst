sphinxcontrib-multipath
=======================

This extension gives Sphinx a fallback path so that a common source pattern can
be used to author documentation. In addition to falling back to the common
source, Jinja can also be used as a transform to extend source files from the
common source.

Configuration
-------------

Multiple source paths can be configured using an option in your configuration::

    extensions = [
        ...
        'sphinxcontrib.multipath',
    ]

    multipaths = [
        '../submodule/docs',
        '.',
    ]

Extending docs
--------------

Extending a source file can be accomplished with Jinja. All you need is a source
file that can be extended, using Jinja blocks. For example, assuming the
configuration file above, a ``../submodule/docs/foo.rst`` would look like::

    Base source file
    ================

    {% block main %}
    This is the base source file
    {% endblock %}

In the local environment source path, ``./foo.rst`` can extend the base source
file::

    {% extends 'foo.rst' %}

    {% block main %}
    This is extended from the base source file
    {% endblock %}
