#!/usr/bin/env python
# -*- coding: utf-8 -*-

import skimage
import os
import numpy as np
import time
import rasterio

def stratification (input_indicator_path,input_LC,output_indicator,resolution,classes,indicator_name,stat_method,stat_stat):

    def shift_bb(coord=[[0, 0], ], dxm=18041000.0000000000000000, dym=9000000.0000000000000000):
        shifted = np.array([[elem[0] + dxm, -elem[1] + dym] for elem in coord])
        return shifted
    
    
    def get_bb_index(bb, px_size):
        f_bb = bb / float(px_size)
        bb_indx = np.floor(f_bb).astype(int)
        #bb_indx = np.ceil(f_bb).astype(int)
        #bb_indx = np.floor(f_bb).astype(int) + np.array([[1,1],[1,1]])
        #bb_indx = np.ceil(f_bb).astype(int) + np.array([[-1,-1],[-1,-1]])
        return bb_indx
    
    
    def nan_if_less(arr, value=0):
        return np.where(arr < value, np.nan, arr)
    
    
    # load bigTiff image obj
    def loadbigtiff(path):
        """load BigTiff from absolute path return array 2D"""
    
        print("Reading data for the indicator ...")
        image_array = skimage.io.imread(path, key=0)
        print("Raster indicator size: " + str(image_array.shape))
        print("Extracting data for tile i ...")
    
        return image_array
    
    
    # extract tiles data from bigtiff image using bb
    def extract_bb_data(btif_image, bbox, ppx=250, tpx=250):
        start = time.process_time()
        ext_ti = [[bbox['ll'][0], bbox['ur'][1]], [bbox['ur'][0], bbox['ll'][1]]]
        print("ext_ti: " + str(ext_ti))
        ext_ti_shifted = shift_bb(ext_ti)
        #ext_ti_shifted = shift_bb(ext_ti, dxm=0., dym=0.)
        #ext_ti_shifted = shift_bb(coord=ext_ti, dxm=1136703.4471957464702427, dym=6432839.4450090918689966)
        print("ext_ti_shifted: " + str(ext_ti_shifted))
        ti_bb_indx = get_bb_index(ext_ti_shifted, tpx)
        print("ext_ti_indexes: " + str(ti_bb_indx))
    
        # eg pop_tile
        tile_array = btif_image[ti_bb_indx[0][1]: ti_bb_indx[1][1], ti_bb_indx[0][0]:ti_bb_indx[1][0]]
        print ("tile_array extracted shape: " + str(tile_array.shape))

        print("LOG ---- "+str(tile_array.shape))
        # TODO replace all negative indicator values as null values
        tile_array = nan_if_less(tile_array, 0.)
        print("LOG --nanifless-- "+str(tile_array.shape))
        # pop_ti = np.array([[c for c in r[ti_bb_indx[0][0]:ti_bb_indx[1][0]]] for r in image[ti_bb_indx[0][1]:ti_bb_indx[1][1]]])
        print("Pop data extracted for tile i with dimensions:")
        print("Raster clip size: " + str(len(tile_array)) + " x " + str(len(tile_array[0])))
        print("Average Pop Tile i : " + str(np.nanmean(tile_array)))
        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
        print(elapsed_time)
    
        return tile_array
    
    
    def extract_all_tiles(tiles, btif_image, classes):
        indicator_values = {k: np.array([]) for k in classes}
    
        print("Indicator stats computation...")
        start = time.process_time()
    
        for tile_i in tiles:
            with rasterio.open(tile_i, 'r') as tile:
                print("Processing Tile: " + tile_i)
                bbox_tile = tile.bounds  # BoundingBox(left=358485.0, bottom=4028985.0, right=590415.0, top=4265115.0)
                tile_pixel_x = tile.transform[0]  # pixel size x
                tile_pixel_y = np.abs(tile.transform[4])  # pixel size y
                # Read as numpy array
                t_classes = tile.read(1)  # read first band
                print("Classes tile shape: " + str(t_classes.shape))
                print("Classes pixel size: " + str(tile_pixel_x))
                profile = tile.profile
    
            t_pixel = tile_pixel_x  ###TODO !!! using square pixels where size x = size y !!!
    
            # the coordinates of the tile are expressed in lower-left (ll) and upper-right (ur)
            # with rasterio open tile tiff and get extensions
            bbox = {'ll': [bbox_tile.left, bbox_tile.bottom],
                    'ur': [bbox_tile.right, bbox_tile.top]
                    }
    
            tile_data = extract_bb_data(btif_image, bbox, ppx=resolution, tpx=t_pixel)
    
            print("Indicator tile shape: " + str(tile_data.shape))
    
            # skimage.io.imsave(input_LC+'tile_data.tif', tile_data)
    
            for c in classes:
                td = np.array(t_classes, dtype=np.int32).astype(float)
                td[np.where(td != c)] = -1.0
                td[np.where(td == c)] = 1.0
    
                # np.savetxt(input_LC + 'class_'+str(c)+'.dat', td)
                # skimage.io.imsave(input_LC + 'class_'+str(c)+'.tif', td)
    
                t_prod = td * tile_data  # 2D array
                #print("T prod shape: " + str(t_prod.shape))
                #print(t_prod)
                # flatten only positive values
                if np.isnan(np.sum(t_prod)):
                    t_prod = t_prod[~np.isnan(t_prod)]  # remove nan elements
                indicator_class_i_values = t_prod[np.where(t_prod > 0.0)]  # array 1D
                # indicator_class_i_values = np.array([ fv for fv in t_prod.flatten() if fv is not np.nan and fv >= 1]) # array 1D
    
                indicator_values[c] = np.append(indicator_values[c], indicator_class_i_values)
    
                del td, t_prod, indicator_class_i_values
    
        # test print median from all tiles
        indicator_stats = {k: {'median': np.nanmedian(indicator_values[k]),
                               'mean': np.mean(indicator_values[k]),
                               'min': np.min(indicator_values[k]),
                               'max': np.max(indicator_values[k]),
                               #'std_dev': np.max(indicator_values[k]),
                               #'quantile': np.percentile(indicator_values, [25,50,75]) # returns quartiles
                               } for k in indicator_values.keys()}
        for k in sorted(indicator_stats.keys()):
            print("Stats for class "+str(k)+" :")
            print("Min value: " + str(indicator_stats[k]['min']))
            print("Max value: " + str(indicator_stats[k]['max']))
            print("Median value: " + str(indicator_stats[k]['median']))
            print("Mean value: " + str(indicator_stats[k]['mean']))
            #print("Quantile" + str(indicator_stats [25,75]['quantile']))
    
        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
        print(elapsed_time)
    
    
        return indicator_stats
    
    def stat_indicator(ind_name, btif_image, tiles,  indicator_stats,method="greater",stat="median",stat2="max",input_LC=os.getcwd()+'/'):
    
        print("Indicator replace with median processing...")
        start = time.process_time()
    
        for tile_i in tiles:
            with rasterio.open(tile_i, 'r') as tile:
                print("Processing Tile: " + tile_i)
                bbox_tile = tile.bounds  # BoundingBox(left=358485.0, bottom=4028985.0, right=590415.0, top=4265115.0)
                tile_pixel_x = tile.transform[0]  # pixel size x
                tile_pixel_y = np.abs(tile.transform[4])  # pixel size y
                # Read as numpy array
                t_classes = tile.read(1)  # read first band
                print("Classes tile shape: " + str(t_classes.shape))
                profile = tile.profile
    
            t_pixel = tile_pixel_x  ###TODO !!! using square pixels where size x = size y !!!
    
            # the coordinates of the tile are expressed in lower-left (ll) and upper-right (ur)
            # with rasterio open tile tiff and get extensions
            bbox = {'ll': [bbox_tile.left, bbox_tile.bottom],
                    'ur': [bbox_tile.right, bbox_tile.top]
                    }
    
            tile_data = extract_bb_data(btif_image, bbox, ppx=resolution, tpx=t_pixel)
    
            print("Indicator tile shape: " + str(tile_data.shape))
    
            tiles_sum = np.zeros(t_classes.shape)
            for c in classes:
                td = np.array(t_classes, dtype=np.int32).astype(float)
                td[np.where(td != c)] = -1.0
                td[np.where(td == c)] = 1.0
    
                t_prod = td * tile_data
                if np.isnan(np.sum(t_prod)):
                    t_prod[np.isnan(t_prod)] = 0 # replace nan with zeros
    
                #if method is greater then all values greater or equal to median = 1
                if method == "greater":
                    #TODO works only for positive indicators and stats!!!
                    t_prod[np.where(t_prod < indicator_stats[c][stat])] = 0
                    t_prod[np.where(t_prod >= indicator_stats[c][stat])] = 1
                elif method == "minor":
                    #TODO works only for positive indicators and stats!!!
                    # TODO solve the correct order to do it!!!
                    t_prod[np.where(t_prod > indicator_stats[c][stat])] = stat2
                    t_prod[np.where(t_prod <= indicator_stats[c][stat])] = 1
                    t_prod[np.where(t_prod >= indicator_stats[c][stat2])] = 0
                    pass
                elif method == "quantile":
                    # TODO select <=1 quartile and => 3 qaurtile (<25% or >75%)
                    pass
                else:
                    #TODO manage other options
                    pass
    
                tiles_sum += t_prod
    
            tif_out = input_LC + os.path.splitext(os.path.basename(tile_i))[0]+'_'+ind_name+'.tif'
            with rasterio.open(tif_out, 'w', **profile) as dst:
                # Write to disk
                dst.write(np.array([tiles_sum], dtype=np.uint8))
                print("Tile "+tif_out+" done.")
    
        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
        print(elapsed_time)
    
        return "done"

    tiles = [input_LC + f for f in os.listdir(input_LC) if os.path.splitext(f)[-1] == '.tif']

    population = loadbigtiff(input_indicator_path)
    print("Computing Indicator " + input_indicator_path)
    indicator_stats = extract_all_tiles(tiles, population, classes)

    stat_indicator(indicator_name, population, tiles, indicator_stats, method=stat_method, stat=stat_stat, input_LC=output_indicator)
    del population

    print('stratification done.')
    return 'Done'

# eg.

# input_indicator_path = os.getcwd() + "/input_raster/BUILT_UP/builtup.tif"
# input_LC = os.getcwd() + "/output/"
# output_indicator = os.getcwd() + '/indicator_median/'
# resolution = 250
# classes = [1, 2, 3, 4, 5, 6]
# indicator_name = 'population'
# stat_method = 'greater'
# stat_stat = 'median'
#
# stratification (input_indicator_path,input_LC,output_indicator,resolution,classes,indicator_name,stat_method,stat_stat)