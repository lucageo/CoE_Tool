from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import fiona
import itertools
import os
import time

output = 'D:/Python_projects/git/convergence/output'
vector_in = os.path.join(output, 'LC_vector3.shp')
vector_out = os.path.join(output, 'LC_dissolved.shp')


def dissolve_vector(vector_in, vector_out):

    start = time.process_time()
    print('Dissolving...')

    with fiona.open(vector_in) as input:
        # preserve the schema of the original shapefile, including the crs
        meta = input.meta
        with fiona.open(vector_out, 'w', **meta) as output:
            # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'raster_val' field
            e = sorted(input, key=lambda k: k['properties']['raster_val'])
            # group by the 'VALUE' field
            for key, group in itertools.groupby(e, key=lambda x:x['properties']['raster_val']):
                properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
                # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
                output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})

    el_time = (time.process_time() - start)
    elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
    print(elapsed_time)