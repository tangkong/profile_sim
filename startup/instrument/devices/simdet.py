from ophyd.sim import det

all = ['ptDet', 'pilDet', 'xsp3']

ptDet = det

# set up filestore simulated detectors

import os
import numpy as np
from pathlib import Path
import uuid

from ophyd.sim import SynSignal
from ophyd.areadetector.filestore_mixins import resource_factory

import tifffile
import h5py 

# Basic signals for simulated area detectors
class SynTiffFilestore(SynSignal):
    def trigger(self):
        # not running at the moment.... but super.trigger() is.  
        tmpRoot = Path(self.fstore_path)
        tmpPath = 'tmp'
        os.makedirs(tmpRoot / tmpPath, exist_ok=True)
        st = super().trigger() # re-evaluates self._func, puts into value
        # Returns NullType
        ret = super().read()    # Signal.read() exists, not SynSignal.read()
        # But using Signal.read() does not allow uid's to be passed into mem.
        val = ret[self.name]['value']
        
        # AD_TIFF handler generates filename by populating template
        # self.template % (self.path, self.filename, self.point_number)
        self.point_number += 1 
        resource, datum_factory = resource_factory(
                spec='AD_TIFF',
                root=tmpRoot,
                resource_path=tmpRoot / tmpPath,
                resource_kwargs={'template': '%s%s_%d.tiff' , 
                                    'filename': f'{uuid.uuid4()}'},
                path_semantics='windows')
        datum = datum_factory({'point_number': self.point_number})
        
        self._asset_docs_cache.append(('resource', resource))
        self._asset_docs_cache.append(('datum', datum))

        fname = (resource['resource_kwargs']['filename'] 
                    + f'_{self.point_number}.tiff')
        fpath = Path(resource['root']) / resource['resource_path'] / fname
        # for tiff spec
        tifffile.imsave(fpath, val)
        
        # replace 'value' in read dict with some datum id
        ret[self.name]['value'] = datum['datum_id']
        self._last_ret = ret
        return st

class SynHDF5Filestore(SynSignal):
    def trigger(self):
        # not running at the moment.... but super.trigger() is.  
        tmpRoot = Path(self.fstore_path)
        tmpPath = 'tmp'
        os.makedirs(tmpRoot / tmpPath, exist_ok=True)
        st = super().trigger() # re-evaluates self._func, puts into value
        # Returns NullType
        ret = super().read()    # Signal.read() exists, not SynSignal.read()
        # But using Signal.read() does not allow uid's to be passed into mem.
        val = ret[self.name]['value']

        self.point_number += 1 
        fn = f'{uuid.uuid4()}.h5'
        resource, datum_factory = resource_factory(
                spec='XSP3',
                root=tmpRoot,
                resource_path=tmpRoot / tmpPath / fn,
                resource_kwargs={}, # Handler takes only one 'filename' argument, which is pulled from the... 
                path_semantics='windows')
        datum = datum_factory({})
        print(resource)     
        self._asset_docs_cache.append(('resource', resource))
        self._asset_docs_cache.append(('datum', datum))

        fpath = Path(resource['root']) / resource['resource_path']
        # for h5 spec
        with h5py.File(fpath, 'w') as f:
            e = f.create_group('/entry/instrument/detector')
            dset = e.create_dataset('data', data=val)
        
        # replace 'value' in read dict with some datum id
        ret[self.name]['value'] = datum['datum_id']
        self._last_ret = ret
        return st

class ArraySynSignal(SynSignal):
    """
    Base class for synthetic array signals. 
    Same interface as a normal ArraySignal, but with simulated data and 
    filestore
    """
    _asset_docs_cache = []
    _last_ret = None
    point_number = 0

    def __init__(self, fstore_path=None, *args, **kwargs):
        self.fstore_path = fstore_path
        super(ArraySynSignal, self).__init__(*args, **kwargs)
    
    def describe(self):
        ret = super().describe()
        ret[self.name]['external'] = 'FILESTORE:'
        return ret
    
    def read(self):
        '''Put the status of the signal into a simple dictionary format
        for data acquisition

        Returns
        -------
            dict
        '''
        # Appears to break things, throw resource sentinel issue... 
        # need to initialize sentinel when starting RunEngine
        # Is ostensibly the same as Signal.read()?...
        if self._last_ret is not None:
            return self._last_ret
            # return {self.name: {'value': self._last_ret,
            #                     'timestamp': self.timestamp}}
        else: # If detector has not been triggered already
            raise Exception('read before being triggered')
            # return {self.name: {'value': self.get(),
            #                      'timestamp': self.timestamp}}

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item

from .images import make_random_peaks, generate_image

# Create simulated image for dexela detector
def p1M_func():
    """imfunc is a function that produces a simulated dexela image
    """
    x = np.linspace(1, 6, num=301)
    intensity = make_random_peaks(x, peak_chance=0.05)*100
    image = generate_image(x, intensity, (512, 512))
    return image

def xsp3_func():
    '''
    Return a simulated MCA array
    '''
    x = np.linspace(1, 2000, num=2000)
    intensity = make_random_peaks(x)
    return intensity

class SynMar(ArraySynSignal, SynTiffFilestore):
    pass

class SynXsp3(ArraySynSignal, SynHDF5Filestore):
    pass

fpath = Path(os.getcwd()) / 'fstore'
print(f'Filestore path: {fpath}')
pilDet = SynMar(name='pilatus1M_image', fstore_path=fpath, func=p1M_func)
xsp3 = SynXsp3(name='Xspress3EXAMPLE', fstore_path=fpath, func=xsp3_func)
