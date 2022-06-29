### Explorative dashboard to analyze multidimensional data visually. [Live Demo](https://explorata.herokuapp.com) ![visitors](https://visitor-badge.glitch.me/badge?page_id=mohd-muzamil.IrisDashboard)

<ul>
  <li>Two views, i.e. Glyph View and Feature View, allow the user to interact with the dataset and select a specific data point which can then be compared with the remainder of the data points or lasso selected data points.
  <li>The menu in the sidebar allows the user to choose a few options like type and size of glyphs, hide/show the glyph labels, and hide/show the background grid and option to apply overlap removal.
  <li>The menu also has a search bar that allows users to search and select a specific datapoint using its ID.
  <li>Users can also vary the k-parameter to the K Nearest Neighbours (KNN) algorithm. The cluster value derived using KNN is used to add a stroke colour over the glyph.
  <li>The menu also allows users to choose between t-SNE and PCA dimensionality algorithms. The glyphs' positions over Glyphs-View are based on this DR algorithm.

### Steps(mac):
Create a virtual environment in the base folder and install dependencies into venv.\
`python3 -m venv venv`\
`source ./venv/bin/activate`    
`pip install -r requirements.txt`\
To run the dashboard, execute below command from base folder path.\
`python app.py`

![Dashboard_SS](https://user-images.githubusercontent.com/19529402/173147494-d04a76b7-9d89-47cf-834c-2fac78391c31.png)
(https://youtu.be/xHMLt8pg9e8)

