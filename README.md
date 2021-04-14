# napari-manual-classifier

[![License](https://img.shields.io/pypi/l/napari-manual-classifier.svg?color=green)](https://github.com/napari/napari-manual-classifier/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-manual-classifier.svg?color=green)](https://pypi.org/project/napari-manual-classifier)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-manual-classifier.svg?color=green)](https://python.org)

Simple napari widget for annotating classes for each slice of an nd-image

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using with [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/docs/plugins/index.html
-->

## Installation

You can install `napari-manual-classifier` via [pip]:

    pip install napari-manual-classifier

## Usage

Import using:

	from napari_manual_classifier import build_widget

Start the widget by running:

	build_widget(viewer)

`viewer` is a napari viewer instance. `build_widget` also takes optional arguments:

|argument|description|
|--------|-----------|
|metadata_levels|list of names for the leading dimensions of the image, used for formatting dataframe output|
|initial_classes|list of class names to initialize as options|
	

If no layers are open when initializing the widget, a dialog box will open to select a desired image.

Label the displayed image slice by either clicking the desired class button or pressing the corresponding number on the keyboard. This will automatically advance to display the next slice; however, you can always go back and re-classify a slice (warning will be displayed).

Additional class options can be added by typing the class label in the text box in the "classes" box, and then clicking `Add class`.

Once finished, click the `Save...` button in the widget; this opens a dialog box to save a table with the resulting classifications.

## Contributing

Contributions are very welcome.

## License

Distributed under the terms of the [MIT] license,
"napari-manual-classifier" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/lukebfunk/napari-manual-classifier/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/