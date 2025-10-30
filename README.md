# jupyter-ai-magic-commands

Magics are currently provided for Jupyter AI via the package `jupyter-ai-magics` ([current version 2.31.6](https://pypi.org/project/jupyter-ai-magics)). This works with Jupyter AI v2 but will not work with the collection of extensions for v3 developed in https://github.com/jupyter-ai-contrib, which use `litellm` via the https://github.com/jupyter-ai-contrib/jupyter-ai-litellm repository. Therefore, we introduce an updated magics package, titled `jupyter_ai_magic_commands` (v0.0.1) for use with Jupyter AI v3.

## Installation

Create the environment:

```
conda create -n v3 python=3.13 nodejs=20
conda activate v3
```

To install basic Jupyter AI from scratch using the package collection in https://github.com/jupyter-ai-contrib:

```
pip install jupyter-ai-router jupyter-ai-persona-manager jupyter-ai-jupyternaut

git clone https://github.com/srdas/jupyter-ai-magic-commands.git
cd jupyter-ai-magic-commands
git switch first_magic
cd ..
pip install -e jupyter-ai-magic-commands
```

## Test

To test the new package, try the code in the notebook (attached): `magics_litellm.ipynb`
