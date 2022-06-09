##Explorative dashboard to analyze multidimensional data visually.
Two views, i.e. Glyph View and Feature View, allow the user to interact with the dataset and select a specific data point which can then be compared with the remainder of the data points or lasso selected data points.
The menu in the sidebar allows the user to choose a few options like Glyph type and size of the glyph, hide/show the glyph labels, and hide/show the grid to show its 2D projections.
The menu also has a search bar that allows users to search and select a specific using their ID quickly.
Users can also vary the k-parameter to the K Nearest Neighbours (KNN) algorithm. The cluster value derived using KNN is used to add a stroke colour over the glyph.
The menu also allows users to choose between t-SNE and PCA dimensionality algorithms. The glyphs' positions over Glyphs View are based on this DR algorithm.
