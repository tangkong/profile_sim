from ophyd.sim import SynAxis, SynSignal

__all__ = ['filter1', 'filter2', 'filter3', 'filter4']

filter1 = SynAxis(name='filter1', value=1)
filter2 = SynAxis(name='filter2', value=1)
filter3 = SynAxis(name='filter3', value=1)
filter4 = SynAxis(name='filter4', value=1)


shutter = SynAxis(name='FastShutter')
I1 = SynAxis(name='I1', value=1)
I0 = SynAxis(name='I0', value=1)

table_busy = SynSignal(name='table_busy')
table_trigger = SynSignal(name='table_trigger')
