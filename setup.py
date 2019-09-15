from setuptools import setup

setup(
    name="wow_realm_status",
    install_requires=[
        "attrs",
        "requests",
        "discord",
        "expiringdict",
    ],
    packages=["wow_realm_bot"],
    entry_points={
        'console_scripts':[
            'wow_bot=wow_realm_bot.bot:cli'
        ]
    },
    package_dir={"":"src/"},
    zip_safe=False,
)