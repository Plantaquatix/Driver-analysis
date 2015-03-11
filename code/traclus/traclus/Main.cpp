#include <stdio.h>
#include <iostream>
#include <stdlib.h>

#include "TraClusterDoc.h"

int main(int argc, char** argv)
{
	if (argc < 5)
	{
		cout << "USAGE: traclus <driver file> <driver directory> <output file> [<eps> <minLns>]" << endl;
		cout << "       - <driver file>: a file with the list of drivers" << endl;
		cout << "       - <driver directory>: a directory with all the drivers sub-directories" << endl;
		cout << "       - <output file>: a cluster file" << endl;
		cout << "       - <eps>: the parameter epsilon (float)" << endl;
		cout << "       - <MinLns>: the parameter MinLnsi (integer)" << endl;
		return 0;
	}

	CTraClusterDoc* document = new CTraClusterDoc;
	
	if (!document->OnOpenDocument(argv[1], argv[2]))
	{
		cout << "Cannot open a trajectory file" << endl;
		return 0;
	}

	if (!document->OnClusterGenerate(argv[3], atof(argv[4]), atoi(argv[5])))
	{
		cout << "Cannot generate a cluster file" << endl;
		return 0;
	}

	cout << "Clustering has been completed sucessfully" << endl;

	return EXIT_SUCCESS;
}
