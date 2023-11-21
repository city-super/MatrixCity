.. XRFeitoriaGear documentation master file, created by
   sphinx-quickstart on Fri Sep  2 17:12:45 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. |check| raw:: html

   <input checked=""  type="checkbox">

.. |check_| raw:: html

   <input checked=""  disabled="" type="checkbox">

.. |uncheck| raw:: html

   <input type="checkbox">

.. |uncheck_| raw:: html

   <input disabled="" type="checkbox">

Welcome to XRFeitoria-Gear's documentation!
=============================================


.. note::

   ``XRFeitoriaGear``: A Synthetic Data Factory for Machine Learning

.. image:: pics/demo.gif

- It's for AI Researchers who have no experience with Unreal Engine, and want to create synthetic datasets.

- Using this to generate synthetic data including rgb, segmentation, depth, normal map, camera parameters, 3d vertices, 3d bounding box, etc.
.. _Movie Render Queue: https://docs.unrealengine.com/5.0/en-US/render-cinematics-in-unreal-engine/

- This plugin is relied on the `Movie Render Queue`_ plugin, and is python-friendly.

|check_| Tested on Unreal Engine 5.0.3

|check_| Test on Unreal Engine 4.27.3

.. toctree::
   :maxdepth: 2

   Get-Started.md
   Tutorial.md

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Additional Resources
====================

.. toctree::
   :maxdepth: 2
   :caption: XRFeitoria-Gear Plugins Info

   Plugin.md

.. toctree::
   :maxdepth: 2
   :caption: Related Plugins

   Related.md