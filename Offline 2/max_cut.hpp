#pragma once

#include <bits/stdc++.h>
using namespace std;

class MaxCut
{
public:
    int vertices, edges;
    vector<vector<int>> graph;
    int maxIter;
    double alpha;
    int localSearchIterations;
    // vector<int> solution;

    MaxCut(int vertices, int edges, vector<vector<int>> graph, int maxIter = 1000, double alpha = 0.5)
    {
        this->vertices = vertices;
        this->edges = edges;
        this->graph = graph;
        this->maxIter = maxIter;
        this->alpha = alpha;
        this->localSearchIterations = 0;
        // this->solution.resize(vertices);
    }

    vector<int> randomSolution()
    {
        vector<int> sol(vertices);
        for (int i = 0; i < vertices; i++)
        {
            sol[i] = rand() % 2;
        }
        return sol;
    }

    vector <int> randomSolution2(){
        vector<int> sol(vertices);
        for (int i = 0; i < vertices; i++)
        {
            float prob = static_cast<float>(rand()) / RAND_MAX;
            if (prob >= 0.5)
            {
                sol[i] = 0; // Assign to set X
            }
            else
            {
                sol[i] = 1; // Assign to set Y
            }
        }
        return sol;
    }

    int calculateCutValue(vector<int> &sol)
    {
        int cutValue = 0;
        for (int i = 0; i < vertices; i++)
        {
            // Iterate through all other distinct vertices j
            for (int j = i + 1; j < vertices; j++)
            {
                // Check if an edge exists (graph[i][j] > 0)
                // and if vertices i and j are in different sets
                if (graph[i][j] != 0 && sol[i] != sol[j])
                {
                    cutValue += graph[i][j]; // Add the weight of the edge to the cut
                }
            }
        }
        return cutValue; // No division by 2 needed if iterating j from i + 1
    }

    int randomizedMaxCut()
    {
        int totalCutValue = 0;
        for (int i = 0; i < maxIter; i++)
        {
            vector<int> sol = randomSolution();
            int cutValue = calculateCutValue(sol);
            totalCutValue += cutValue;
        }
        return totalCutValue / this->maxIter; // Average cut value
    }

    pair<int, int> findMaxWt()
    {
        int maxWt = INT_MIN;
        pair<int, int> maxEdge;
        int n = this->vertices;
        for (int i = 0; i < n; i++)
        {
            for (int j = i + 1; j < n; j++)
            {
                if (maxWt < graph[i][j])
                {
                    maxWt = graph[i][j];
                    maxEdge = {i, j};
                }
            }
        }
        return maxEdge;
    }

    int calculateGreedyValue(int z, unordered_set<int> &other)
    {
        int wt = 0;
        for (int y : other)
        {
            wt += graph[z][y];
        }
        return wt;
    }

    vector<int> GreedySolution()
    {
        vector<int> sol(vertices);
        pair<int, int> maxEdge = findMaxWt();
        int u = maxEdge.first, v = maxEdge.second;
        sol[u] = 0;
        sol[v] = 1;
        unordered_set<int> X, Y;
        X.insert(u);
        Y.insert(v);
        for (int i = 0; i < vertices; i++)
        {
            int wtX = 0, wtY = 0;

            if (i != u || i != v)
            {
                // Assuming i in X
                wtX = calculateGreedyValue(i, Y);
                // Assuming i in Y
                wtY = calculateGreedyValue(i, X);
            }

            if (wtX > wtY)
            { // Put in X
                sol[i] = 0;
                X.insert(i);
            }
            else if (wtY > wtX)
            { // Put in Y
                sol[i] = 1;
                Y.insert(i);
            }
            else
            { // Randomly assign
                if (rand() % 2 == 0)
                {
                    sol[i] = 0; // Put in X
                    X.insert(i);
                }
                else
                {
                    sol[i] = 1; // Put in Y
                    Y.insert(i);
                }
            }
        }
        return sol;
    }

    vector<int> SemiGreedySolution(double alpha)
    {
        vector<int> sol(vertices);
        unordered_set<int> X, Y;
        unordered_set<int> unassigned;
        for (int i = 0; i < vertices; i++)
        {
            unassigned.insert(i);
        }
        while (!unassigned.empty())
        {
            int minSigmaX = INT_MAX;
            int minSigmaY = INT_MAX;
            int maxSigmaX = INT_MIN;
            int maxSigmaY = INT_MIN;
            int w_min = INT_MAX;
            int w_max = INT_MIN;
            unordered_map<int, int> SigmaX;
            unordered_map<int, int> SigmaY;

            for (auto it = unassigned.begin(); it != unassigned.end();)
            {
                int v = *it;
                int sigmaX = calculateGreedyValue(v, X);
                SigmaX[v] = sigmaX;
                int sigmaY = calculateGreedyValue(v, Y);
                SigmaY[v] = sigmaY;
                int greedyFuncValue = max(sigmaX, sigmaY);
                minSigmaX = min(minSigmaX, sigmaX);
                minSigmaY = min(minSigmaY, sigmaY);
                maxSigmaX = max(maxSigmaX, sigmaX);
                maxSigmaY = max(maxSigmaY, sigmaY);
                it++;
            }

            w_min = min(minSigmaX, minSigmaY);
            w_max = max(maxSigmaX, maxSigmaY);
            int cutoff = w_min + alpha * (w_max - w_min);

            vector<int> RCL;
            for (auto it = unassigned.begin(); it != unassigned.end();)
            {
                int v = *it;
                int sigmaX = SigmaX[v];
                int sigmaY = SigmaY[v];
                int greedyFuncValue = max(sigmaX, sigmaY);
                if (greedyFuncValue >= cutoff)
                {
                    RCL.push_back(v);
                }
                it++;
            }

            int selectedVertex;

            if (RCL.empty())
            {
                selectedVertex = *unassigned.begin();
            }
            else
            {
                selectedVertex = RCL[rand() % RCL.size()];
            }
            int sigmaX = SigmaX[selectedVertex];
            int sigmaY = SigmaY[selectedVertex];
            if (sigmaX < sigmaY)
            {
                sol[selectedVertex] = 0;
                X.insert(selectedVertex);
            }
            else if (sigmaY < sigmaX)
            {
                sol[selectedVertex] = 1;
                Y.insert(selectedVertex);
            }
            else
            { // Randomly assign
                if (rand() % 2 == 0)
                {
                    sol[selectedVertex] = 0;
                    X.insert(selectedVertex);
                }
                else
                {
                    sol[selectedVertex] = 1;
                    Y.insert(selectedVertex);
                }
            }
            unassigned.erase(selectedVertex);
        }
        return sol;
    }

    int calculateDelta(int v, unordered_set<int> &S, unordered_set<int> &S_bar, vector<int> &sol)
    {
        int delta = 0;
        int sigmaS = calculateGreedyValue(v, S);
        int sigmaS_bar = calculateGreedyValue(v, S_bar);
        if (sol[v] == 0)
        {
            delta = sigmaS - sigmaS_bar;
        }
        else
        {
            delta = sigmaS_bar - sigmaS;
        }
        return delta;
    }

    vector<int> LocalSearch(vector<int> &sol)
    {
        int count = 0;
        unordered_set<int> X, Y;
        for (int i = 0; i < vertices; i++)
        {
            if (sol[i] == 0)
            {
                X.insert(i);
            }
            else
            {
                Y.insert(i);
            }
        }
        bool improved = true;
        while (improved)
        {
            improved = false;
            count++;
            for (int i = 0; i < vertices; i++)
            {
                int delta = calculateDelta(i, X, Y, sol);
                if (delta > 0)
                {
                    improved = true;
                    if (sol[i] == 0)
                    {
                        sol[i] = 1;
                        X.erase(i);
                        Y.insert(i);
                    }
                    else
                    {
                        sol[i] = 0;
                        Y.erase(i);
                        X.insert(i);
                    }
                }
            }
        }
        this->localSearchIterations += count;
        return sol;
    }

    vector<int> GRASP(int iteration)
    {
        vector<int> bestSol = randomSolution();
        int bestCutValue = calculateCutValue(bestSol);
        for (int i = 0; i < iteration; i++)
        {
            vector<int> sol = SemiGreedySolution(this->alpha);
            sol = LocalSearch(sol);
            int cutValue = calculateCutValue(sol);
            if (cutValue > bestCutValue)
            {
                bestCutValue = cutValue;
                bestSol = sol;
            }
        }
        return bestSol;
    }
};