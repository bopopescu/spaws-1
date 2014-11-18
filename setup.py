from setuptools import setup, find_packages


name = "spaws"
version = "0.1"
requires = ["setuptools", "boto", "click"]


###########################################
# probably no need to edit anything below #
###########################################

kwargs = {
    "name": name,
    "version": version,
    "packages": find_packages(exclude=["tests", "tests.*"]),
    "install_requires": requires,
    "test_suite": "nose.collector",
    "tests_require": ["nose"],
    "include_package_data": True
}
kwargs["entry_points"] = {
    # buildout.cfg should be used instead to define entry points,
    # unless they are suitable to be installed globally
    "console_scripts": [
        name + " = " + name + ":main"
    ],
    "setuptools.installation": [
        "eggsecutable = " + name + ":main",
    ]
}
setup(**kwargs)
