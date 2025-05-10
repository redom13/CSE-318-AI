#include <bits/stdc++.h>
using namespace std;
#include "max_cut.hpp"

unordered_map<string, int> known_bests{
    {"G1", 12078}, {"G2", 12084}, {"G3", 12077}, {"G11", 627}, {"G12", 621}, {"G13", 645}, {"G14", 3187}, {"G15", 3169}, {"G16", 3172}, {"G22", 14123}, {"G23", 14129}, {"G24", 14131}, {"G32", 1560}, {"G33", 1537}, {"G34", 1541}, {"G35", 8000}, {"G36", 7996}, {"G37", 8009}, {"G43", 7027}, {"G44", 7022}, {"G45", 7020}, {"G48", 6000}, {"G49", 6000}, {"G50", 5988}};

void makeCSV(ofstream &csv, const string &filename, int graph_id, MaxCut &max_cut, int vertices, int edges, double alpha, int iterations)
{
    // Run RandomizedCut
    int avgCutWeight = max_cut.randomizedMaxCut();

    vector<int> greedySol = max_cut.GreedySolution();
    int greedyCutVal = max_cut.calculateCutValue(greedySol);

    vector<int> semiGreedySol = max_cut.SemiGreedySolution(alpha);
    int semiGreedyCutVal = max_cut.calculateCutValue(semiGreedySol);

    vector<int> localSearchSol = max_cut.LocalSearch(semiGreedySol);
    int localSearchCutVal = max_cut.calculateCutValue(localSearchSol);
    int localSearchIterations = max_cut.localSearchIterations;

    vector<int> graspSol = max_cut.GRASP(iterations);
    int graspCutVal = max_cut.calculateCutValue(graspSol);

    // Write to CSV
    csv << "G" << graph_id << "," << vertices << "," << edges << ","
        << avgCutWeight << "," << greedyCutVal << "," << semiGreedyCutVal << ","
        << localSearchIterations << "," << localSearchCutVal << "," << iterations << "," << graspCutVal << ","
        << known_bests["G" + to_string(graph_id)] << "\n";

    csv.flush();
}

// int main()
// {
//     vector<int> inputs = {6};
//     int n = inputs.size();
//     cout << "Number of inputs: " << n << endl;
//     for (int i = 0; i < n; i++)
//     {
//         string inputFile = "set1/g" + to_string(inputs[i]) + ".rud";
//         cout << "Input file: " << inputFile << endl;
//         ifstream inFile(inputFile);
//         if (!inFile)
//         {
//             cerr << "Error opening file: " << inputFile << endl;
//             return 1;
//         }
//         int vertices, edges;
//         inFile >> vertices >> edges;
//         vector<vector<int>> graph(vertices, vector<int>(vertices, 0));
//         for (int j = 0; j < edges; j++)
//         {
//             int u, v, w;
//             inFile >> u >> v >> w;
//             graph[u - 1][v - 1] = w;
//             graph[v - 1][u - 1] = w;
//         }
//         cout << "Input taken successfully from " << inputFile << endl;
//         inFile.close();
//         int iterations = 10;
//         double alpha = 0.5;
//         MaxCut maxCut(vertices, edges, graph, iterations, alpha);
//         int avgCutValue = maxCut.randomizedMaxCut();
//         cout << "----------------------------------------" << endl;
//         cout << "Cut value for Randomized of " << inputFile << ": " << avgCutValue << endl;
//         cout << "----------------------------------------" << endl;
//         vector<int> greedySol = maxCut.GreedySolution();
//         int greedyCutValue = maxCut.calculateCutValue(greedySol);
//         cout << "Cut value for Greedy of " << inputFile << ": " << greedyCutValue << endl;
//         cout << "----------------------------------------" << endl;
//         vector<int> semiGreedySol = maxCut.SemiGreedySolution(alpha);
//         int semiGreedyCutValue = maxCut.calculateCutValue(semiGreedySol);
//         cout << "Cut value for SemiGreedy of " << inputFile << ": " << semiGreedyCutValue << endl;
//         cout << "----------------------------------------" << endl;
//         vector<int> localSearchSol = maxCut.LocalSearch(semiGreedySol);
//         int localSearchCutValue = maxCut.calculateCutValue(localSearchSol);
//         int localSearchIterations = maxCut.localSearchIterations;
//         cout << "Cut value for LocalSearch of " << inputFile << ": " << localSearchCutValue << endl;
//         cout << "LocalSearch iterations: " << localSearchIterations << endl;
//         cout << "----------------------------------------" << endl;
//         vector<int> graspSol = maxCut.GRASP(iterations);
//         int graspCutValue = maxCut.calculateCutValue(graspSol);
//         cout << "Cut value for GRASP of " << inputFile << ": " << graspCutValue << endl;
//         cout << "----------------------------------------" << endl;
//     }
// }

int main()
{
    ofstream csvFile("results.csv");
    if (!csvFile)
    {
        cerr << "Error creating CSV file.\n";
        return 1;
    }
    csvFile << "Problem,|V|,|E|,Randomized,Greedy,SemiGreedy,LocalSearch_Iter,LocalSearch_Avg,GRASP_Iter,GRASP_Best,KnownBest\n";
    csvFile.flush();

    for (int id = 1; id <= 54; id++)
    {
        string inputFile = "set1/g" + to_string(id) + ".rud";
        ifstream inFile(inputFile);
        if (!inFile)
        {
            cerr << "Error opening file: " << inputFile << endl;
            continue;
        }
        int vertices, edges;
        inFile >> vertices >> edges;
        vector<vector<int>> graph(vertices, vector<int>(vertices, 0));
        for (int j = 0; j < edges; j++)
        {
            int u, v, w;
            inFile >> u >> v >> w;
            graph[u - 1][v - 1] = w;
            graph[v - 1][u - 1] = w;
        }
        cout << "Input taken successfully from " << inputFile << endl;
        inFile.close();
        int iterations = 10;
        double alpha = 0.5;
        MaxCut maxCut(vertices, edges, graph, iterations, alpha);
        makeCSV(csvFile, inputFile, id, maxCut, vertices, edges, alpha, iterations);
        cout << "Results for G" << id << " written to CSV." << endl;
    }
    csvFile.close();
    cout << "CSV file created successfully." << endl;
    return 0;
}