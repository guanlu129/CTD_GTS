Processing near-real time ship based near real time CTD data for GTS submission
Objective: convert near-real time  CTD data in to TESAC format

SeaSoft processing steps:

1. Data conversion – convert raw data .hex to CNV files using SeaSoft Data Conversion routine.
2. Wildedit – get rid of single point spikes using SeaSoft Wildedit.
3. Align CTD  - align oxygen data in time, relative to pressure using SeaSoft Align CTD.
4. Cell thermal mass – perform conductivity thermal mass correction using SeaSoft Cell Thermal Mass.
5. Derive – use pressure, temperature and conductivity to compute oceanographic parameters such as density using SeaSoft Derive.


Python processing Steps:
6.  run GTS.py – convert SeaSoft processed CNV files to TEASAC format. 
7.  run Combine.py - combine the output files into one .DTA file 
