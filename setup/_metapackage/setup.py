import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-connector-documenso",
    description="Meta package for open-synergy-ssi-connector-documenso Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_connector_documenso',
        'odoo14-addon-ssi_connector_documenso_signing',
        'odoo14-addon-test_ssi_connector_documenso_signing',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
