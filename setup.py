import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / "VERSION").open() as f:
    version = f.read()
with (root_dir / "README.md").open() as f:
    long_description = f.read()
with (root_dir / "requirements.in").open() as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="pypn_habref_api",
    version=version,
    description="Python lib related to Habref referential (INPN)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Parcs nationaux des Écrins et des Cévennes",
    maintainer_email="geonature@ecrins-parcnational.fr",
    url="https://github.com/PnX-SI/Habref-api-module",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    extras_require={
        "tests": [
            "pytest",
            "pytest-flask",
        ],
    },
    include_package_data=True,
    entry_points={
        "alembic": [
            "migrations = pypn_habref_api.migrations:versions",
        ],
    },
    zip_safe=False,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
