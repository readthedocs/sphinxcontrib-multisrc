# -*- coding: utf-8 -*-

"""Sphinx multiple source path support."""

__version_info__ = (1, 0, 0)
__version__ = '1.0.0'

import os
import types

from jinja2 import Environment, FileSystemLoader
from sphinx.environment import BuildEnvironment


def create_fallback_envs_for_app(app):
    """
    Create additional envs for separate source paths.

    Additional environments are created in order to find files and translate
    docnames to paths. Additional environments are the cleanest method to
    accomplish this.

    :param app: Base Sphinx application
    """
    # This code is copied from the Sphinx application instantiation
    for path in app.config.multisrc_paths:
        env = BuildEnvironment()
        env.app = app
        env.doctreedir = app.doctreedir
        env.srcdir = path
        env.version = app.registry.get_envversion(app)
        env.domains = {}
        for domain in app.registry.create_domains(env):
            env.domains[domain.name] = domain
        env._update_config(app.config)
        env._update_settings(app.config)
        yield env


def builder_inited(app):
    """Event listener to set up multiple environments."""
    fallback_envs = list(create_fallback_envs_for_app(app))
    patch_find_files(app.env, fallback_envs)
    patch_doc2path(app.env, fallback_envs)


def patch_find_files(env, fallback_envs):
    """
    Patches the base environment ``find_files`` to support multiple paths.

    The patched function uses each environments ``find_files`` to create a
    complete list of all of the docnames found across the environments.

    :param env: Base Sphinx environment
    :type env: sphinx.environment.BuildEnvironment
    :param fallback_envs: A list of fallback environments
    :type fallback_envs: [sphinx.environment.BuildEnvironment]
    """
    override_find_files = env.find_files

    def find_files(env, config, builder):
        override_find_files(config, builder)
        for fallback_env in fallback_envs:
            fallback_env.find_files(config, builder)
            env.found_docs |= fallback_env.found_docs

    env.find_files = types.MethodType(find_files, env)


def patch_doc2path(env, fallback_envs):
    """
    Patches the base environment ``doc2path`` to support multiple paths.

    The patched function uses each environments ``doc2path`` until it finds a
    file that exists for the docname.

    :param env: Base Sphinx environment
    :type env: sphinx.environment.BuildEnvironment
    :param fallback_envs: A list of fallback environments
    :type fallback_envs: [sphinx.environment.BuildEnvironment]
    """
    override_doc2path = env.doc2path

    def doc2path(env, docname, base=True, suffix=None):
        path = override_doc2path(docname, base, suffix)
        if not os.path.exists(path):
            for fallback_env in fallback_envs:
                # Force our base env path name in front of the path, as a
                # relative path, so that it can pass some asserts that check for
                # the ``env.srcdir`` at the beginning of the path name
                fallback_path = fallback_env.doc2path(docname, base, suffix)
                if os.path.exists(fallback_path):
                    path = os.path.join(
                        env.srcdir,
                        os.path.relpath(
                            fallback_path,
                            env.srcdir,
                        ),
                    )
                    break
        return path

    env.doc2path = types.MethodType(doc2path, env)


def render_jinja(app, docname, source):
    """Perform Jinja transform on source on read."""
    env = Environment(loader=FileSystemLoader(app.config.multisrc_paths),)
    template = env.from_string(source[0])
    source[0] = template.render(app.config.html_context)


def setup(app):
    app.connect('builder-inited', builder_inited)
    app.connect('source-read', render_jinja)
    app.add_config_value('multisrc_paths', ['.'], 'env')
    return {
        'version': __version__,
    }
