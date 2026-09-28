---
name: geojson-mapbox-spatial-analysis
metadata:
  category: Geospatial and GIS Engineering
description: Perform in-browser spatial analysis, GeoJSON feature processing, Turf.js geometric computations (buffers, convex hulls, Voronoi polygons, centroids), and Mapbox GL JS / MapLibre vector tile styling. Trigger when rendering interactive map layers, visualizing spatial datasets, or computing client-side geographic boundaries.
compatibility: Mapbox GL JS v2+, MapLibre GL v3+, Turf.js v7+, GeoJSON RFC 7946
---

# GeoJSON & Mapbox Spatial Analysis Skill Guide

This skill governs client-side geospatial data manipulation, vector tile rendering, and spatial geometric algorithms using Turf.js and Mapbox GL / MapLibre.

---

## 1. GeoJSON Client Pipeline

```text
[ Raw GeoJSON FeatureCollection ] (RFC 7946)
             |
             v
[ Turf.js Geospatial Processing Engine ]
  |-- Calculate Centroids & Bounding Boxes
  |-- Generate Buffer Zones (e.g. 500m catchment)
  |-- Convex Hull / Voronoi Tessellation
             |
             v
[ Mapbox GL / MapLibre Vector Renderer ]
  |-- Add Source: type: 'geojson', cluster: true
  |-- Choropleth Fill Layer with Data-Driven Expressions
  |-- Symbol & Cluster Count Overlays
```

---

## 2. Production Implementation Patterns

### A. Client-Side Spatial Analysis with Turf.js (TypeScript)

```typescript
import * as turf from "@turf/turf";
import type { FeatureCollection, Point, Polygon } from "geojson";

export interface SpatialCoverageResult {
  hull: turf.Feature<Polygon>;
  centroid: turf.Feature<Point>;
  bufferedAreaKm2: number;
}

/**
 * Calculates spatial catchment area and convex hull around a cluster of store points.
 */
export function analyzeClusterCoverage(points: FeatureCollection<Point>, bufferRadiusKm: number = 2.0): SpatialCoverageResult {
  if (!points.features || points.features.length === 0) {
    throw new Error("Cannot analyze empty feature collection");
  }

  // 1. Calculate geographic centroid
  const centroid = turf.centroid(points);

  // 2. Compute minimum bounding convex hull
  const hull = turf.convex(points);
  if (!hull) {
    throw new Error("At least 3 non-collinear points required for convex hull");
  }

  // 3. Generate buffer around all points and dissolve into single polygon
  const buffered = turf.buffer(points, bufferRadiusKm, { units: "kilometers" });
  const dissolved = turf.dissolve(buffered);

  // 4. Calculate total square kilometer area
  const areaM2 = turf.area(dissolved);
  const bufferedAreaKm2 = areaM2 / 1_000_000;

  return {
    hull,
    centroid,
    bufferedAreaKm2,
  };
}
```

### B. High-Performance Mapbox Layer & Clustering Setup

```typescript
import mapboxgl from "mapbox-gl";

export function initializeClusteredMap(map: mapboxgl.Map, geojsonUrl: string) {
  map.on("load", () => {
    // 1. Add clustered GeoJSON source
    map.addSource("incidents", {
      type: "geojson",
      data: geojsonUrl,
      cluster: true,
      clusterMaxZoom: 14, // Max zoom to cluster points on
      clusterRadius: 50,  // Radius of each cluster when clustering points (pixels)
    });

    // 2. Clustered Circle Layer with Data Expressions
    map.addLayer({
      id: "clusters",
      type: "circle",
      source: "incidents",
      filter: ["has", "point_count"],
      paint: {
        "circle-color": [
          "step",
          ["get", "point_count"],
          "#51bbd6", 20,
          "#f1f075", 100,
          "#f28cb1"
        ],
        "circle-radius": [
          "step",
          ["get", "point_count"],
          18, 20,
          24, 100,
          32
        ],
      },
    });

    // 3. Cluster Count Label Layer
    map.addLayer({
      id: "cluster-count",
      type: "symbol",
      source: "incidents",
      filter: ["has", "point_count"],
      layout: {
        "text-field": "{point_count_abbreviated}",
        "text-font": ["DIN Offc Pro Medium", "Arial Unicode MS Bold"],
        "text-size": 12,
      },
    });

    // 4. Unclustered Individual Point Layer
    map.addLayer({
      id: "unclustered-point",
      type: "circle",
      source: "incidents",
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-color": "#11b4da",
        "circle-radius": 6,
        "circle-stroke-width": 1,
        "circle-stroke-color": "#fff",
      },
    });
  });
}
```

---

## 3. Best Practices & Optimization

1. **RFC 7946 Standard Coordinate Order:** Always enforce `[longitude, latitude]` order. Never invert to `[latitude, longitude]`.
2. **GeoJSON Simplification:** When transmitting large polygon boundaries to the browser, apply Douglas-Peucker simplification (`turf.simplify`) with tolerance thresholds to reduce payload size by up to 80%.
3. **Avoid Re-Adding Sources:** Update data in place using `source.setData(newGeoJson)` rather than calling `map.removeSource` and `map.addSource`.
