from setuptools import setup, find_packages


kwargs = {
    "name": "spaws",
    "version": "0.1",
    "packages": find_packages(exclude=["tests", "tests.*"]),
    "install_requires": ["setuptools", "boto", "click"],
    "test_suite": "nose.collector",
    "tests_require": ["nose"],
    "include_package_data": True
}
kwargs["entry_points"] = {
    # buildout.cfg should be used instead to define entry points,
    # unless they are suitable to be installed globally
    "console_scripts": [
        "spaws = spaws:main",
        "spark-ec2 = spaws.spark_ec2:main"
    ],
    "setuptools.installation": [
        "eggsecutable = spaws:main",
    ]
}
setup(**kwargs)
