import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
import sys
sys.path.append('util')
from plotsUtil import *
from myProgressBar import printProgressBar
from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel as C
import warnings
import os

def partitionData(nData,nBatch):
    # ~~~~ Partition the data across batches
    # Simple parallelization across snapshots
    NDataGlob = nData
    tmp1=0
    tmp2=0
    nData_b = np.zeros(nBatch,dtype=int)
    startData_b = np.zeros(nBatch,dtype=int)
    for ibatch in range(nBatch):
        tmp2 = tmp2 + tmp1
        tmp1 = int(NDataGlob/(nBatch-ibatch))
        nData_b[ibatch] = tmp1
        startData_b[ibatch] = tmp2
        NDataGlob = NDataGlob - tmp1
    return nData_b, startData_b


def getPrediction(gpr,data):
    result = np.zeros(data.shape[0])
    # Batch 
    nPoints = data.shape[0]
    ApproxBatchSize = 10000
    nBatch = max(int(round(nPoints/ApproxBatchSize)),1)
    nData_b, startData_b = partitionData(nPoints,nBatch)
    printProgressBar(0, nBatch, prefix = 'Get prob ' + str(0) + ' / ' +str(nBatch),suffix = 'Complete', length = 50)
    for ibatch in range(nBatch):
        start_ = startData_b[ibatch]
        end_ = startData_b[ibatch] + nData_b[ibatch]
        result[start_:end_] = gpr.predict(data[start_:end_])
        printProgressBar(ibatch+1, nBatch, prefix = 'Get prob ' + str(ibatch+1) + ' / ' +str(nBatch),suffix = 'Complete', length = 50)

    return result

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore" # Also affect subprocesses

nPoints = [1000]
downsSamplingModes = ['random','kmeans','phase']

# Load full data
try:
    combustion_data = np.load('../data/fullData.npy')[:,:2].astype('float32')
    srcProg = np.load('../data/fullData.npy')[:,11].astype('float32')
except FileNotFoundError:
    print('File ../data/fullData.npy is needed and available upon request to malik!hassanaly!at!nrel!gov')
    sys.exit()

# Rescale data
print('RESCALE DATA')
nDim = combustion_data.shape[1]
minVal = np.zeros(nDim)
maxVal = np.zeros(nDim)
freq = np.zeros(nDim)
for i in range(nDim):
    minVal[i] = np.amin(combustion_data[:,i])
    maxVal[i] = np.amax(combustion_data[:,i])
    if i==0:
        freq[i] = (maxVal[i]- minVal[i])/2.5 
    if i==1:
        freq[i] = (maxVal[i]- minVal[i])/1.5




for irep in range(5):
    for nPoint in nPoints:
        print('\tnPoint = ',nPoint)
        for mode in downsSamplingModes:
            if mode=='random':
                indices = np.load('../data/downSampledDataRandom_'+str(nPoint)+'_'+str(irep+1)+'.npz')['indices']
            if mode=='kmeans':
                indices = np.load('../data/downSampledDataKmeans40_'+str(nPoint)+'_'+str(irep+1)+'.npz')['indices']
            if mode=='phase':
                indices = np.load('../data/downSampledData_'+str(nPoint)+'_iter1_'+str(irep+1)+'.npz')['indices']
    
            combustion_data_downSampled = combustion_data[indices]
            
            # TRAIN GP
            X = combustion_data_downSampled[:,:2]
            # Rescale X
            X = (X - minVal[:2])/(maxVal[:2] - minVal[:2])
            Y = np.squeeze(srcProg[indices]).astype('float32')
            kernel = C(1.0, (1e-3, 1e3)) * RBF([0.1,0.1],length_scale_bounds=(1e-3, 1))  + WhiteKernel(noise_level=0.01, noise_level_bounds=(1e-9, 1e5))
            gpr = GaussianProcessRegressor(kernel=kernel,n_restarts_optimizer=10,random_state=42).fit(X,Y)
            print(gpr.kernel_.get_params())
            print('trained')

            # TEST GP
            X_all = combustion_data[:,:2]
            # Rescale X
            X_all = (X_all - minVal[:2])/(maxVal[:2] - minVal[:2])
            Y_all = srcProg[:].astype('float32')
            Y_pred = getPrediction(gpr,X_all)

            # Compute Error
            Error = abs(Y_pred-Y_all)
    
            # Log
            print('\t\t'+mode + ' max = %.4f , mean = %.4f , std = %.4f ' % (np.amax(Error) , np.mean(Error), np.std(Error)  )) 

            f = open('Max_'+mode+'_n'+str(nPoint), "a+")  # append mode 
            f.write(str(np.amax(Error)) + "\n"   )
            f.close()
            f = open('Mean_'+mode+'_n'+str(nPoint), "a+")  # append mode 
            f.write(str(np.mean(Error)) + "\n"   )
            f.close()
            f = open('Std_'+mode+'_n'+str(nPoint), "a+")  # append mode 
            f.write(str(np.std(Error)) + "\n"   )
            f.close()

