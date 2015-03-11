// Trajectory.cpp : implementation file
//

#include "Trajectory.h"

#include <iomanip>


// CTrajectory

CTrajectory::CTrajectory()
{
	m_trajectoryId = -1;
	m_nDimensions = 2;
	m_nPoints = 0;
	m_nPartitionPoints = 0;
}

CTrajectory::CTrajectory(int id, int nDimensions)
{
	m_trajectoryId = id;
	m_nDimensions = nDimensions;
	m_nPoints = 0;
	m_nPartitionPoints = 0;
}

CTrajectory::~CTrajectory()
{
	m_nPoints = 0;
}

// CCluster member functions

bool CTrajectory::WritePartitionPts(ofstream& outFile)
{
	outFile << (int) m_trajectoryId << ' ' << (int)m_nPartitionPoints << ' ';

	for (int i = 0; i < (int)m_partitionPointArray.size(); i++)
	{
		outFile << fixed << setprecision(1);
		outFile << m_partitionPointArray[i].GetCoordinate(0) << ' ' << m_partitionPointArray[i].GetCoordinate(1) << ' ';
	}

	outFile << endl;

	return true;
}


// CTrajectory member functions
