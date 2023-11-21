from sphinx.cmd.build import main as sphinx_build_main
from utils import loader_func
from GLOBAL_VARS import PLUGIN_ROOT


@loader_func
def build_docs():
    _docs = PLUGIN_ROOT / 'docs'
    _build = _docs / '_build'
    argv = ['-M', 'html', str(_docs), str(_build)]

    sphinx_build_main(argv)


if __name__ == "__main__":
    build_docs()