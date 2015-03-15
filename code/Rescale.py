import numpy as np
import itertools
import pandas as pd

def get_all_drivers():
    return np.loadtxt('../data/drivers.txt', dtype=np.uint)


if __name__ == '__main__':
	all_drivers = get_all_drivers()
	ind = [str(driver)+'_'+str(trip) for driver, trip in itertools.product(all_drivers, np.arange(1,201))]
	original_df = pd.read_csv('../data/subshifthead.csv', header=0, index_col=0)

	df = pd.DataFrame(index=ind)
	for n, driver in enumerate(all_drivers):
		#print('Driver no. %5u (%5u/%5u)' % (driver, n, len(all_drivers)))
		# Load matrix
		m = np.loadtxt('../data/mats2/'+str(driver)+'_similarityMatrixNew.csv', dtype=np.float, delimiter=',')

		# Create the index for the trips
		ind = []
		for i in np.arange(1,201):
			ind.append(str(driver)+'_'+str(i))

		# compute probabilities
		p = original_probs = original_df.ix[ind, 'prob'].values
		repeated = np.sum(m, 1)[1:]; # array of repetitions
		p = 1 - (1-p)**(1+repeated/5);



		# Add the new probas
		df.ix[ind,'prob'] = p

	df.to_csv('../data/subshifthead5.csv', index_label='driver_trip')
