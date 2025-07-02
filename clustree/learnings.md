# My learnings

## Matplotlib

### Axes

**Q: When plotting multiple images using matplotlib, what is the advantage of creating a new axes for each image?**

When plotting multiple images using matplotlib, creating a new axis for each image can have the following advantages:

1. Customization: Each axis can be customized independently, allowing you to control the properties of each image individually. For example, you can set different x and y limits, add different annotations, or set different aspect ratios for each image.
2. Layering: When multiple images are placed on the same axis, they can overlap and obscure one another. By creating a new axis for each image, you can ensure that each image is displayed on its own, separate layer.
3. Scaling: When multiple images are placed on the same axis, it can be difficult to adjust the scaling of each image individually. By creating a new axis for each image, you can control the scaling of each image independently, ensuring that each image is displayed at the desired size.
4. Organization: When multiple images are placed on the same axis, it can become difficult to distinguish between different images and keep track of their respective locations. By creating a new axis for each image, you can easily organize and keep track of multiple images in a more organized manner.

In general, creating a new axis for each image in a plot can provide greater control and flexibility in how the images are displayed, making it easier to create clear and informative visualizations.

### Coordinates

**Q: Why do we have to transform from data coordinates (scaled between xlim and ylim) to display coordinates when using matplotlib**

In Matplotlib, the xlim and ylim properties define the data coordinate limits for a plot. The data coordinates correspond to the actual values that are being plotted. The display coordinates, on the other hand, correspond to the pixels on the screen where the plot is displayed.

Transforming from data coordinates to display coordinates is necessary because the plotting process involves converting the data into a visual representation on the screen. In order to do this, Matplotlib needs to know how the data values map to specific pixels on the screen. This mapping is performed by transforming from data coordinates to display coordinates.

The transformation from data coordinates to display coordinates is performed by the plotting library, and is based on the aspect ratio, data range, and screen resolution. The aspect ratio and data range control the scaling of the data, while the screen resolution determines the number of pixels that are available to display the plot.

In summary, the transformation from data coordinates to display coordinates is an essential step in the plotting process, as it allows Matplotlib to translate the data values into a visual representation on the screen. This is necessary in order to display the plot correctly and to ensure that the data is correctly represented in the visual display.

### Spaces

**Q: What are all the coordinate spaces to consider when using matplotlib?**

In Matplotlib, there are three main coordinate spaces to consider:

Data space: The original coordinate space of your data. In this space, the data is represented by its numerical values.

Figure space: The space in which the entire figure is defined. The origin is the lower-left corner of the figure and the x- and y-coordinates increase as you move to the right and up, respectively.

Display space: The space in which the figure is displayed on the screen or saved to a file. The origin is the lower-left corner of the screen and the x- and y-coordinates increase as you move to the right and up, respectively.

It's important to note that the size and aspect ratio of the data and figure spaces are not necessarily the same as the size and aspect ratio of the display space. Transformations, such as transFigure, are used to convert between these spaces and ensure that the data is properly mapped to the figure and display spaces.


### Collections

**Q: What are containment tests used for in matplotlib.collections?**

Containment tests are used in matplotlib.collections to check if a given point or set of points are contained within a path or a collection of paths. The matplotlib.path.Path class provides the contains_point method which can be used for a single point, and the contains_points method for multiple points.


