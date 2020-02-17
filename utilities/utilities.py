from io import BytesIO, StringIO
import pandas as pd
import numpy as np
from numba import jit
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
from skimage import measure

import re
import os

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def color_diff(c1, c2):
    '''
    compute the manhatten distance between colors c1 and colors c2
    c1 is of shape n by 3, c2 is of shape 1 by 3 or n by 3
    '''
    return np.sum(np.abs(c1-c2),axis=len(c1.shape)-1)

def get_most_common_color(sample_pixels):
    if len(sample_pixels.shape)==3:
        sample_pixels = sample_pixels.reshape(-1,3)
    
    unique_color, color_count = np.unique(sample_pixels, axis=0, return_counts = True)
    n = np.argsort(color_count)[-1]
    most_common_color = np.expand_dims(unique_color[n], axis=0)
    return most_common_color

def get_depth_text_from_img(im):
    ocr_data = pytesseract.image_to_data(im)
    df = pd.read_csv(StringIO(ocr_data), delimiter = '\t', index_col=False)
    df = df.dropna()
    df = df[df['conf']>80]

    final_col = ['l','t','w','h','d']
    df_final = pd.DataFrame([],columns=final_col)
    for i, row in df.iterrows():
        try:
            d = float(row['text'])
            df_final = df_final.append(dict(zip(final_col, [*row[['left','top','width','height']].values, d])) , ignore_index=True)
        except:
            pass
    depth_record = {'x': df_final['d'].to_list(), 'y': (df_final['t']+df_final['h']/2).to_list()}
    
    return depth_record, df_final

def remove_background_grid(im, mode='adaptive'):
    im_g = im.convert('L')
    im_np = 255-np.array(np.asarray(im_g))
    im_3c_np = np.array(np.asarray(im.convert('RGB')))

    background_color = get_most_common_color(im_3c_np)

    x_ticks_to_remove = find_grid_loc(im_np,axis=0)
    y_ticks_to_remove = find_grid_loc(im_np,axis=1)
    if mode=='adaptive':
        for x in x_ticks_to_remove:
            im_3c_np = remove_grid_at_loc_adaptive(im_3c_np, x, background_color, axis=0)

        for y in y_ticks_to_remove:
            im_3c_np = remove_grid_at_loc_adaptive(im_3c_np, y, background_color, axis=1)
    elif mode=='aggressive':
        im_3c_np[y_ticks_to_remove,:] = background_color
        im_3c_np[:,x_ticks_to_remove] = background_color

    new_im = Image.fromarray(im_3c_np)
    return new_im

def color_filter(im, picked_color, mode='keep'):
    im = im.convert('RGB')
    picked_color = np.array([[picked_color]])
    im_np= np.array(np.asarray(im))
    if mode =='keep':
        i, j = np.where(np.sum(np.abs(im_np - picked_color), axis=2)>30)
    else:
        i, j = np.where(np.sum(np.abs(im_np - picked_color), axis=2)<15)
    im_np[i,j]=np.array([255,255,255])
    return  Image.fromarray(im_np)

def region_removal(im, clicked_coord, picked_color):
    im_np = np.array(im.convert('RGB'))
    background_color = get_most_common_color(im_np)
    mask = np.array(color_diff(im_np, np.array(picked_color))<20, dtype=np.int)
    labeled_mask = measure.label(mask, background=False, connectivity=2)
    label = labeled_mask[clicked_coord[1],clicked_coord[0]]
    rp = measure.regionprops(labeled_mask)
    props = rp[label-1]
    coords = props.coords
    i = coords[:,0].flatten()
    j = coords[:,1].flatten()
    im_np[i,j] = background_color
    return Image.fromarray(im_np)

def find_grid_loc(im, axis=0):
    cum_pixel = im.sum(axis=axis)
    cum_pixel_base = lowPassFilter(cum_pixel,fc=0.01)
    pixel_to_remove = np.where(cum_pixel > cum_pixel_base * 1.2)[0]
    return pixel_to_remove

def lowPassFilter(signal, fc=0.01):
    #fc = .01
    b = 0.1
    N = int(np.ceil(4 / b))
    if not N % 2: N += 1
    n = np.arange(N)
    halfN = (N - 1) // 2

    sinc_func = np.sinc(2 * fc * (n - (N - 1) / 2.))
    sinc_func = sinc_func / sinc_func.sum()

    signal_base = np.convolve(signal, sinc_func)
    signal_base = signal_base[halfN:-halfN]

    return signal_base

def remove_grid_at_loc_adaptive(im, loc, background_color, axis=0):
    line = im[:, loc] if axis==0 else im[loc]
    grid_color = get_most_common_color(line)
    if axis==0:
        ys = np.where(color_diff(im[:,loc],grid_color)<10)[0]
        im[ys,loc] = background_color
    else:
        xs = np.where(color_diff(im[loc],grid_color)<10)[0]
        im[loc,xs] = background_color
    return im

@jit(nopython=True)
def computeCost(raw_invert, pixel_weight, maxDX, goodDist=10):
    '''
    trace curve using dynamic programming, return cost and path information
    '''
    (ny, nx) = raw_invert.shape
    COST = 1e10 * np.ones((ny, nx))

    COST[0, :] = raw_invert[0, :] * pixel_weight
    for iy in range(1, ny):
        for ix in range(nx):
            for j in range(max(0, ix - maxDX), min(nx, ix + maxDX + 1)):
                #        A[iy,ix] = min_(j) A[iy-1,j]+cost((iy-1,j)->(iy,ix))
                #       cost((iy-1,j)->(iy,ix))
                dist = abs(j - ix)
                dist_penalize = 1 if dist < goodDist else dist
                tmp = COST[iy - 1, j] + dist_penalize
                if tmp < COST[iy, ix]:
                    COST[iy, ix] = tmp
        COST[iy, :] = COST[iy, :] + raw_invert[iy, :] * pixel_weight
    return COST

@jit(nopython=True)
def tracePath(COST, w, mode = 'mid'):
    ny,nx = COST.shape
    PATH = np.zeros(ny)
    for iy in range(ny-1,-1,-1):
        if iy==ny-1:
            xmin, xmax = 0, nx
        else:
            xmin = max(0, int(PATH[iy+1]-w))
            xmax = min(nx, int(PATH[iy+1]+w))
        min_cost = COST[iy,xmin:xmax].min()
        l_candi = np.where(COST[iy,xmin:xmax]==min_cost)[0]+xmin
        if mode == 'left':
            PATH[iy] = l_candi[0]
        elif mode == 'right':
            PATH[iy] = l_candi[-1]
        else:
            PATH[iy] = l_candi[len(l_candi)//2]
    
    return PATH

def CurveTraceDynamicProgramming(im_gray, trace_mode = 'mid', smooth_mode = 1):

    (ny, nx) = im_gray.shape
    #kernel = np.hanning(3)  # a Hanning window with width 10
    #kernel /= kernel.sum()  # normalize the kernel weights to sum to 1
    #raw_smooth = ndimage.convolve1d(im_gray, kernel, 1) / 255.0
    im_gray = (im_gray-im_gray.min())/(im_gray.max()-im_gray.min()) #scale to 0-1
    
    maxDX_list =  [15, 25, 35, 50]
    maxDXfrac_list =  [15, 10, 6, 4]
    goodDX_list = [10, 15, 25, 30]
    goodDXfrac_list = [24, 15, 8, 4]

    maxDX = max(maxDX_list[smooth_mode], nx//maxDXfrac_list[smooth_mode])
    goodDist = max(goodDX_list[smooth_mode], nx//goodDXfrac_list[smooth_mode])
    
    print(maxDX, goodDist)

    Cost = computeCost(im_gray, pixel_weight= 20.0, maxDX = maxDX, \
                        goodDist = goodDist)

    # Cost, BestPath = computeBestPath(raw_smooth, maxDX = maxDX, \
    #                                  goodDist = goodDist, pixel_weight= 100.0)

    BestPath = tracePath(Cost, maxDX, mode = trace_mode)

    BestPath = [int(x) for x in BestPath]
    
    return BestPath

def trace_curve(im, trace_mode, trace_smooth_mode, method='dynamic_programming'):

    im_color = np.asarray(im.convert('RGB'))
    
    im_reduced = reduce_color_kmean(im, n_colors=4)
    im_np = np.array(im_reduced.convert('L'))
    
    x = CurveTraceDynamicProgramming(im_np, trace_mode = trace_mode, smooth_mode = trace_smooth_mode)
    
    y = list(range(len(x)))
    curve_data = {'x': x, 'y': y}
    curve_color = get_most_common_color(im_color[y,x]).flatten().tolist()
    fit_color = [255-c for c in curve_color]
    if sum(fit_color)>200*3: #too bright to be seen!
        fit_color[0]=0
    fit_color = tuple(fit_color)
    print(fit_color)
    draw = ImageDraw.Draw(im)
    xy = list(zip(x, y))
    draw.line(xy, fill=fit_color, width=2)

    return im, curve_data


def merge_digitization_data(old, new):
    y0, y1 = np.array(old['y']), np.array(new['y'])
    x0, x1 = np.array(old['x']), np.array(new['x'])

    new_y = np.unique(np.concatenate((y0,y1)))
    new_x = np.zeros_like(new_y)

    ind_old = np.searchsorted(new_y, y0)
    new_x[ind_old] = x0
    ind_new = np.searchsorted(new_y, y1)
    new_x[ind_new] = x1
    return {'x': new_x.tolist(), 'y': new_y.tolist()}


def reduce_color_kmean(im, n_colors=16):
    im = im.convert('RGB')
    im_np = np.array(im, dtype=np.float64)/255
    (w, h, d) = im_np.shape
    im_np_1d = im_np.reshape(w*h,d)
    color_sample = shuffle(im_np_1d, random_state=0)[:2000]
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(color_sample)

    labels = kmeans.predict(im_np_1d).reshape(w,h)
    im_reduced = kmeans.cluster_centers_[labels]
    
    return Image.fromarray(np.uint8(im_reduced*255))