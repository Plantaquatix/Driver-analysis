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
	// Antoine (and remove their initialisations to zero)
	for (std::vector<CTrajectory*>::iterator it = m_trajectoryList.begin(); it != m_trajectoryList.end(); ++it)
		delete *it;
	for (std::vector<CCluster*>::iterator it = m_clusterList.begin(); it != m_clusterList.end(); ++it)
		delete *it;
}


// CTraClusterDoc commands

bool CTraClusterDoc::OnOpenDocument(char* inputFileName)
{
	int nDimensions = 2;		// default dimension = 2
	int nTrajectories = 0;
	int nTotalPoints = 0;
	int trajectoryId;
	int nPoints;
	float value;
	char *buffer = NULL;
	char tmp_buf1[1024], tmp_buf2[1024];
	int offset = 0;

	buffer = new char[BUFFER_SIZE];
	if (buffer == NULL) return false;

	ifstream istr(inputFileName);

	if(!istr)
	{
		fprintf(stderr, "Unable to open input file\n");
		delete buffer;
		return false;
	}

	istr.getline(buffer, BUFFER_SIZE);	// the number of dimensions
	sscanf(buffer, "%d", &nDimensions);
	m_nDimensions = nDimensions;
	istr.getline(buffer, BUFFER_SIZE);	// the number of trajectories
	sscanf(buffer, "%d", &nTrajectories);
	m_nTrajectories = nTrajectories;

	m_maxNPoints = -2147483648; //INT_MIN;					// initialize for comparison

	// the trajectory Id, the number of points, the coordinate of a point ...
	for (int i = 0; i < nTrajectories; i++)
	{
		offset = 0;

		istr.getline(buffer, BUFFER_SIZE);	// each trajectory
		sscanf(buffer, "%d %d", &trajectoryId, &nPoints);
		sscanf(buffer, "%s %s", tmp_buf1, tmp_buf2);
		offset += (int)strlen(tmp_buf1) + (int)strlen(tmp_buf2) + 2;

		if (nPoints > m_maxNPoints) m_maxNPoints = nPoints;
		nTotalPoints += nPoints;

		CTrajectory* pTrajectoryItem = new CTrajectory(trajectoryId, nDimensions); 
		m_trajectoryList.push_back(pTrajectoryItem);

		for (int j = 0; j < nPoints; j++)
		{
			CMDPoint point(nDimensions);	// initialize the CMDPoint class for each point
			
			for (int k = 0; k < nDimensions; k++)
			{
				sscanf(buffer + offset, "%f", &value);
				sscanf(buffer + offset, "%s", tmp_buf1);
				offset += (int)strlen(tmp_buf1) + 1;

				point.SetCoordinate(k, value);
			}

			pTrajectoryItem->AddPointToArray(point);
		}
	}
	delete buffer;
	return true;
}

// Antoine's code here
bool CTraClusterDoc::OnOpenDocument(char *DriverFileName, char *DriverDirectory) {
	
	try {
		// Open the list of drivers
		std::ifstream DriverFile;

		DriverFile.exceptions(ifstream::failbit | ifstream::badbit);
		DriverFile.open(DriverFileName);

		m_nDimensions = 2;
		m_nTrajectories = 200;
		m_maxNPoints = 0; // incremented later on

		// Loop on each driver
		while (!DriverFile.eof()) {
			unsigned int DriverNo;

			DriverFile >> DriverNo;
			// Loop on each trip
			for (int i = 1; i <= 200; ++i) {
				std::string TrajectoryFileName = std::string(DriverDirectory) // directory
					+ static_cast<std::ostringstream*>(&(std::ostringstream() << DriverNo))->str() // driver number
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
		}


	}
	catch (std::ifstream::failure e) {
		std::cout << "Error while processing the file (" << e.what() << ")." << std::endl;
		return false;
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
