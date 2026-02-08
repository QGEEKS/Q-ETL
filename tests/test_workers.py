import unittest
from qgis.core import QgsVectorLayer
from python.engine.workers import Worker

class TestWorkers(unittest.TestCase):

    def setUp(self):
        """Set up a sample layer for testing."""
        self.sample_layer = QgsVectorLayer("Point?crs=epsg:4326", "test_layer", "memory")
        self.sample_layer.dataProvider().addAttributes([
            QgsField("id", QVariant.Int),
            QgsField("name", QVariant.String)
        ])
        self.sample_layer.updateFields()

        # Add sample features
        features = []
        for i in range(3):
            feature = QgsFeature()
            feature.setAttributes([i, f"Name_{i}"])
            feature.setGeometry(QgsGeometry.fromWkt(f"POINT({i} {i})"))
            features.append(feature)
        self.sample_layer.dataProvider().addFeatures(features)
        self.sample_layer.updateExtents()

    def test_addxyfieldstolayer(self):
        """Test the addxyfieldstolayer function."""
        result_layer = Worker.Vector.addxyfieldstolayer(self.sample_layer, "EPSG:4326")
        self.assertIsInstance(result_layer, QgsVectorLayer)
        self.assertTrue(result_layer.fields().indexFromName("x") != -1)
        self.assertTrue(result_layer.fields().indexFromName("y") != -1)

    def test_convexhull(self):
        """Test the convexhull function."""
        result_layer = Worker.Vector.convexhull(self.sample_layer)
        self.assertIsInstance(result_layer, QgsVectorLayer)
        self.assertEqual(result_layer.featureCount(), 1)  # Convex hull should produce one feature

    def test_concavehull(self):
        """Test the concavehull function."""
        result_layer = Worker.Vector.concavehull(self.sample_layer, alpha=0.5, holes=False, multigeom=False)
        self.assertIsInstance(result_layer, QgsVectorLayer)
        self.assertEqual(result_layer.featureCount(), 1)  # Concave hull should produce one feature

    def test_extractvertices(self):
        """Test the extractvertices function."""
        result_layer = Worker.Vector.extractvertices(self.sample_layer)
        self.assertIsInstance(result_layer, QgsVectorLayer)
        self.assertGreater(result_layer.featureCount(), self.sample_layer.featureCount())  # More vertices than features

    def test_multiringconstantbuffer(self):
        """Test the multiringconstantbuffer function."""
        result_layer = Worker.Vector.multiringconstantbuffer(self.sample_layer, rings=3, distance="10")
        self.assertIsInstance(result_layer, QgsVectorLayer)
        self.assertEqual(result_layer.featureCount(), 3 * self.sample_layer.featureCount())  # 3 rings per feature

if __name__ == "__main__":
    unittest.main()