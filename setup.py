from setuptools import setup

setup(name="gann",
      version=0.1,
      description="A tradingbot flowing the stock trading principles of William Delbert Gann.",
      include_package_data=True,
      zip_safe=True,
      install_requires=['socketIO-client==0.5.7.2'],
      packages=['gann', 'gann.tests'],
      scripts=['bin/compress_data']
)
