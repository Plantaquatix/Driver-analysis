// TraClusterDoc.cpp : implementation of the CTraClusterDoc class
//
#include "TraClusterDoc.h"
#include "ClusterGen.h"

#include <fstream>
#include <string.h>
#include <stdio.h>
#include <iostream>
#include <sstream> 
using namespace std;

#define BUFFER_SIZE (1 << 20) // 1Mo

// CTraClusterDoc construction/destruction

CTraClusterDoc::CTraClusterDoc()
{
	// TODO: add one-time construction code here
	m_nTrajectories = 0;
	m_nClusters = 0;
	m_clusterRatio = 0.0;
}

CTraClusterDoc::~CTraClusterDoc()
{
	// Antoine's addition (and remove their initialisations to zero)
	for (std::vector<CTrajectory*>::iterator it = m_trajectoryList.begin(); it != m_trajectoryList.end(); ++it)
		delete *it;
	for (std::vector<CCluster*>::iterator it = m_clusterList.begin(); it != m_clusterList.end(); ++it)
		delete *it;
}


// Antoine's code here
bool CTraClusterDoc::OnOpenDocument(char *DriverDirectory) {
	m_nDimensions = 2;
	m_nTrajectories = 200;
	m_maxNPoints = 0; // incremented later on

	// Loop on each trip
	for (int i = 1; i <= m_nTrajectories; ++i) {
		std::string TrajectoryFileName = std::string(DriverDirectory) // directory
			+ '/'
			+ static_cast<std::ostringstream*>(&(std::ostringstream() << i))->str() // trip number
			+ std::string(".csv"); // extension
		std::ifstream TrajectoryFile;
		unsigned int nPoints = 0;
		CTrajectory* pTrajectoryItem = new CTrajectory(i, m_nDimensions);
				
		// Open the file
		TrajectoryFile.exceptions(ifstream::failbit | ifstream::badbit);
		TrajectoryFile.open(TrajectoryFileName);

		// Ignore header
		TrajectoryFile.ignore(numeric_limits<streamsize>::max(), '\n'); // Don't care about the header

		try {
			// Loop over points in the trajectory
			while (!TrajectoryFile.eof()) {
				CMDPoint Point(m_nDimensions);
				float x = 0.f, y = 0.f;

				++nPoints;

				TrajectoryFile >> x;
				TrajectoryFile.ignore(1, ',');
				TrajectoryFile >> y;
				TrajectoryFile.ignore(numeric_limits<streamsize>::max(), '\n');

				Point.SetCoordinate(1, x);
				Point.SetCoordinate(2, y);
				pTrajectoryItem->AddPointToArray(Point);
			}
		} catch (std::ifstream::failure e) {
			e; // avoid warning
			// Does nothing, it is empty lines at the end of the file here.
		}
		// Keep the max numer of points
		if (nPoints > (unsigned) m_maxNPoints)
			m_maxNPoints = (signed) nPoints; // pff. should be unsigned, whatever

		// Add the trajectory to the list
		m_trajectoryList.push_back(pTrajectoryItem);
	}
	return true;
}

bool CTraClusterDoc::OnClusterGenerate(char* clusterFileName, float epsParam, int minLnsParam)
{
	CClusterGen generator(this);

	if (m_nTrajectories == 0)
	{
		fprintf(stderr, "Load a trajectory data set first\n");
		return false;
	}

	// FIRST STEP: Trajectory Partitioning
	if (!generator.PartitionTrajectory())
	{
		fprintf(stderr, "Unable to partition a trajectory\n");
		return false;
	}

#define DEBUG 1
#ifdef DEBUG
	// Write the generated clusters
	// START ...
	ofstream outFile1;
	outFile1.open("./data/parts.txt");
    //outFile << (int)m_clusterList.size() << endl;

	vector<CTrajectory*>::iterator iter1;
	for (iter1 = m_trajectoryList.begin(); iter1 != m_trajectoryList.end(); iter1++)
	{
		CTrajectory* pTrajectory = *iter1;
		pTrajectory->WritePartitionPts(outFile1);
	}

	outFile1.close();
#endif

	// SECOND STEP: Density-based Clustering
	if (!generator.PerformDBSCAN(epsParam, minLnsParam))
	{
		fprintf(stderr, "Unable to perform the DBSCAN algorithm\n");
		return false;
	}

	// THIRD STEP: Cluster Construction
	if (!generator.ConstructCluster())
	{
		fprintf(stderr, "Unable to construct a cluster\n");
		return false;
	}

	// Write the generated clusters
	// START ...
	ofstream outFile;
	outFile.open(clusterFileName);
	outFile << (int)m_clusterList.size() << endl;

	vector<CCluster*>::iterator iter;
	for (iter = m_clusterList.begin(); iter != m_clusterList.end(); iter++)
	{
		CCluster* pCluster = *iter;
		pCluster->WriteCluster(outFile);
	}

	outFile.close();
	// ... END

	return true;
}

bool CTraClusterDoc::OnEstimateParameter(float& epsParam, int& minLnsParam)
{
	CClusterGen generator(this);

	if (!generator.PartitionTrajectory())
	{
		fprintf(stderr, "Unable to partition a trajectory\n");
		return false;
	}

	if (!generator.EstimateParameterValue(epsParam, minLnsParam))
	{
		fprintf(stderr, "Unable to calculate the entropy\n");
		return false;
	}

	return true;
}
