#include <stdio.h>
#include <iostream>
#include <stdlib.h>

#include "TraClusterDoc.h"

int main(int argc, char** argv)
{
	if (argc < 5)
	{
		cout << "USAGE: traclus <driver directory> <output file> [<eps> <minLns>]" << endl;
		cout << "       - <driver directory>: a directory with all the driver's trips" << endl;
		cout << "       - <output file>: a cluster file" << endl;
		cout << "       - <eps>: the parameter epsilon (float)" << endl;
		cout << "       - <MinLns>: the parameter MinLnsi (integer)" << endl;
		return 0;
	}

	CTraClusterDoc* document = new CTraClusterDoc;
	
	if (!document->OnOpenDocument(argv[1]))
	{
		return EXIT_FAILURE;
	}

	if (!document->OnClusterGenerate(argv[2], (float) atof(argv[3]), atoi(argv[4])))
	{
		cout << "Cannot generate a cluster file" << endl;
		return EXIT_FAILURE;
	}

	cout << "Clustering has been completed sucessfully" << endl;

	return EXIT_SUCCESS;
}
