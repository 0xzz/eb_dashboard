from io import BytesIO, StringIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import PIL.ImageOps
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.interpolate import interp1d


import base64
import os
import shutil
import copy

from utilities import get_depth_text_from_img, remove_background_grid, \
                        rgb2hex, color_filter, trace_curve, \
                        merge_digitization_data, reduce_color_kmean, \
                        region_removal

class UserLogImageSession:
    '''
    properties and methods of a user working-in-progress session
    '''

    def __init__(self, session_id, raw_img_content, raw_img_name, img_lastmodifed):

        self.dir_path = os.path.join('sessions',session_id)
        if os.path.exists(self.dir_path):
            shutil.rmtree(self.dir_path)
        os.makedirs(self.dir_path)
            
        self.session_id = session_id

        self.ext = raw_img_name.split('.')[1]
        self.raw_img_name = raw_img_name
        self.well_name = raw_img_name.split('.')[0]
        self.img_lastmodifed = img_lastmodifed
        self.raw_path = os.path.join('sessions',session_id,'raw.'+self.ext)

        img64 = raw_img_content.split(',',1)[1]
        img64_decoded = base64.b64decode(img64)
        im = Image.open(BytesIO(img64_decoded))
        self.raw_size = im.size
        print('Raw Image size = ', self.raw_size)
        with open(self.raw_path, 'wb') as f:
            f.write(img64_decoded)

        self.actions = []
        self.saved_results = []
        self.las_name = self.well_name + ".las"
        self.las_path = os.path.join('sessions', self.session_id,self.las_name)

        self.depth_entry_name = None
        self.depth_regressor = LinearRegression()
        self.current_coords = {'x':-1, 'y':-1}
        self.last_selected_color = [255,255,255]
        self.last_clicked_crop_coords = [0,0]

    def __save_new_tmp_crop(self, tmp_Img, region):
        #clear actions
        for action in self.actions:
            if os.path.isfile(action['path']):
                os.remove(action['path'])
        self.actions = []
        self.__save_new_action_and_processed_crop( \
            tmp_Img, action_name = 'new crop', region = region)

    def __save_new_action_and_processed_crop(self, tmp_Img, action_name, region = None, data = None):
        tmp_ind = len(self.actions) + 1
        new_tmp_path = os.path.join('sessions', self.session_id,\
            'tmp_{:d}.{:s}'.format(tmp_ind, self.ext))
        tmp_Img.save(new_tmp_path)
        if region is None:
            region = self.actions[-1]['region']
        self.actions.append({
            'name': action_name,
            'region': region,
            'data': data,
            'path': new_tmp_path})

    def update_click_coords(self, new_coords):
        '''
        self.current_coords is a size-1 queue.
        if it is empty, push new_coords into it, and return -2
        otherwise, generate a crop, reset the current_coords queue, and return 1
        '''

        if self.current_coords['x']==-1:
            self.current_coords = new_coords
            return -2
        
        x1, x2 = self.current_coords['x'], new_coords['x']
        y1, y2 = self.current_coords['y'], new_coords['y']
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        raw_img = Image.open(self.raw_path)
        im1 = raw_img.crop((x1, y1, x2, y2))
        self.__save_new_tmp_crop(im1, region = {'x':[x1,x2],'y':[y1,y2]})
        self.current_coords = {'x':-1, 'y':-1}
        return 1

    def extract_depth(self):
        im = Image.open(self.actions[-1]['path'])
        im_w, _ = im.size
        depth_record, depth_record_df = get_depth_text_from_img(im)
        font = ImageFont.truetype('segoeuib.ttf',int(24*im_w/90))
        draw = ImageDraw.Draw(im)
        for _, row in depth_record_df.iterrows():
            l,t,w,h,d = row[['l','t','w','h','d']].values
            draw.line((l,t+h/2,l+w,t+h/2), (250,40,40))
            draw.line((l+w/2,t,l+w/2,t+h), (250,40,40))
            draw.line((l,t,l+w,t,l+w,t+h,l,t+h,l,t), (250,40,40))
            draw.text((l,t+h), str(d), (250,40,40), font=font)
        self.__save_new_action_and_processed_crop(im, 'extract depth', data = depth_record)

    def remove_grid(self, mode):
        im_crop = Image.open(self.actions[-1]['path'])
        processed_im = remove_background_grid(im_crop, mode = mode)
        self.__save_new_action_and_processed_crop(processed_im, f'remove grid {mode}')

    def to_grayscale(self):
        im_crop = Image.open(self.actions[-1]['path'])
        processed_im = im_crop.convert('L').convert('RGB')
        self.__save_new_action_and_processed_crop(processed_im, 'to grayscale')

    def increase_contrast(self):
        im_crop = Image.open(self.actions[-1]['path'])
        enhancer = ImageEnhance.Contrast(im_crop)
        processed_im = enhancer.enhance(1.5)
        self.__save_new_action_and_processed_crop(processed_im, 'increase contrast')

    def sharpen(self):
        im_crop = Image.open(self.actions[-1]['path'])
        enhancer = ImageEnhance.Sharpness(im_crop) 
        processed_im = enhancer.enhance(1.5)
        self.__save_new_action_and_processed_crop(processed_im, 'sharpen')
    
    def denoise(self):
        #img = cv.imread(self.actions[-1]['path'])
        #im = 
        return 

    def reduce_color(self):
        im_crop = Image.open(self.actions[-1]['path']).convert('RGB')
        n_unique_color = np.unique(np.asarray(im_crop).reshape(-1,3),axis=0).shape[0]
        n_reduced_color = min(32,max(2, n_unique_color//2))
        processed_im = reduce_color_kmean(im_crop, n_colors = n_reduced_color)
        self.__save_new_action_and_processed_crop(processed_im, 'reduce color')
        
    def undo(self):
        if len(self.actions)==0:
            return
        last_path = self.actions[-1]['path']
        os.remove(last_path)
        self.actions.pop()

    def get_latest_crop_based64(self):
        if len(self.actions)==0:
            return ''
        else:
            with open(self.actions[-1]['path'], "rb") as img_f:
                img_encoded_string = base64.b64encode(img_f.read())
            return 'data:image/png;base64,{}'.format(img_encoded_string.decode())

    def click_at_coord(self, coords):
        im_crop = Image.open(self.actions[-1]['path']).convert('RGB')
        r, g, b = im_crop.getpixel((coords['x'], coords['y']))
        self.last_selected_color = [r,g,b]
        self.last_clicked_crop_coords = [coords['x'], coords['y']]
        return rgb2hex(r,g,b)

    def filter_img_by_picked_color(self, mode='keep'):
        im_crop = Image.open(self.actions[-1]['path'])
        processed_im = color_filter(im_crop, self.last_selected_color, mode)
        self.__save_new_action_and_processed_crop(processed_im, 'select color', data = self.last_selected_color)

    def remove_region_by_picked_color(self):
        im_crop = Image.open(self.actions[-1]['path'])
        processed_im = region_removal(im_crop, self.last_clicked_crop_coords, self.last_selected_color)
        self.__save_new_action_and_processed_crop(processed_im, 'remove region', data = self.last_clicked_crop_coords)

    def smart_trace(self, trace_mode, trace_smooth_mode):
        im_crop = Image.open(self.actions[-1]['path'])
        tm_dict = ['left','mid','right']
        tm = tm_dict[trace_mode]
        
        processed_im, curve_data = trace_curve(im_crop, \
                    tm, trace_smooth_mode,\
                    method='dynamic_programming')
        #adjust to offset
        
        self.__save_new_action_and_processed_crop(processed_im, 'curve trace', data = curve_data)

    def save_last_action(self, curve_name, curve_unit, curve_range, islog):
        if type(curve_name) is str and len(curve_name)>0 and len(self.actions)!=0:
            action = self.actions[-1]
            action_name, region = action['name'], action['region']
            if action_name == 'curve trace':
                return self._add_result({
                        'name': curve_name, 
                        'unit': curve_unit,
                        'region':region,
                        'range': curve_range,
                        'islog': islog,
                        'data': copy.deepcopy(action['data']),
                        'type': 'curve'
                    })
            elif action_name == 'extract depth':
                return self._add_result({
                        'name': curve_name, 
                        'unit': curve_unit,
                        'region':region,
                        'range':[0,1],
                        'islog':False,
                        'data': copy.deepcopy(action['data']),
                        'type': 'depth'
                    })
        return 'No new data saved'

    def save_last_action_depth(self, curve_name, curve_unit, curve_range):
        if type(curve_name) is str and len(curve_name)>0 and len(self.actions)!=0:
            action = self.actions[-1]
            action_name, region = action['name'], action['region']
            if action_name == 'extract depth':
                return self._add_result({
                        'name': curve_name, 
                        'unit': curve_unit,
                        'region':region,
                        'range':[0,1],
                        'islog':False,
                        'data': copy.deepcopy(action['data']),
                        'type': 'depth'
                    })
            elif action_name == 'new crop':
                curve_range = [float(c) for c in curve_range]
                manual_depth_record = [list(item) for item in zip(region['y'],curve_range)]
                manual_depth_record = {'x': curve_range, 'y': region['y']}
                
                return self._add_result({
                        'name': curve_name, 
                        'unit': curve_unit,
                        'region':region,
                        'range':curve_range,
                        'islog':False,
                        'data': manual_depth_record,
                        'type': 'depth'
                    })  
            return 'No new data saved.'

    def _add_result(self, entry):
        '''
        add new entry to saved results
        1. get absolute pixel coordinates of the curve
        2. get depth-value of the curve if depth is saved
        3. update other curves' depth-value if depth is just provided
        '''
        #first, convert data to full-image coordinate by adjust xy to xy-offset
        y_offset = entry['region']['y'][0]
        x_offset = entry['region']['x'][0]
        print(f"y_offset = {y_offset}, x_offset={x_offset}")
        print(f"raw x range {min(entry['data']['x'])}-{max(entry['data']['x'])}")
        print(f"raw y range {min(entry['data']['y'])}-{max(entry['data']['y'])}")

        entry['data']['y'] = [y+y_offset for y in entry['data']['y']]
        if entry['type']!='depth': #when type is depth, ['data']['x'] records the actual depth information. No offset adjustment is needed
            entry['data']['x'] = [x+x_offset for x in entry['data']['x']]
        print('After offset adjustment:')
        print(f"raw x range {min(entry['data']['x'])}-{max(entry['data']['x'])}")
        print(f"raw y range {min(entry['data']['y'])}-{max(entry['data']['y'])}")

        result_added = False
        #merge or override
        for item in self.saved_results:
            if item['name'] == entry['name']:
                if entry['type'] == 'depth' or item['unit'] != entry['unit'] or \
                   item['islog']!=entry['islog']: #override
                    for key in {'unit','region','data','type','islog','range'}:
                        item[key] = copy.deepcopy(entry[key])
                    self._update_saved_sequence(item)
                    msg = f"{entry['name']} information overrided."
                    result_added = True
                    break
                else: #merge
                    item['data'] = merge_digitization_data(old = item['data'], new = entry['data'])
                    self._update_saved_sequence(item)
                    msg = f"{entry['name']} information merged with previous saved data."
                    result_added = True
                    break
        if not result_added:
            #new record
            self.saved_results.append(entry)
            self._update_saved_sequence(entry)
            msg = f"{entry['name']} information is saved."

        print([n['name'] for n in self.saved_results])
        return msg


    def _update_saved_sequence(self, entry):
        '''
            1. update value
            2. get depth of the curve if depth is saved
            3. update other curves' depth if the new entry is depth
        '''
        if entry['type']=='depth':
            self._update_depth_regressor(entry)
            for item in self.saved_results:
                self._update_saved_item_depth(item) #update all curve with new depth regressor
        else:
            entry['digitized_data'] = {'depth':None, 'value': self._get_curve_values(entry)}
            self._update_saved_item_depth(entry)
        return

    def _update_saved_item_depth(self, item):
        '''
            2. get depth-value of the curve if depth is saved
        '''
        if item['type'] == 'depth': #no need to update
            return
        try:
            interped_depth = self.depth_regressor.predict(np.array(item['data']['y']).reshape(-1,1))
            item['digitized_data']['depth'] = interped_depth.flatten().tolist()
        except:
            pass
        return

    def remove_saved_result(self, series_to_remove):
        self.saved_results = [s for s in self.saved_results if s['name'] not in series_to_remove]
        return


    def _get_curve_values(self, item):
        print(item['name'], ' curve range :',item['range'], ' islog=', item['islog'])
        lb, rb = item['range']
        x_pixel_range = item['region']['x']
        print('x pixel coordinate on raw image: ', x_pixel_range)
        if item['islog']:
            lb, rb = np.log(lb), np.log(rb)
        x = np.array(item['data']['x'])
        #scale to 0-1
        x = (x-x_pixel_range[0])/(x_pixel_range[1]-x_pixel_range[0])
        #scale to lb,rb
        x = x*(rb-lb)+lb
        if item['islog']:
            x = np.exp(x)
        return x.flatten().tolist()
        
    
    def _update_depth_regressor(self, depth_item):
        y_pixel = np.array(depth_item['data']['y']).reshape(-1,1)
        d_value = np.array(depth_item['data']['x']).reshape(-1,1)
        self.depth_regressor.fit(y_pixel, d_value) #vertical pixel to depth
        self.depth_entry_name = depth_item['name']
        return
        
    def update_summary_df(self):
        '''
        name, type, unit, depth range, value range, log scale
        '''
        col_names = ['name','type','depth range','value-range','unit','log scale']
        df_dict = {}
        for i, item in enumerate(self.saved_results):
            if item['type']=='depth':
                depth_range = '{:.0f}-{:.0f}'.format(min(item['data']['x']),max(item['data']['x']))
                df_dict[i] = [item['name'], 'depth', depth_range, '', item['unit'], 'No']
            else:
                value_range = '{:.2f}-{:.2f}'.format(min(item['digitized_data']['value']),max(item['digitized_data']['value']))
                if item['digitized_data']['depth'] is not None:
                    depth_range = '{:.0f}-{:.0f}'.format(min(item['digitized_data']['depth']),max(item['digitized_data']['depth']))
                else:
                    depth_range = 'Please extract depth first'
                islog = 'Yes' if item['islog'] else 'No'
                df_dict[i] = [item['name'], 'curve', depth_range, value_range, item['unit'], islog]
        summary_df = pd.DataFrame.from_dict(df_dict, orient='index', columns = col_names)
        return summary_df

    def update_las(self):
        '''
        export to las format for download
        '''
        depth_range = [1e30, -1e30]
        ind_depth = -1
        deltaz = 0.5
        null_value = -999
        well_name = self.well_name

        curve2unit = dict()
        depth_unit = 'FT'

        sessions = self.saved_results
        #1. get depth range
        for i, s in enumerate(sessions):
            curve2unit[s['name']] = s['unit']
            if s['type'] == 'depth':
                if s['name'] == self.depth_entry_name:
                    ind_depth = i
                depth_range[0] = min(depth_range[0], min(s['data']['x']))
                depth_range[1] = max(depth_range[1], max(s['data']['x']))
                depth_unit = s['unit'].upper()
            else:
                depth_range[0] = min(depth_range[0], int(min(s['digitized_data']['depth'])))
                depth_range[1] = max(depth_range[1], int(max(s['digitized_data']['depth'])))

        nd = np.ceil((depth_range[1]-depth_range[0])/deltaz)
        d = np.linspace(0,nd,int(nd)+1)*deltaz + depth_range[0]

        #2. depth to pix interpolator
        y_pix = np.array(sessions[ind_depth]['data']['y'])
        depth = np.array(sessions[ind_depth]['data']['x'])
        f = interp1d(depth, y_pix, kind = 'linear', fill_value = 'extrapolate')
        depth_pix = f(d)

        #3. construct dataframe. add depth first
        res = pd.DataFrame(d, columns =[sessions[ind_depth]['name']])

        #4. interpolate values of each curve to the final depth range
        for i, s in enumerate(sessions):
            if i==ind_depth:
                continue
            if s['type'] == 'depth':
                tmp_depth = np.array(s['data']['x'])
                tmp_y_pix = np.array(s['data']['y'])
                f = interp1d(tmp_y_pix, tmp_depth,kind='linear',fill_value = 'extrapolate')
                res[s['name']] = np.round(f(depth_pix)*10000)/10000
            else:
                tmp_value = np.array(s['digitized_data']['value'])
                tmp_depth = np.array(s['digitized_data']['depth'])
                f = interp1d(tmp_depth, tmp_value, kind='linear',bounds_error = False, fill_value = null_value)
                res[s['name']] = np.round(f(d)*10000)/10000

        #5. output las
        f = open(self.las_path,'w')
        #write header
        f.write(f'''~Version Information
 VERS.                2.00:   CWLS log ASCII Standard -VERSION 2.00
 WRAP.                  NO:   One Line per depth step
 ~Well Information Block
 #MNEM.UNIT              Data                Description
 #--------- -------------------------------  -------------------------------
 STRT.{depth_unit:<5s}                    {min(d):12.4f}      :Starting Depth
 STOP.{depth_unit:<5s}                    {max(d):12.4f}      :Ending Depth
 STEP.{depth_unit:<5s}                    {deltaz:12.4f}      :Level Spacing
 NULL.                         {null_value:12.4f}      :Absent Value
 WELL  .               {well_name:>20s}      :Well
 ~Curve Information Block
 #MNEM.UNIT           API Codes    Curve Description
 #---------        -------------   -------------------------------\n''')
        #write curve name and unit
        for name in res:
            u = curve2unit[name]
            f.write(f' {name.upper():<7s}.{u:<5s}                                   :{name.upper()}\n')
        f.write('''~Parameter Information Block
 #MNEM.UNIT              Value             Description
 #---------    -------------------------   -------------------------------
 #  Curve Dat
 ~A\n''')
        f.write(res.to_csv(sep='\t', index=False, header=True))
        f.close()

        return
