import unittest
from qgis.core import QgsVectorLayer
from python.engine.constructors import Constructor

class TestConstructors(unittest.TestCase):

    def test_layerFromWKT(self):
        """Test the layerFromWKT function."""
        wkt_list = [
            "POINT(1 1)",
            "POINT(2 2)",
            "POINT(3 3)"
        ]
        epsg = 4326
        layer = Constructor.layerFromWKT("Point", wkt_list, epsg)

        # Check if the layer is created
        self.assertIsInstance(layer, QgsVectorLayer)
        self.assertEqual(layer.featureCount(), len(wkt_list))

    def test_bboxFromLayer(self):
        """Test the bboxFromLayer function."""
        wkt_list = [
            "POINT(1 1)",
            "POINT(2 2)",
            "POINT(3 3)"
        ]
        epsg = 4326
        layer = Constructor.layerFromWKT("Point", wkt_list, epsg)

        # Get the bounding box
        bbox = Constructor.bboxFromLayer(layer)

        # Check if the bounding box is correct
        self.assertEqual(len(bbox), 5)  # xmin, ymin, xmax, ymax, epsg
        self.assertEqual(bbox[4], "EPSG:4326")

if __name__ == "__main__":
    unittest.main()