import os
import hyperglass.hyperglass

application = hyperglass.hyperglass.app

hyperglass_root = os.path.dirname(hyperglass.__file__)
static = os.path.join(hyperglass_root, "static")

if __name__ == "__main__":
    application.run(static_folder=static)
